from datetime import date
from typing import List, Dict
from src.app.db.repositories.stats_repo import StatsRepository
from src.app.schemas.stats import DailyActiveUsers, TopEvent


class StatsService:
    def __init__(self, repo: StatsRepository):
        self._repo = repo

    async def get_dau(self, from_: date, to_: date) -> List[DailyActiveUsers]:
        rows = await self._repo.get_dau(from_, to_)
        return [DailyActiveUsers(**r) for r in rows]

    async def get_top_events(
        self, from_: date, to_: date, limit: int = 10
    ) -> List[TopEvent]:
        rows = await self._repo.get_top_events(from_, to_, limit)
        return [TopEvent(**r) for r in rows]

    async def get_retention(self, from_: date, window: int = 3) -> List[Dict]:
        rows = await self._repo.get_retention(from_, window)
        return rows
