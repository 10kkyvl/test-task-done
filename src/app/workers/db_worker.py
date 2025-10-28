import asyncio
import json
import os
from datetime import datetime, timezone
from uuid import UUID
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
import nats
from nats.js.api import StreamConfig, StorageType
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
from cassandra.auth import PlainTextAuthProvider
import clickhouse_connect


SCYLLA_HOST = os.getenv("SCYLLA_HOST", "analytics_scylla")
SCYLLA_PORT = int(os.getenv("SCYLLA_PORT", 9042))
SCYLLA_KEYSPACE = os.getenv("SCYLLA_KEYSPACE", "analytics")
SCYLLA_USER = os.getenv("SCYLLA_USER", "cassandra")
SCYLLA_PASSWORD = os.getenv("SCYLLA_PASSWORD", "cassandra")

NATS_HOST = os.getenv("NATS_HOST", "nats")
NATS_PORT = int(os.getenv("NATS_PORT", 4222))
NATS_USER = os.getenv("NATS_USER", "analytics_nats")
NATS_PASSWORD = os.getenv("NATS_PASSWORD", "super_secure_nats_pass")

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "analytics_clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_HTTP_PORT", 8123))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_KEYSPACE", "analytics")


BATCH_SIZE = 50_000
executor = ThreadPoolExecutor(max_workers=10)


def to_datetime(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str).astimezone(timezone.utc)


def connect_scylla():
    cluster = Cluster(
        [SCYLLA_HOST],
        port=SCYLLA_PORT,
        auth_provider=PlainTextAuthProvider(SCYLLA_USER, SCYLLA_PASSWORD),
    )
    session = cluster.connect(SCYLLA_KEYSPACE)
    logger.info("Connected to Scylla")
    return session


def connect_clickhouse():
    client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        database=CLICKHOUSE_DB,
    )
    logger.info("Connected to ClickHouse")
    return client


async def insert_event(e, session, prepared):
    loop = asyncio.get_event_loop()
    fut = session.execute_async(
        prepared,
        (
            UUID(e["event_id"]),
            to_datetime(e["occurred_at"]),
            e["user_id"],
            e["event_type"],
            json.dumps(e["properties"]),
        ),
    )
    await loop.run_in_executor(executor, fut.result)
    logger.debug(f"Inserted into Scylla: {e['event_id']}")


async def hot_worker():
    logger.info("Starting HOT worker")
    nc = await nats.connect(
        servers=[f"nats://{NATS_USER}:{NATS_PASSWORD}@{NATS_HOST}:{NATS_PORT}"]
    )
    js = nc.jetstream()

    try:
        await js.add_stream(
            StreamConfig(
                name="EVENTS_HOT",
                subjects=["events_hot"],
                storage=StorageType.FILE,
                max_msgs=-1,
                max_bytes=-1,
                max_msg_size=-1,
                max_age=24 * 60 * 60 * 1_000_000_000,
            )
        )
    except Exception:
        pass

    session = connect_scylla()
    prepared = session.prepare(
        "INSERT INTO events (event_id, occurred_at, user_id, event_type, properties) VALUES (?, ?, ?, ?, ?)"
    )

    async def handle(msg):
        try:
            data = json.loads(msg.data.decode())
            if not isinstance(data, list):
                await msg.ack()
                return
            logger.info(f"Processing {len(data)} events from NATS")
            await asyncio.gather(*(insert_event(e, session, prepared) for e in data))
            await msg.ack()
            logger.info(f"ACKED {len(data)} events")
        except Exception as e:
            meta = msg.metadata
            logger.error(
                f"Error processing message (attempt {meta.num_delivered}): {e}"
            )
            if meta.num_delivered >= 3:
                await js.publish("events_hot.dlq", msg.data)
                await msg.ack()
                logger.error(
                    f"Moved message to DLQ after {meta.num_delivered} attempts"
                )
            else:
                await msg.nak()

    sub = await js.pull_subscribe("events_hot", durable="events_hot_consumer")
    logger.info("Subscribed to events_hot")

    while True:
        try:
            msgs = await sub.fetch(1, timeout=10)
            for msg in msgs:
                await handle(msg)
        except asyncio.TimeoutError:
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            await asyncio.sleep(1)


async def cold_worker():
    logger.info("Starting COLD worker")
    session = connect_scylla()
    client = connect_clickhouse()

    select_query = f"""
        SELECT event_id, occurred_at, user_id, event_type, properties
        FROM events LIMIT {BATCH_SIZE}
    """
    delete_query = "DELETE FROM events WHERE event_id = ?"
    prepared_delete = session.prepare(delete_query)

    while True:
        rows = list(session.execute(select_query))
        if not rows:
            await asyncio.sleep(10)
            continue

        batch = [
            (
                str(r.event_id),
                r.occurred_at,
                r.user_id,
                r.event_type,
                json.dumps(r.properties),
            )
            for r in rows
        ]

        client.insert(
            "events",
            batch,
            column_names=[
                "event_id",
                "occurred_at",
                "user_id",
                "event_type",
                "properties",
            ],
        )
        logger.info(f"Synced {len(batch)} events to ClickHouse")

        b = BatchStatement(BatchType.UNLOGGED)
        for r in rows:
            b.add(prepared_delete, (r.event_id,))
        session.execute(b)

        logger.info(f"Deleted {len(batch)} events from ScyllaDB")
        await asyncio.sleep(10)


async def main():
    await asyncio.gather(hot_worker(), cold_worker())


if __name__ == "__main__":
    asyncio.run(main())
