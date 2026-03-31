#!/bin/sh
set -e

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8020 \
    --workers "${UVICORN_WORKERS:-4}" \
    --timeout-keep-alive 300 \
    --forwarded-allow-ips="*"
