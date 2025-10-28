from typing import List

from msgspec import json

from src.app.broker.nats import Nats
from src.app.schemas.events import EventInput


class EventService:
    def __init__(self, broker: Nats):
        self.broker = broker

    async def publish_events(self, events: List[EventInput]):
        batch = json.encode([e.__dict__ for e in events])
        await self.broker.publish("events", batch)
