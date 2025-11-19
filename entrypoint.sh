#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL..."
until nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ PostgreSQL is up!"

echo "📦 Running Alembic migrations..."
alembic upgrade head

echo "🚀 Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000