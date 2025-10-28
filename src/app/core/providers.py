from src.app.db.repositories.stats_repo import StatsRepository
from src.app.services.events_service import EventService
from src.app.broker.nats import nats_client
from src.app.services.stats_service import StatsService


async def provide_event_service() -> EventService:
    return EventService(broker=nats_client)


async def provide_stats_repo() -> StatsRepository:
    return StatsRepository()


async def provide_stats_service(repo: StatsRepository) -> StatsService:
    return StatsService(repo)
