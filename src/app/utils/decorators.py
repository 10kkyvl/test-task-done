from functools import wraps


def ensure_nats_connected(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not getattr(self, "client", None) or not self.client.is_connected:
            raise RuntimeError("NATS server not connected")
        if not getattr(self, "js", None):
            raise RuntimeError("JetStream context not initialized")
        return await func(self, *args, **kwargs)

    return wrapper
