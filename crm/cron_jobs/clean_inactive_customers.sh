#!/bin/bash

# Clean inactive customers script
# Deletes customers with no orders since a year ago

# Get the project directory (assuming script is in crm/cron_jobs)
PROJECT_DIR="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"

# Navigate to project directory
cd "$PROJECT_DIR"

# Execute Django command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since a year ago
inactive_customers = Customer.objects.exclude(
    order__order_date__gte=one_year_ago
).distinct()

# Count and delete
count = inactive_customers.count()
inactive_customers.delete()
print(count)
" 2>/dev/null)

# Log the result with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt

echo "Customer cleanup completed. Deleted $DELETED_COUNT customers."
