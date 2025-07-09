#!/bin/bash

echo "RUNNING my service"

echo "${PDB_HOST}"
echo "${PDB_PORT}"

echo "Waiting for my service Postgres Database"
while ! nc -z ${PDB_HOST} ${PDB_PORT}; do sleep 2; done
echo "Connected to my Database"

echo "Waiting for Redis"
while ! nc -z ${REDIS_HOST} ${REDIS_PORT}; do sleep 2; done
echo "Connected to Redis"

if [[ $# -gt 0  ]]; then
    echo "Execute Command..."
    INPUT=$@
    sh -c "$INPUT"
else
    mkdir -p /var/logs/application_logs

    if [[ "$DEBUG" = "True" ]]; then
        echo "Running migrations (debug mode)..."

        # Capture migration output and check for inconsistency error
        MIGRATE_OUTPUT=$(python /home/alibaba/manage.py migrate --noinput 2>&1)
        echo "$MIGRATE_OUTPUT"

        if echo "$MIGRATE_OUTPUT" | grep -q "InconsistentMigrationHistory"; then
            echo "Detected InconsistentMigrationHistory. Attempting to fake users.0001_initial..."

            python /home/alibaba/manage.py migrate users --fake
            python /home/alibaba/manage.py migrate --noinput
        elif echo "$MIGRATE_OUTPUT" | grep -q "Traceback"; then
            echo "Migration failed unexpectedly." >&2
            exit 1
        fi
    fi

    echo "Starting Gunicorn..."

    exec gunicorn alibaba.wsgi:application \
       --name alibaba-gunicorn \
       --bind 0.0.0.0:8080 \
       --workers $GUNICORN_WORKER_NUMBER \
       --pythonpath "/home/alibaba" \
       --log-level=info \
       --log-file=- \
       --timeout $GUNICORN_TIMEOUT \
       --reload
fi

