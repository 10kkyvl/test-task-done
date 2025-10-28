#!/bin/bash

cqlsh "${SCYLLA_HOST}" "${SCYLLA_PORT}" -u "${SCYLLA_USER}" -p "${SCYLLA_PASSWORD}" -f /scripts/create_schema.cql
