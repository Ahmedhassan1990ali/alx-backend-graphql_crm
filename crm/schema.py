import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from .models import Customer, Product, Order

# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Input Types
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

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone or ""
            )
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully"
            )
        except Exception as e:
            raise Exception(f"Error creating customer: {str(e)}")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, inputs):
        customers = []
        errors = []
        
        for idx, input in enumerate(inputs):
            try:
                customer = Customer.objects.create(
                    name=input.name,
                    email=input.email,
                    phone=input.phone or ""
                )
                customers.append(customer)
            except Exception as e:
                errors.append(f"Row {idx+1}: {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input):
        try:
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=input.stock or 0
            )
            return CreateProduct(product=product)
        except Exception as e:
            raise Exception(f"Error creating product: {str(e)}")

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
            products = Product.objects.filter(pk__in=input.product_ids)
            
            if not products.exists():
                raise Exception("At least one valid product must be selected")
            
            order = Order.objects.create(customer=customer)
            order.products.set(products)
            order.save()  # Triggers total_amount calculation
            
            return CreateOrder(order=order)
        except Customer.DoesNotExist:
            raise Exception("Customer does not exist")
        except Product.DoesNotExist:
            raise Exception("One or more products do not exist")
        except Exception as e:
            raise Exception(f"Error creating order: {str(e)}")

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()