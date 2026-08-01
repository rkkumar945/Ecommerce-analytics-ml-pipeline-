from django.contrib import admin
from .models import Product, Order, OrderItem

# Admin screen par products ko sahi se dekhne ke liye
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'stock_quantity', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'category')

# Admin screen par orders ko manage karne ke liye
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'order_status', 'created_at')
    list_filter = ('order_status',)