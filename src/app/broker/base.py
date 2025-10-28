from abc import ABC, abstractmethod
from typing import Dict


class Broker(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def publish(self):
        pass

    @abstractmethod
    async def drain(self):
        pass

    @abstractmethod
    async def close(self):
        pass

