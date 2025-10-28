import os
import pytest
from httpx import AsyncClient

LITESTAR_HOST = os.getenv("LITESTAR_HOST", "localhost")
LITESTAR_PORT = os.getenv("LITESTAR_PORT", "8000")


@pytest.mark.asyncio
async def test_ingest_to_stats_e2e():
    base_url = f"http://{LITESTAR_HOST}:{LITESTAR_PORT}"

    async with AsyncClient(base_url=base_url) as client:
        event = [
            {
                "event_id": "a0f1bde6-6f1c-4cc2-a5aa-0568b6cba7b9",
                "occurred_at": "2025-10-28T00:00:00Z",
                "user_id": 1,
                "event_type": "view_item",
                "properties": {"country": "UA"},
            }
        ]

        r = await client.post("/events", json=event)
        assert r.status_code == 201

        import asyncio

        await asyncio.sleep(20)

        params = {"from": "2025-10-28", "to": "2025-10-28"}
        resp = await client.get("/stats/dau", params=params)
        assert resp.status_code == 200

        data = resp.json()
        print(f"DAU response: {data}")

        results = data.get("results", [])
        assert len(results) > 0
        assert results[0]["users"] >= 1
