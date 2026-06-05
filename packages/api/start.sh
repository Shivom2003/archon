#!/bin/bash
# Startup script — runs migrations then starts the server.
# Using a script (vs CMD chaining) gives cleaner error messages.
set -e

echo "==> Running database migrations..."
alembic upgrade head

echo "==> Starting Archon API on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
