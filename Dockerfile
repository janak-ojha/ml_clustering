# Use Python 3.7 slim base image
FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && \
    apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    cron \
    curl \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Create necessary directories and log files
RUN mkdir -p /app/logs
RUN touch /var/log/cron.log
RUN touch /app/logs/django.log
RUN touch /app/logs/cron_output.log

# Set proper permissions
RUN chmod 644 /var/log/cron.log
RUN chmod 755 /app/logs

# Add an entrypoint shell script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create a script to monitor logs
COPY log_monitor.sh /app/log_monitor.sh
RUN chmod +x /app/log_monitor.sh

EXPOSE 8001

# Run the shell script that starts both cron and Django
CMD ["/app/entrypoint.sh"]