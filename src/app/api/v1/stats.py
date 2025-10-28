from datetime import date
from typing import Annotated, List, Dict

from litestar import get
from litestar.di import Provide
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.params import Parameter
from msgspec import Meta

from src.app.core.providers import provide_stats_repo, provide_stats_service
from src.app.schemas.stats import DAUResponse, TopEvent
from src.app.services.stats_service import StatsService


stats_rate_limit = RateLimitConfig(rate_limit=("second", 1))


@get(
    "/stats/dau",
    dependencies={
        "repo": Provide(provide_stats_repo),
        "service": Provide(provide_stats_service),
    },
    middleware=[stats_rate_limit.middleware],
)
async def get_dau(
    service: StatsService,
    from_: Annotated[date, Parameter(query="from")],
    to: date,
) -> DAUResponse:
    data = await service.get_dau(from_, to)
    return DAUResponse(data)


@get(
    "/stats/top-events",
    dependencies={
        "repo": Provide(provide_stats_repo),
        "service": Provide(provide_stats_service),
    },
    middleware=[stats_rate_limit.middleware],
)
async def get_top_events(
    service: StatsService,
    from_: Annotated[date, Parameter(query="from")],
    to: date,
    limit: Annotated[int, Meta(gt=0)] = 10,
) -> List[TopEvent]:
    return await service.get_top_events(from_, to, limit)


@get(
    "/stats/retention",
    dependencies={
        "repo": Provide(provide_stats_repo),
        "service": Provide(provide_stats_service),
    },
    middleware=[stats_rate_limit.middleware],
)
async def get_retention(
    service: StatsService,
    from_: Annotated[date, Parameter(query="start_date")],
    window: Annotated[int, Meta(gt=0)] = 3,
) -> List[Dict]:
    return await service.get_retention(from_, window)


route_handlers = [get_dau, get_top_events, get_retention]
