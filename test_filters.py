import os
import sys
import django
from django.conf import settings

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx-backend-graphql_crm.settings')
django.setup()

# Import the schema
import importlib
alx_backend_graphql_crm = importlib.import_module('alx-backend-graphql_crm')
schema_module = importlib.import_module('alx-backend-graphql_crm.schema')
schema = schema_module.schema

print("Schema loaded successfully!")
print("Schema has query:", schema.query is not None)
print("Schema has mutation:", schema.mutation is not None)

# Test that the schema has the expected fields
if schema.query:
    fields = schema.query._meta.fields
    print("Available query fields:")
    for field_name in fields:
        print(f"  - {field_name}")
        
    # Check if our filtered fields are present
    expected_fields = ['all_customers', 'all_products', 'all_orders']
    for field in expected_fields:
        if field in fields:
            print(f"✓ {field} field is available")
        else:
            print(f"✗ {field} field is missing")
            
    # Also check for the relay-style fields
    relay_fields = ['allCustomers', 'allProducts', 'allOrders']
    for field in relay_fields:
        if field in fields:
            print(f"✓ {field} relay field is available")
        else:
            print(f"✗ {field} relay field is missing")
else:
    print("Could not get query type from schema")