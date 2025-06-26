#!/bin/bash
set -e

echo "🚀 Starting Django application with cron support..."

echo "🧹 Removing existing cron jobs..."
python manage.py crontab remove || echo "No existing cron jobs to remove"

echo "➕ Adding new cron jobs..."
python manage.py crontab add

echo "📋 Listing current cron jobs..."
python manage.py crontab show

echo "⏰ Starting cron daemon..."
cron

# Create log files if they don't exist
touch /var/log/cron.log
touch /app/logs/django.log
touch /app/logs/cron_output.log
touch /tmp/cron_model_prediction.log

echo "📊 Starting log monitoring in background..."
# Monitor multiple log files and output to console
(
    echo "=== CRON LOGS ==="
    tail -f /var/log/cron.log 2>/dev/null &
    echo "=== DJANGO LOGS ==="
    tail -f /app/logs/django.log 2>/dev/null &
    echo "=== CRON OUTPUT LOGS ==="
    tail -f /tmp/cron_model_prediction.log 2>/dev/null &
    wait
) &

echo "🚀 Starting Django development server on 0.0.0.0:8001..."
echo "📝 Live logs will appear below..."
echo "=================================================="

# Start Django with logging to both file and console
python manage.py runserver 0.0.0.0:8001 2>&1 
# | tee -a /app/logs/django.log