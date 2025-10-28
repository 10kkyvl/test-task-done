from datetime import date
from typing import List

from msgspec import Struct


class DailyActiveUsers(Struct):
    date: date
    users: int


class DAUResponse(Struct):
    results: List[DailyActiveUsers]


class TopEvent(Struct):
    event_type: str
    count: int
