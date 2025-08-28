#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Navigate two levels up to reach project root (where manage.py is located)
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to project root directory (where manage.py is located)
cd "$PROJECT_DIR"

# Execute the Django management command to clean up inactive customers
OUTPUT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order
from django.db.models import Max

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since one year ago
inactive_customers = Customer.objects.annotate(
    last_order_date=Max('order__order_date')
).filter(
    last_order_date__lt=one_year_ago
) | Customer.objects.filter(
    order__isnull=True
)

count = inactive_customers.count()
inactive_customers.delete()
print(f'Deleted {count} inactive customers')
")

# Log the result with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] $OUTPUT" >> /tmp/customer_cleanup_log.txt