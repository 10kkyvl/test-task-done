#!/bin/bash
set -e

clickhouse-client --host="${CLICKHOUSE_HOST}" --port="${CLICKHOUSE_PORT}" --multiquery < /scripts/create_schema_clickhouse.sql
