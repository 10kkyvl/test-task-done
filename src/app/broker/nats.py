from typing import Any, Optional, List

from nats.aio.client import Client as NATS
from nats.js.api import (
    StreamConfig,
    ConsumerConfig,
    StorageType,
    DeliverPolicy,
    AckPolicy,
)
from nats.js.client import JetStreamContext

from src.app.core.logger import logger
from src.app.core.config import settings


class Nats:
    def __init__(self, url: str = settings.nats.url):
        self.url = url
        self.client = NATS()
        self.js: Optional[JetStreamContext] = None

    async def connect(self):
        await self.client.connect(
            servers=[self.url],
            connect_timeout=10,
            reconnect_time_wait=2,
            max_reconnect_attempts=5,
        )
        self.js = self.client.jetstream()

    async def publish(self, subject: str, message: Any):
        if not self.client.is_connected:
            raise RuntimeError("NATS not connected")
        await self.js.publish(subject, message)

    async def add_streams(self, streams: List[dict]):
        if not self.client.is_connected:
            raise RuntimeError("NATS not connected")

        for s in streams:
            name = s["name"]
            subjects = s["subjects"]
            main_subject = subjects[0]

            dlq_subject = s.get("dlq_subject", f"{main_subject}.dlq")
            storage = (
                StorageType.FILE
                if s.get("storage", "file") == "file"
                else StorageType.MEMORY
            )
            max_deliver = s.get("max_deliver", 3)

            try:
                await self.js.add_stream(
                    StreamConfig(
                        name=name,
                        subjects=subjects,
                        storage=storage,
                    )
                )
                logger.info(f"[NATS] stream {name} created")
            except Exception as e:
                if "subjects overlap with an existing stream" in str(e):
                    logger.info(f"[NATS] stream {name} already exists, skip")
                else:
                    raise

            try:
                await self.js.add_stream(
                    StreamConfig(
                        name=f"{name}_DLQ",
                        subjects=[dlq_subject],
                        storage=storage,
                    )
                )
                logger.info(f"[NATS] dlq stream {name}_DLQ created")
            except Exception as e:
                if "subjects overlap with an existing stream" in str(e):
                    logger.info(f"[NATS] dlq stream {name}_DLQ already exists, skip")
                else:
                    raise

            consumer_cfg = ConsumerConfig(
                durable_name=f"{name}_CONSUMER",
                deliver_policy=DeliverPolicy.ALL,
                ack_policy=AckPolicy.EXPLICIT,
                max_deliver=max_deliver,
                deliver_subject=f"{main_subject}.deliver",
                max_ack_pending=100,
            )

            try:
                await self.js.add_consumer(stream=name, config=consumer_cfg)
                logger.info(f"[NATS] consumer {name}_CONSUMER created")
            except Exception as e:
                logger.info(
                    f"[NATS] consumer {name}_CONSUMER already exists, skip: {e}"
                )

    async def drain(self):
        if self.client.is_connected:
            await self.client.drain()

    async def close(self):
        if self.client.is_connected:
            await self.client.close()

    async def shutdown(self):
        await self.drain()
        await self.close()


nats_client = Nats()
