#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx-backend-graphql_crm.settings')
django.setup()

def send_order_reminders():
    """Query GraphQL endpoint for pending orders and log reminders."""
    
    # GraphQL endpoint URL
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    # GraphQL query for orders within the last 7 days
    query = gql("""
        query GetRecentOrders($startDate: DateTime!) {
            orders(orderDate_Gte: $startDate) {
                id
                orderDate
                customer {
                    email
                }
            }
        }
    """)
    
    try:
        # Execute the query
        result = client.execute(query, variable_values={"startDate": seven_days_ago.isoformat()})
        
        # Log each order
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entries = []
        
        for order in result.get('orders', []):
            order_id = order['id']
            customer_email = order['customer']['email']
            log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}"
            log_entries.append(log_entry)
        
        # Write to log file
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            for entry in log_entries:
                log_file.write(entry + '\n')
        
        print("Order reminders processed!")
        
    except Exception as e:
        # Log error
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"[{timestamp}] Error processing order reminders: {str(e)}"
        
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(error_msg + '\n')
        
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_order_reminders()
