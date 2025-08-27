#!/bin/bash

# Get current date for logging
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Change to the project directory
cd /home/evie/ALX/ProBackend/alx-graphql/alx_backend_graphql

# Activate virtual environment if needed
# source venv/bin/activate

# Run the cleanup command and capture output
OUTPUT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

try:
    # Calculate date one year ago
    one_year_ago = timezone.now() - timedelta(days=365)
    
    # Find customers with no orders in the last year
    inactive_customers = Customer.objects.filter(
        orders__isnull=True,
        created_at__lt=one_year_ago
    )
    
    # Get count before deletion
    count = inactive_customers.count()
    
    # Delete the inactive customers
    deleted_count, _ = inactive_customers.delete()
    
    print(f'Successfully deleted {deleted_count} inactive customers')
    
except Exception as e:
    print(f'Error during customer cleanup: {str(e)}')
" 2>&1)

# Log the output
echo "[$TIMESTAMP] $OUTPUT" >> /tmp/customer_cleanup_log.txt

echo "Cleanup completed at $TIMESTAMP" >> /tmp/customer_cleanup_log.txt