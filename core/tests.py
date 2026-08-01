from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Product, Order, OrderItem


class ProductModelTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            title="Test Product", category="Test", price=100.00, stock_quantity=5
        )

    def test_string_representation(self):
        self.assertEqual(str(self.product), "Test Product")

    def test_in_stock_property_true(self):
        self.assertTrue(self.product.in_stock)

    def test_in_stock_property_false_when_zero(self):
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.in_stock)


class ProductApiTests(TestCase):
    def setUp(self):
        Product.objects.create(title="Item A", category="Cat", price=50, stock_quantity=10)
        Product.objects.create(title="Item B", category="Cat", price=75, stock_quantity=3)

    def test_product_list_returns_all_products(self):
        response = self.client.get(reverse('product-list-api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)


class OrderApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass1234')
        self.product = Product.objects.create(
            title="Item C", category="Cat", price=200, stock_quantity=5
        )
        self.order = Order.objects.create(
            user=self.user, total_amount=200, order_status='Pending'
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, quantity=1, price_at_purchase=200
        )

    def test_order_list_includes_nested_items(self):
        response = self.client.get(reverse('order-list-api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]['items']), 1)
        self.assertEqual(data[0]['items'][0]['product_title'], 'Item C')
