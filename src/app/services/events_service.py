from typing import List
from msgspec import json, DecodeError, ValidationError
from litestar.exceptions import HTTPException

from src.app.broker.base import Broker
from src.app.schemas.events import EventInput
from src.app.core.logger import logger


class EventService:
    def __init__(self, broker: Broker):
        self._broker = broker

    async def ingest(self, raw_body: bytes) -> int:
        try:
            events: List[EventInput] = json.decode(raw_body, type=List[EventInput])
        except DecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")

        if not events:
            raise HTTPException(status_code=400, detail="Empty event batch")

        for e in events:
            if not e.event_type:
                raise HTTPException(
                    status_code=400, detail="event_type cannot be empty"
                )
            if e.user_id <= 0:
                raise HTTPException(status_code=400, detail="user_id must be positive")

        await self.publish_events(events)
        return len(events)

    async def publish_events(self, events: List[EventInput]) -> None:
        payload = json.encode(events)
        await self._broker.publish("events_hot", payload)
        logger.debug(f"Published {len(events)} events to NATS")
