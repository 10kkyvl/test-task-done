from src.app.api.v1 import events as events_v1
from src.app.api.v1 import stats as stats_v1

route_handlers = [
    *events_v1.route_handlers,
    *stats_v1.route_handlers,
]
