#!/bin/bash
set -e

export PGDATA=${PGDATA:-/var/lib/postgresql/data}

if [ -z "$(ls -A "$PGDATA" 2>/dev/null)" ]; then
    echo "Pulling base backup from master..."
    mkdir -p "$PGDATA"
    chown postgres:postgres "$PGDATA"

    max_attempts=30
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        rm -rf "${PGDATA}"/*
        if su - postgres -c "PGPASSWORD=replicator_pass pg_basebackup -h postgres-master -D ${PGDATA} -U replicator -v -P -R -X stream"; then
            echo "Base backup done."
            break
        fi
        echo "Waiting for master... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    if [ $attempt -gt $max_attempts ]; then
        echo "Failed to pull base backup after $max_attempts attempts"
        exit 1
    fi

    chmod 700 "$PGDATA"
fi

exec su - postgres -c "postgres -D ${PGDATA}"
