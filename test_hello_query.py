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

# Test the hello query
from graphene.test import Client
client = Client(schema)

# Execute a simple query
query = '''
{
  hello
}
'''

result = client.execute(query)
print("Query result:", result)

if 'data' in result and 'hello' in result['data']:
    print("SUCCESS: Hello query works correctly")
    print("  Response:", result['data']['hello'])
else:
    print("FAILED: Hello query failed")
    print("  Result:", result)