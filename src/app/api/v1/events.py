from litestar import post, Request
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.middleware.rate_limit import RateLimitConfig

from src.app.core.logger import logger
from src.app.schemas.events import EventResponse
from src.app.core.providers import provide_event_service
from src.app.services.events_service import EventService


ingest_rate_limit = RateLimitConfig(rate_limit=("second", 5))


@post(
    "/events",
    dependencies={"event_service": Provide(provide_event_service)},
    # middleware=[ingest_rate_limit.middleware],
)
async def ingest_events(request: Request, event_service: EventService) -> EventResponse:
    try:
        body_bytes = await request.body()
        events_len = await event_service.ingest(body_bytes)
        return EventResponse(status="ok", ingested=events_len)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to ingest events\n", e)
        raise HTTPException(status_code=503, detail="Failed to ingest events")


route_handlers = [ingest_events]
