import pytest
import os
import time

import clickhouse_connect
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from src.app.main import app


SCYLLA_HOST = "localhost"
SCYLLA_PORT = int(os.getenv("SCYLLA_PORT", 9042))
SCYLLA_KEYSPACE = os.getenv("SCYLLA_KEYSPACE", "analytics")
SCYLLA_USER = os.getenv("SCYLLA_USER", "cassandra")
SCYLLA_PASSWORD = os.getenv("SCYLLA_PASSWORD", "cassandra")

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_HTTP_PORT", 8123))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_KEYSPACE", "analytics")


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def mock_nats(monkeypatch):
    fake_publish = AsyncMock()
    monkeypatch.setattr("src.app.broker.nats.Nats.publish", fake_publish)


@pytest.fixture(scope="function", autouse=True)
def cleanup_db():
    print("\n[TEST FIXTURE] Cleanup DB started")
    session = None
    cluster = None

    for attempt in range(5):
        try:
            print(
                f"[Scylla] Attempt {attempt+1}: connecting to {SCYLLA_HOST}:{SCYLLA_PORT}"
            )
            auth_provider = PlainTextAuthProvider(SCYLLA_USER, SCYLLA_PASSWORD)
            cluster = Cluster(
                [SCYLLA_HOST],
                port=SCYLLA_PORT,
                auth_provider=auth_provider,
                protocol_version=4,
                connect_timeout=5,
            )
            session = cluster.connect(SCYLLA_KEYSPACE)
            print("[Scylla] Connected successfully.")
            break
        except Exception as e:
            print(f"[Scylla] Connection failed: {e}")
            time.sleep(2)
    else:
        print("[Scylla] Giving up. Proceeding without Scylla connection.")

    ch = None
    try:
        print(f"[ClickHouse] Connecting to {CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}")
        ch = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            database=CLICKHOUSE_DB,
            connect_timeout=5,
        )
        print("[ClickHouse] Connected successfully.")
    except Exception as e:
        print(f"[ClickHouse] Connection failed: {e}")

    try:
        if session:
            print("[Scylla] Truncating table events...")
            session.execute("TRUNCATE TABLE events;")
        if ch:
            print("[ClickHouse] Truncating table events...")
            ch.command(f"TRUNCATE TABLE {CLICKHOUSE_DB}.events")
        print("[Cleanup] Done before test.")
    except Exception as e:
        print(f"[WARN] Cleanup before test failed: {e}")

    yield

    try:
        if session:
            print("[Scylla] Truncating table events (post-test)...")
            session.execute("TRUNCATE TABLE events;")
        if ch:
            print("[ClickHouse] Truncating table events (post-test)...")
            ch.command(f"TRUNCATE TABLE {CLICKHOUSE_DB}.events")
        print("[Cleanup] Done after test.")
    except Exception as e:
        print(f"[WARN] Cleanup after test failed: {e}")
    finally:
        if session:
            print("[Scylla] Closing session...")
            session.shutdown()
        if cluster:
            cluster.shutdown()
        if ch:
            ch.close()
        print("[TEST FIXTURE] Cleanup complete\n")
