#!/bin/bash

# Navigate to the project root (adjust path if needed)
cd "$(dirname "$0")/../.."

# Run Django shell command to delete inactive customers
deleted_count=$(python manage.py shell -c "
import datetime
from crm.models import Customer, Order
from django.utils import timezone

one_year_ago = timezone.now() - datetime.timedelta(days=365)
inactive_customers = Customer.objects.exclude(
    order__created_at__gte=one_year_ago
).distinct()

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log result with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt

