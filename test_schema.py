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