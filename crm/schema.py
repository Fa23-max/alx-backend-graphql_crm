import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
import re
from .models import Customer, Product, Order
from crm.models import Product
from .filters import CustomerFilter, ProductFilter, OrderFilter

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")
        interfaces = (graphene.relay.Node, )

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at")
        interfaces = (graphene.relay.Node, )

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")
        interfaces = (graphene.relay.Node, )

# Input types for mutations
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutation classes
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        # Validate phone format if provided
        if input.phone:
            # Simple phone validation (allows +1234567890 or 123-456-7890 format)
            phone_pattern = r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$'
            if not re.match(phone_pattern, input.phone):
                raise Exception("Invalid phone format. Use +1234567890 or 123-456-7890")

        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        error_messages = []

        for i, customer_input in enumerate(input):
            try:
                # Validate email uniqueness
                if Customer.objects.filter(email=customer_input.email).exists():
                    error_messages.append(f"Customer {i+1}: Email already exists")
                    continue

                # Validate phone format if provided
                if customer_input.phone:
                    phone_pattern = r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$'
                    if not re.match(phone_pattern, customer_input.phone):
                        error_messages.append(f"Customer {i+1}: Invalid phone format")
                        continue

                customer = Customer(
                    name=customer_input.name,
                    email=customer_input.email,
                    phone=customer_input.phone
                )
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                error_messages.append(f"Customer {i+1}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=error_messages)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        # Validate price is positive
        if input.price <= 0:
            raise Exception("Price must be positive")

        # Validate stock is not negative
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(
            name=input.name,
            price=input.price,
            stock=stock
        )
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        # Validate at least one product is selected
        if not input.product_ids:
            raise Exception("At least one product must be selected")

        # Validate all products exist
        products = []
        total_amount = 0
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(id=product_id)
                products.append(product)
                total_amount += product.price
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {product_id}")

        # Create order
        order = Order(
            customer=customer,
            total_amount=total_amount
        )
        order.save()
        
        # Associate products with the order
        for product in products:
            order.products.add(product)
            
        # Refresh from database to ensure all fields are populated
        order.refresh_from_db()
        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass
    
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)
    
    def mutate(self, info):
        # Find products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        
        for product in low_stock_products:
            product.stock += 10  # Increment stock by 10
            product.save()
            updated_products.append(product)
        
        return UpdateLowStockProducts(
            success=True,
            message=f"Updated {len(updated_products)} low-stock products",
            updated_products=updated_products
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    
    def resolve_hello(self, info):
        return "Hello, GraphQL!"
        
    def resolve_all_customers(self, info, **kwargs):
        return Customer.objects.all()
        
    def resolve_all_products(self, info, **kwargs):
        return Product.objects.all()
        
    def resolve_all_orders(self, info, **kwargs):
        return Order.objects.all()