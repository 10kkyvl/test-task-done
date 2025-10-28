import os

from litestar import Litestar
from litestar.config.cors import CORSConfig

from src.app.api.v1 import route_handlers
from src.app.core.metrics import route_handlers as metrics
from src.app.broker.nats import nats_client
from src.app.db.clickhouse import clickhouse
from src.app.core.logger import logger
from src.app.middleware.metrics_middleware import MetricsMiddleware

STREAMS = [
    {
        "name": "EVENTS_HOT",
        "subjects": ["events_hot"],
        "dlq_subject": "events_hot.dlq",
        "max_deliver": 3,
        "storage": "file",
    },
]


async def create_streams_on_startup() -> None:
    await nats_client.connect()
    await nats_client.add_streams(STREAMS)


def create_app() -> Litestar:
    cors_config = CORSConfig(
        allow_origins=["*"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app = Litestar(
        route_handlers=route_handlers + metrics,
        debug=os.getenv("DEBUG", False),
        cors_config=cors_config,
        middleware=[MetricsMiddleware],
        on_startup=[clickhouse.connect, create_streams_on_startup],
        on_shutdown=[clickhouse.close, nats_client.shutdown],
    )

    return app


app = create_app()
