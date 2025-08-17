import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
import re
from decimal import Decimal

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# structured inputs
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

#define mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        # Email uniqueness check
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists.")
        # Phone validation if provided
        if input.phone and not re.match(r"^\+?\d{7,15}$|^\d{3}-\d{3}-\d{4}$", input.phone):
            errors.append("Invalid phone format.")
        if errors:
            return CreateCustomer(errors=errors, message="Failed to create customer.")

        customer = Customer.objects.create(
            name=input.name, email=input.email, phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []
        with transaction.atomic():
            for data in input:
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Email {data.email} already exists.")
                    continue
                if data.phone and not re.match(r"^\+?\d{7,15}$|^\d{3}-\d{3}-\d{4}$", data.phone):
                    errors.append(f"Invalid phone format for {data.email}.")
                    continue
                customer = Customer.objects.create(
                    name=data.name, email=data.email, phone=data.phone
                )
                customers.append(customer)
        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        if input.price <= 0:
            errors.append("Price must be positive.")
        if input.stock is not None and input.stock < 0:
            errors.append("Stock cannot be negative.")
        if errors:
            return CreateProduct(errors=errors)

        product = Product.objects.create(
            name=input.name,
            price=Decimal(str(input.price)),
            stock=input.stock or 0
        )
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(errors=errors)

        if not input.product_ids:
            errors.append("At least one product ID is required.")
            return CreateOrder(errors=errors)

        products = Product.objects.filter(id__in=input.product_ids)
        if not products.exists():
            errors.append("No valid products found.")
            return CreateOrder(errors=errors)

        total_amount = sum([p.price for p in products])

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date or timezone.now()
        )
        order.products.set(products)

        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


#graphql types
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
    order_date = graphene.DateTime()