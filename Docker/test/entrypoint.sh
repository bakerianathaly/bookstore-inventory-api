#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for PostgreSQL to be ready..."

    max_retries=30
    count=0

    until python -c "
import sys
try:
    import psycopg2
    conn = psycopg2.connect('$DATABASE_URL')
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
        count=$((count + 1))
        if [ $count -ge $max_retries ]; then
            echo "Error: PostgreSQL not available after $max_retries attempts. Exiting."
            exit 1
        fi
        echo "PostgreSQL not ready yet (attempt $count/$max_retries). Retrying in 2s..."
        sleep 2
    done

    echo "PostgreSQL is ready."
fi

exec "$@"
