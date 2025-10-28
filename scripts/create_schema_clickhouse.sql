CREATE DATABASE IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.events
(
    event_id UUID,
    occurred_at DateTime64(3, 'UTC'),
    user_id UInt64,
    event_type String,
    properties String
)
ENGINE = ReplacingMergeTree()
PARTITION BY toDate(occurred_at)
ORDER BY (user_id, event_id);
