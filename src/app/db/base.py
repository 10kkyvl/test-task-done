from abc import ABC, abstractmethod


class BaseDatabase(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass
