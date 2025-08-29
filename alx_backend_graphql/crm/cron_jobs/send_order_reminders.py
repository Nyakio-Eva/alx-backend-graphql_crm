#!/usr/bin/env python3
import sys
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date 7 days ago
seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat()

# GraphQL query to get orders from the last 7 days
query = gql("""
    query GetRecentOrders($since: Date!) {
        orders(orderDate_Gte: $since, status: "PENDING") {
            id
            customer {
                email
            }
        }
    }
""")

params = {"since": seven_days_ago}

try:
    result = client.execute(query, variable_values=params)
    orders = result.get("orders", [])

    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for order in orders:
            log_file.write(f"{timestamp} - Reminder: Order {order['id']} for {order['customer']['email']}\n")

    print("Order reminders processed!")

except Exception as e:
    sys.stderr.write(f"Error processing reminders: {e}\n")
    sys.exit(1)

