import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_event_indexing(fake_repo):
    events = [
        {
            "event_id": uuid4(),
            "occurred_at": "2025-10-27T12:00:00Z",
            "user_id": 42,
            "event_type": "view_item",
            "properties": {},
        },
        {
            "event_id": uuid4(),
            "occurred_at": "2025-10-27T13:00:00Z",
            "user_id": 42,
            "event_type": "purchase",
            "properties": {},
        },
    ]

    fake_repo.query_by_user.return_value = events
    result = await fake_repo.query_by_user(42)
    assert len(result) == 2
