from datetime import date
from typing import List, Dict

from pygments.lexers import r

from src.app.db.clickhouse import clickhouse


class StatsRepository:
    def __init__(self):
        self._client = clickhouse.client

    async def get_dau(self, start_date: date, end_date: date) -> List[Dict[str, int]]:
        query = """
                SELECT toDate(occurred_at) AS day,
                uniqExact(user_id) AS dau
                FROM analytics.events
                WHERE occurred_at >= %(from)s \
                  AND occurred_at <= %(to)s
                GROUP BY day
                ORDER BY day ASC \
                """
        result = await self._client.query(query, {"from": start_date, "to": end_date})

        return [
            {"date": r[0] if isinstance(r[0], date) else r[0].date(), "users": r[1]}
            for r in result.result_rows
        ]

    async def get_top_events(
        self, start_date: date, end_date: date, limit: int = 10
    ) -> List[Dict[str, int]]:
        query = """
            SELECT
                event_type,
                count() AS total
            FROM analytics.events
            WHERE occurred_at >= %(from)s AND occurred_at <= %(to)s
            GROUP BY event_type
            ORDER BY total DESC
            LIMIT %(limit)s
        """
        result = await self._client.query(
            query, {"from": start_date, "to": end_date, "limit": limit}
        )

        return [{"event_type": r[0], "count": r[1]} for r in result.result_rows]

    async def get_retention(self, start_date: date, window: int = 3) -> List[Dict]:
        query = """
                WITH cohort AS (SELECT user_id, \
                                       toDate(min(occurred_at)) AS cohort_date \
                                FROM analytics.events \
                                WHERE toDate(occurred_at) >= toDate(%(start_date)s) \
                                GROUP BY user_id), \

                     cohort_sizes AS (SELECT cohort_date, \
                                             count() AS cohort_size \
                                      FROM cohort \
                                      GROUP BY cohort_date), \

                     days AS (SELECT toUInt32(number) AS day_index \
                              FROM numbers(toUInt32(%(window)s) + 1))

                SELECT c.cohort_date            AS cohort, \
                       d.day_index, \
                       countDistinct(e.user_id) AS active_users, any (cs.cohort_size) AS cohort_size, round(countDistinct(e.user_id) * 1.0 / any (cs.cohort_size), 4) AS retention_rate
                FROM cohort AS c
                    CROSS JOIN days AS d
                    INNER JOIN cohort_sizes AS cs \
                ON cs.cohort_date = c.cohort_date
                    LEFT JOIN analytics.events AS e
                    ON e.user_id = c.user_id
                    AND toDate(e.occurred_at) = date_add(DAY, CAST (d.day_index AS Int32), c.cohort_date)
                GROUP BY c.cohort_date, d.day_index
                ORDER BY cohort ASC, day_index ASC \
                """

        result = await self._client.query(
            query, {"start_date": start_date, "window": window}
        )

        return [
            {
                "cohort": r[0].isoformat(),
                "day_index": r[1],
                "active_users": r[2],
                "cohort_size": r[3],
                "retention_rate": float(r[4]),
            }
            for r in result.result_rows
        ]
