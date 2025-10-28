CREATE KEYSPACE IF NOT EXISTS analytics
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

USE analytics;

CREATE TABLE IF NOT EXISTS events (
    event_id uuid,
    user_id bigint,
    event_type text,
    occurred_at timestamp,
    properties text,
    PRIMARY KEY (event_id)
) WITH default_time_to_live = 86400
  AND bloom_filter_fp_chance = 0.01
  AND compaction = {'class': 'SizeTieredCompactionStrategy'}
  AND compression = {'sstable_compression': 'org.apache.cassandra.io.compress.LZ4Compressor'};
