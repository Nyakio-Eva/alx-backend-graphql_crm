from django.core.management.base import BaseCommand
from crm.models import Customer, Product, Order
from decimal import Decimal
from datetime import datetime
import random


class Command(BaseCommand):
    help = "Seed the database with sample customers, products, and orders."

    def handle(self, *args, **kwargs):
        # Customers
        customers_data = [
            {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
            {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
            {"name": "Carol", "email": "carol@example.com"},
        ]

        customers = []
        for data in customers_data:
            customer, _ = Customer.objects.get_or_create(**data)
            customers.append(customer)

        # Products
        products_data = [
            {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
            {"name": "Phone", "price": Decimal("499.99"), "stock": 25},
            {"name": "Headphones", "price": Decimal("79.99"), "stock": 50},
        ]

        products = []
        for data in products_data:
            product, _ = Product.objects.get_or_create(**data)
            products.append(product)

        # Orders
        for _ in range(5):
            customer = random.choice(customers)
            selected_products = random.sample(products, k=2)
            order = Order.objects.create(
                customer=customer,
                order_date=datetime.now()
            )
            order.products.set(selected_products)
            order.total_amount = sum([p.price for p in selected_products])
            order.save()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

