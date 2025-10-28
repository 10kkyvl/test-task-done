import os
import csv
import json
import uuid
import time
import argparse
from datetime import datetime
from clickhouse_connect import get_client


def parse_datetime(dt_str: str) -> str:
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def connect_clickhouse():
    host = os.getenv("CLICKHOUSE_HOST", "localhost")
    port = int(os.getenv("CLICKHOUSE_HTTP_PORT", "8123"))
    user = os.getenv("CLICKHOUSE_USER", "default")
    password = os.getenv("CLICKHOUSE_PASSWORD", "")
    db = os.getenv("CLICKHOUSE_KEYSPACE", "analytics")

    client = get_client(
        host=host, port=port, username=user, password=password, database=db
    )

    for _ in range(10):
        try:
            client.command("SELECT 1")
            print(f"Connected to ClickHouse at {host}:{port}")
            return client
        except Exception as e:
            print(f"Waiting for ClickHouse... {e}")
            time.sleep(3)
    raise RuntimeError("Can't reach ClickHouse server")


def insert_csv(client, file_path: str, batch_size: int = 1000):
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        total = 0

        for row in reader:
            props = json.loads(row["properties_json"])
            props_str = json.dumps(props, ensure_ascii=False)

            rows.append(
                [
                    uuid.UUID(row["event_id"]),
                    parse_datetime(row["occurred_at"]),
                    int(row["user_id"]),
                    row["event_type"],
                    props_str,
                ]
            )

            if len(rows) >= batch_size:
                client.insert(
                    "analytics.events",
                    rows,
                    column_names=[
                        "event_id",
                        "occurred_at",
                        "user_id",
                        "event_type",
                        "properties",
                    ],
                )
                total += len(rows)
                print(f"Inserted {len(rows)} rows (total: {total})")
                rows.clear()

        if rows:
            client.insert(
                "analytics.events",
                rows,
                column_names=[
                    "event_id",
                    "occurred_at",
                    "user_id",
                    "event_type",
                    "properties",
                ],
            )
            total += len(rows)
            print(f"Inserted {len(rows)} rows (total: {total})")

    print(f"Import completed: {total} rows inserted.")


def main():
    parser = argparse.ArgumentParser(
        description="Import events from CSV into ClickHouse."
    )
    parser.add_argument("csv_path", help="Path to CSV file with events.")
    parser.add_argument(
        "--batch-size", type=int, default=1000, help="Batch size for inserts."
    )
    args = parser.parse_args()

    client = connect_clickhouse()
    insert_csv(client, args.csv_path, args.batch_size)


if __name__ == "__main__":
    main()
