from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from litestar import get
from litestar.response import Response

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["status"]
)

EVENTS_COUNT = Counter(
    "events_processed_total",
    "Total events processed"
)

RPS = Gauge("http_requests_per_second", "Requests per second")


@get("/metrics", sync_to_thread=False)
async def metrics_endpoint() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@get("/health", sync_to_thread=False)
async def health_check() -> dict:
    return {"status": "ok"}


route_handlers = [metrics_endpoint, health_check]
