# Celery CRM Report Setup Guide

## Prerequisites
- Redis server installed and running
- Python 3.8+ with pip

## Setup Instructions

1. Install Python Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run Database Migrations:
   ```bash
   python manage.py migrate
   ```

3. Start Celery Worker (in terminal 1):
   ```bash
   celery -A crm worker -l info
   ```

4. Start Celery Beat (in terminal 2):
   ```bash
   celery -A crm beat -l info
   ```
5. Install Redis (Ubuntu/Debian):
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```

6. Optional: Start Flower for Monitoring (in terminal 3):
   ```bash
   celery -A crm flower --port=5555
   ```

## Verification

1. **Check Redis Connection**:
   ```bash
   redis-cli ping
   # Should return "PONG"
   ```

2. **Verify Celery Workers**:
   - Check terminal output for worker startup messages
   - Look for "Connected to redis://localhost:6379/0"

3. **Check Scheduled Tasks**:
   - Celery Beat should show the scheduled task
   - Look for "Scheduler: Sending due task generate-crm-report"

4. **View Reports**:
   ```bash
   tail -f /tmp/crm_report_log.txt
   ```

## Troubleshooting

1. **Redis Connection Issues**:
   - Ensure Redis is running: `sudo systemctl status redis`
   - Check Redis port: `netstat -tulpn | grep 6379`

2. **Celery Worker Issues**:
   - Check Django settings: `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`
   - Verify task discovery: `celery -A crm inspect registered`

3. **Permissions Issues**:
   - Ensure write permissions to `/tmp/crm_report_log.txt`

## Monitoring

- Flower dashboard: http://localhost:5555
- Celery task status: `celery -A crm status`
- Worker monitoring: `celery -A crm inspect active`
