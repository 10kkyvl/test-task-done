import os
from dataclasses import dataclass


@dataclass
class ScyllaSettings:
    host: str
    port: int
    datacenter: str
    keyspace: str
    user: str
    password: str


@dataclass
class RedisSettings:
    host: str
    port: int
    password: str

    @property
    def url(self) -> str:
        return f"redis://:{self.password}@{self.host}:{self.port}/0"


@dataclass
class NatsSettings:
    host: str
    port: int
    user: str
    password: str

    @property
    def url(self) -> str:
        return f"nats://{self.user}:{self.password}@{self.host}:{self.port}"


@dataclass
class ClickhouseSettings:
    host: str
    port: int
    http_port: int

    @property
    def url(self) -> str:
        return f"clickhouse://{self.host}:{self.port}/default"


@dataclass
class AppSettings:
    host: str
    port: int


@dataclass
class Settings:
    scylla: ScyllaSettings
    redis: RedisSettings
    nats: NatsSettings
    clickhouse: ClickhouseSettings
    app: AppSettings


def load_settings() -> Settings:
    return Settings(
        scylla=ScyllaSettings(
            host=os.getenv("SCYLLA_HOST", "scylla"),
            port=int(os.getenv("SCYLLA_PORT", "9042")),
            datacenter=os.getenv("SCYLLA_DATACENTER", "datacenter1"),
            keyspace=os.getenv("SCYLLA_KEYSPACE", "analytics_events"),
            user=os.getenv("SCYLLA_USER", "cassandra"),
            password=os.getenv("SCYLLA_PASSWORD", "cassandra"),
        ),
        redis=RedisSettings(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", "super_secure_redis_pass"),
        ),
        nats=NatsSettings(
            host=os.getenv("NATS_HOST", "nats"),
            port=int(os.getenv("NATS_PORT", "4222")),
            user=os.getenv("NATS_USER", "analytics_nats"),
            password=os.getenv("NATS_PASSWORD", "super_secure_nats_pass"),
        ),
        clickhouse=ClickhouseSettings(
            host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
            port=int(os.getenv("CLICKHOUSE_PORT", "9000")),
            http_port=int(os.getenv("CLICKHOUSE_HTTP_PORT", "8123")),
        ),
        app=AppSettings(
            host=os.getenv("LITESTAR_HOST", "0.0.0.0"),
            port=int(os.getenv("LITESTAR_PORT", "8000")),
        ),
    )


settings = load_settings()
