import os
from typing import List, Any, Optional
from loguru import logger
import clickhouse_connect
from clickhouse_connect.driver.asyncclient import AsyncClient

from src.app.db.base import BaseDatabase
from src.app.core.config import settings


class ClickHouse(BaseDatabase):
    def __init__(self):
        self._client: Optional[AsyncClient] = None
        self._host = settings.clickhouse.host
        self._port = settings.clickhouse.http_port
        self._user = settings.clickhouse.user
        self._password = settings.clickhouse.password
        self._database = settings.clickhouse.database

    async def connect(self) -> AsyncClient:
        if self._client is None:
            self._client = await clickhouse_connect.get_async_client(
                host=self._host,
                port=self._port,
                username=self._user,
                password=self._password,
                database=self._database,
            )
            logger.info(f"Connected to ClickHouse at {self._host}:{self._port}")
        return self._client

    async def execute(self, query: str, parameters: Optional[List[Any]] = None):
        client = await self.connect()
        result = await client.query(query, parameters or [])
        return result.result_rows

    async def insert(
        self, table: str, rows: List[list], columns: Optional[List[str]] = None
    ):
        client = await self.connect()
        await client.insert(table, rows, column_names=columns)
        logger.debug(f"Inserted {len(rows)} rows into {table}")

    async def command(self, query: str):
        client = await self.connect()
        await client.command(query)
        logger.debug(f"Executed command: {query}")

    async def close(self):
        if self._client:
            await self._client.close()
            logger.info("Closed ClickHouse connection.")
            self._client = None

    @property
    def client(self):
        return self._client


clickhouse = ClickHouse()
