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

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A remosphere worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

# Wait a moment for Celery to start
sleep 2

# Start Django with Gunicorn in the foreground
echo "Starting Django application..."
exec gunicorn remosphere.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 2 --log-level info

# Note: If Gunicorn exits, the container will stop
# Celery will be automatically terminated when the container stops
