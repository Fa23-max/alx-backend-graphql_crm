import os
import sys
import django
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx-backend-graphql_crm.settings')
django.setup()

from crm.models import Product

def log_crm_heartbeat():
    """Log a heartbeat message every 5 minutes to confirm CRM health."""
    
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    heartbeat_msg = f"{timestamp} CRM is alive"
    
    try:
        # Optionally query GraphQL hello field to verify endpoint is responsive
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        query = gql("""
            query {
                hello
            }
        """)
        
        result = client.execute(query)
        if result.get('hello'):
            heartbeat_msg += " - GraphQL endpoint responsive"
        
    except Exception as e:
        heartbeat_msg += f" - GraphQL endpoint error: {str(e)}"
    
    # Append to log file
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(heartbeat_msg + '\n')

def update_low_stock():
    """Execute UpdateLowStockProducts mutation and log updates."""
    
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Execute the mutation
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)
        
        result = client.execute(mutation)
        
        # Log the results
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mutation_result = result.get('updateLowStockProducts', {})
        
        log_entries = [f"[{timestamp}] Low stock update executed"]
        
        if mutation_result.get('success'):
            log_entries.append(f"Success: {mutation_result.get('message', 'Products updated')}")
            
            for product in mutation_result.get('updatedProducts', []):
                log_entries.append(f"Updated: {product['name']} - New stock: {product['stock']}")
        else:
            log_entries.append(f"Failed: {mutation_result.get('message', 'Unknown error')}")
        
        # Write to log file
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            for entry in log_entries:
                log_file.write(entry + '\n')
                
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"[{timestamp}] Error updating low stock products: {str(e)}"
        
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(error_msg + '\n')
