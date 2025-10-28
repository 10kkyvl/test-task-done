import time
from collections import deque
from threading import Lock
from litestar.types import ASGIApp, Receive, Scope, Send
from src.app.core.metrics import REQUEST_COUNT, RPS


class MetricsMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.lock = Lock()
        self.request_times = deque()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] == "/metrics":
            await self.app(scope, receive, send)
            return

        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        start = time.time()
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            REQUEST_COUNT.labels(status=status_code).inc()
            now = time.time()
            with self.lock:
                self.request_times.append(now)
                cutoff = now - 1
                while self.request_times and self.request_times[0] < cutoff:
                    self.request_times.popleft()
                RPS.set(len(self.request_times))
