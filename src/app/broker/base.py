from abc import ABC, abstractmethod
from typing import Dict, Any


class Broker(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def publish(self, subject: str, message: Dict[str, Any]):
        pass

    @abstractmethod
    async def drain(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def shutdown(self):
        pass
