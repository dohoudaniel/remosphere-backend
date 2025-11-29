#!/bin/bash
set -e

echo "======================================="
echo "Starting RemoSphere Backend Services"
echo "======================================="

# Run Django migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Supervisor to manage Django + Celery
echo "Starting Django and Celery via Supervisor..."
exec /usr/bin/supervisord -c /app/supervisord.conf
