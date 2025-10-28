import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def fake_repo():
    repo = AsyncMock()
    repo.save_event = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.query_by_user = AsyncMock(return_value=[])
    return repo
