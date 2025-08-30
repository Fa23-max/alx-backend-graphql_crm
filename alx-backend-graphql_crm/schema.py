import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

class Query(graphene.ObjectType):
    hello = graphene.String()
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType, order_date_gte=graphene.DateTime())
    
    def resolve_hello(self, info):
        return "Hello, GraphQL!"
    
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info, order_date_gte=None):
        queryset = Order.objects.all()
        if order_date_gte:
            queryset = queryset.filter(order_date__gte=order_date_gte)
        return queryset

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
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)