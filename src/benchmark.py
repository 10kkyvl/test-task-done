import asyncio
import random

import aiohttp
import orjson
import uuid
import time
import statistics
import datetime
from collections import Counter

URL = "http://localhost:8000/events"
CONCURRENCY = 1
TARGET_RPS = 1000
TOTAL_REQUESTS = 50000

latencies = []
errors = 0
status_codes = Counter()


async def send_event(session: aiohttp.ClientSession):
    payload = [
        {
            "event_id": str(uuid.uuid4()),
            "occurred_at": datetime.datetime.now(datetime.UTC).isoformat() + "Z",
            "user_id": random.randint(1, 999999999),
            "event_type": "view_item",
            "properties": {"session_id": str(uuid.uuid4()), "country": "UA"},
        }
    ]
    start = time.perf_counter()
    try:
        async with session.post(
            URL,
            data=orjson.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        ) as resp:
            await resp.read()
            latency = time.perf_counter() - start
            status_codes[resp.status] += 1
            if resp.status not in [200, 201, 202]:
                raise Exception(f"status={resp.status}")
            latencies.append(latency)
    except Exception:
        global errors
        errors += 1


async def rate_limited_sender(session):
    interval = 1 / TARGET_RPS
    for _ in range(TOTAL_REQUESTS):
        start = time.perf_counter()
        await send_event(session)
        elapsed = time.perf_counter() - start
        delay = interval - elapsed
        if delay > 0:
            await asyncio.sleep(delay)


async def main():
    async with aiohttp.ClientSession() as session:
        start_time = time.perf_counter()
        tasks = [
            asyncio.create_task(rate_limited_sender(session))
            for _ in range(CONCURRENCY)
        ]
        await asyncio.gather(*tasks)
        duration = time.perf_counter() - start_time

    success = len(latencies)
    if success == 0:
        print("No success requests")
        return

    rps = success / duration
    avg = statistics.mean(latencies)
    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=100)[94]

    print(f"\n--- Load test summary ---")
    print(f"Requests total: {TOTAL_REQUESTS}")
    print(f"Success: {success}")
    print(f"Errors: {errors}")
    print(f"Duration: {duration:.2f}s")
    print(f"RPS achieved: {rps:.2f}")
    print(f"Avg latency: {avg*1000:.2f} ms")
    print(f"P50 latency: {p50*1000:.2f} ms")
    print(f"P95 latency: {p95*1000:.2f} ms")
    print(f"\n--- Response codes ---")
    for code, count in sorted(status_codes.items()):
        pct = (count / TOTAL_REQUESTS) * 100
        print(f"{code}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    asyncio.run(main())
