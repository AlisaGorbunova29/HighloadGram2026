#!/bin/bash
set -e
echo "host replication replicator 0.0.0.0/0 scram-sha-256" >> "$PGDATA/pg_hba.conf"
pg_ctl reload -D "$PGDATA"
