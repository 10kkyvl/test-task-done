#!/bin/bash

set -e

until cqlsh -u "${SCYLLA_USER}" -p "${SCYLLA_PASSWORD}" -e "SELECT now() FROM system.local;" &>/dev/null; do
  echo "Ожидание готовности Scylla..."
  sleep 5
done

#cqlsh -u "${SCYLLA_USER}" -p "${SCYLLA_PASSWORD}" -e "
#  CREATE KEYSPACE IF NOT EXISTS ${SCYLLA_KEYSPACE} WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
#"

cqlsh -u "${SCYLLA_USER}" -p "${SCYLLA_PASSWORD}" -f /scripts/create_schema.cql

#cqlsh -u "${SCYLLA_USER}" -p "${SCYLLA_PASSWORD}" -f /scripts/populate_db.cql
