import json
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.app.services.events_service import EventService


@pytest.mark.asyncio
async def test_event_publish(monkeypatch):
    fake_broker = AsyncMock()
    service = EventService(fake_broker)

    event = {
        "event_id": str(uuid4()),
        "occurred_at": "2025-10-27T12:00:00Z",
        "user_id": 1,
        "event_type": "view_item",
        "properties": {},
    }

    body = json.dumps([event]).encode()
    await service.ingest(body)

    fake_broker.publish.assert_awaited_once()
