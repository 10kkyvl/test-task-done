from datetime import date
from typing import List, Dict

from src.app.core import config
from src.app.db.clickhouse import clickhouse


class StatsRepository:
    def __init__(self):
        self._client = clickhouse.client

    async def get_dau(self, start_data: date, end_data: date) -> List[Dict[str, int]]:
        client = await self._client
        query = """
            SELECT 
                toDate(occured_at) AS day,
                uniqExact(user_id) AS dau
            FROM analytics.events
            WHERE occured_at >= %(from)s AND occured_at <= %(to)s
            GROUP BY day
            ORDER BY day ASC
        """
        result = await self._client.query(query, {"from": start_data, "to": end_data})
        return [{"date": r[0].isoformat(), "users": r[1]} for r in result.result_rows]
