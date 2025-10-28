#!/bin/bash

set -e

until clickhouse-client --host="${CLICKHOUSE_HOST}" --port="${CLICKHOUSE_PORT}" --query "SELECT 1" &>/dev/null; do
  echo "Ожидание готовности ClickHouse..."
  sleep 5
done

clickhouse-client --host="${CLICKHOUSE_HOST}" --port="${CLICKHOUSE_PORT}" --query "
  CREATE TABLE IF NOT EXISTS ${CLICKHOUSE_KEYSPACE}.events (
    id UUID,
    event_time DateTime,
    event_type String,
    data String
  ) ENGINE = MergeTree()
  PARTITION BY toYYYYMM(event_time)
  ORDER BY (event_time, id);
"

clickhouse-client --host="${CLICKHOUSE_HOST}" --port="${CLICKHOUSE_PORT}" --query "
  INSERT INTO ${CLICKHOUSE_KEYSPACE}.events
  FORMAT CSV
" < "$1"
