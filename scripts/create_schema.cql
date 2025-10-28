CREATE KEYSPACE IF NOT EXISTS analytics
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS analytics.events (
    event_id uuid,
    user_id uuid,
    event_type text,
    occurred_at timestamp,
    properties text,
    PRIMARY KEY (event_id)
);
