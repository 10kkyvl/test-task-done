import datetime
from typing import Annotated, Dict, Any
from uuid import UUID

from msgspec import Struct, Meta


PositiveInt = Annotated[int, Meta(gt=0)]


class EventInput(Struct, frozen=True):
    event_id: UUID
    occurred_at: datetime.datetime
    user_id: PositiveInt
    event_type: Annotated[str, Meta(min_length=1, max_length=64)]
    properties: Dict[str, Any]


class EventResponse(Struct, frozen=True):
    status: str = "Queued"
    ingested: PositiveInt = 0
