-- Создание базы
CREATE DATABASE IF NOT EXISTS analytics;

-- Таблица событий
CREATE TABLE IF NOT EXISTS analytics.events
(
    event_id UUID,
    user_id UUID,
    event_type String,
    occurred_at DateTime64(3, 'UTC'),
    properties JSON
)
ENGINE = ReplacingMergeTree(event_id)
PARTITION BY toDate(occurred_at)
ORDER BY (event_id);
