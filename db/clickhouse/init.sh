#!/bin/bash
set -e

retry_query() {
    local host=$1
    local query=$2
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if clickhouse-client --host "$host" --query "$query"; then
            return 0
        fi
        echo "Waiting for $host... (attempt $attempt/$max_attempts)"
        sleep 1
        attempt=$((attempt + 1))
    done
    echo "Failed to connect to $host after $max_attempts attempts"
    exit 1
}

retry_query clickhouse-shard1 "
    CREATE TABLE IF NOT EXISTS messages_local (
        message_id UInt64,
        channel_id UInt64,
        tag_id UInt64 DEFAULT 0,
        user_id UInt64,
        created_at DateTime
    ) ENGINE = MergeTree()
    PARTITION BY toYYYYMM(created_at)
    ORDER BY (channel_id, tag_id, created_at);
"

retry_query clickhouse-shard2 "
    CREATE TABLE IF NOT EXISTS messages_local (
        message_id UInt64,
        channel_id UInt64,
        tag_id UInt64 DEFAULT 0,
        user_id UInt64,
        created_at DateTime
    ) ENGINE = MergeTree()
    PARTITION BY toYYYYMM(created_at)
    ORDER BY (channel_id, tag_id, created_at);
"

retry_query clickhouse-shard1 "
    CREATE TABLE IF NOT EXISTS messages_dist AS messages_local
    ENGINE = Distributed('cluster_1', 'default', 'messages_local', intHash64(channel_id));
"

retry_query clickhouse-shard1 "
    CREATE TABLE IF NOT EXISTS analytics_local (
        channel_id UInt64,
        period Date,
        messages_count UInt64,
        active_users UInt64,
        subscribers_count UInt64,
        version UInt64
    ) ENGINE = ReplacingMergeTree(version)
    ORDER BY (channel_id, period);
"

retry_query clickhouse-shard2 "
    CREATE TABLE IF NOT EXISTS analytics_local (
        channel_id UInt64,
        period Date,
        messages_count UInt64,
        active_users UInt64,
        subscribers_count UInt64,
        version UInt64
    ) ENGINE = ReplacingMergeTree(version)
    ORDER BY (channel_id, period);
"

retry_query clickhouse-shard1 "
    CREATE TABLE IF NOT EXISTS analytics_dist AS analytics_local
    ENGINE = Distributed('cluster_1', 'default', 'analytics_local', intHash64(channel_id));
"

echo "ClickHouse init done."
