#!/bin/bash

# Script to monitor and display logs in real-time
echo "🔍 Starting comprehensive log monitoring..."

# Function to format log output with timestamps and labels
format_logs() {
    local label=$1
    local logfile=$2
    local color=$3
    
    tail -f "$logfile" 2>/dev/null | while read line; do
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo -e "${color}[$timestamp] [$label] $line\033[0m"
    done &
}

# Create log files if they don't exist
touch /var/log/cron.log
touch /app/logs/django.log
touch /app/logs/cron_output.log
touch /tmp/cron_model_prediction.log

# Start monitoring different log files with different colors
echo "Starting log monitors..."

# Cron system logs (Red)
format_logs "CRON-SYS" "/var/log/cron.log" "\033[0;31m"

# Django application logs (Green)
format_logs "DJANGO" "/app/logs/django.log" "\033[0;32m"

# Cron job output logs (Blue)
format_logs "CRON-OUT" "/tmp/cron_model_prediction.log" "\033[0;34m"

# Additional cron output (Yellow)
format_logs "CRON-APP" "/app/logs/cron_output.log" "\033[0;33m"

echo "📊 Log monitoring started. Press Ctrl+C to stop."

# Keep the script running
wait