#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for PostgreSQL to be ready..."

    max_retries=30
    count=0

    until python -c "
import socket, sys
try:
    s = socket.create_connection(('db', 5432), timeout=3)
    s.close()
    sys.exit(0)
except Exception as e:
    print(f'Connection error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1; do
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
