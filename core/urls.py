from django.urls import path
from .views import product_list_api, order_list_api

urlpatterns = [
    path('api/products/', product_list_api, name='product-list-api'),
    path('api/orders/', order_list_api, name='order-list-api'), # Naya orders ka route
]