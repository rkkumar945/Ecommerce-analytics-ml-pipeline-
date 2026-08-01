"""
Custom management command to populate the database with sample data.

Ise banane ki wajah: analytics.py ko test karne ke liye har baar
manually admin panel se products/orders add karna time-waste tha,
isliye ek chhota seed script bana diya. Run karne ke liye:

    python manage.py seed_sample_data

--clear flag pass karoge to purana data delete karke fresh seed hoga.
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Product, Order, OrderItem


SAMPLE_PRODUCTS = [
    ("Wireless Mechanical Keyboard", "Electronics", 3499.00, 25),
    ("Noise Cancelling Headphones", "Electronics", 6999.00, 12),
    ("Stainless Steel Water Bottle", "Home & Kitchen", 499.00, 80),
    ("Running Shoes - Size 9", "Footwear", 2799.00, 30),
    ("Yoga Mat (6mm)", "Fitness", 899.00, 45),
    ("Bluetooth Portable Speaker", "Electronics", 2199.00, 18),
    ("Office Chair - Ergonomic", "Furniture", 8999.00, 7),
    ("Ceramic Coffee Mug Set", "Home & Kitchen", 649.00, 60),
]


class Command(BaseCommand):
    help = "Seeds the database with sample products, a demo user, and a few orders."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing Product/Order data before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing product/order data cleared.'))

        # 1. Products
        created_products = []
        for title, category, price, stock in SAMPLE_PRODUCTS:
            product, created = Product.objects.get_or_create(
                title=title,
                defaults={'category': category, 'price': price, 'stock_quantity': stock},
            )
            created_products.append(product)

        self.stdout.write(self.style.SUCCESS(f'{len(created_products)} products ready.'))

        # 2. A demo user to attach orders to (only if one doesn't exist yet)
        demo_user, _ = User.objects.get_or_create(
            username='demo_customer',
            defaults={'email': 'demo@example.com'},
        )

        # 3. A couple of sample orders so /api/orders/ has something to show
        if not Order.objects.filter(user=demo_user).exists():
            for _ in range(3):
                order = Order.objects.create(
                    user=demo_user,
                    total_amount=0,
                    order_status=random.choice(['Pending', 'Completed']),
                )
                chosen = random.sample(created_products, k=2)
                running_total = 0
                for product in chosen:
                    qty = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price_at_purchase=product.price,
                    )
                    running_total += product.price * qty
                order.total_amount = running_total
                order.save()

            self.stdout.write(self.style.SUCCESS('Sample orders created for demo_customer.'))
        else:
            self.stdout.write('Demo orders already exist, skipping.')

        self.stdout.write(self.style.SUCCESS('Seeding complete. Try /api/products/ and /api/orders/.'))
