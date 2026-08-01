from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


@api_view(['GET'])
def product_list_api(request):
    """
    Database se saare products nikal kar JSON format me deta hai.
    analytics.py isi tarah ka data seedha DB se (Pandas ke through)
    padhta hai, lekin yeh endpoint frontend/Postman testing ke liye hai.
    """
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def order_list_api(request):
    """
    Saare customer orders unke items ke saath return karta hai.
    Customer purchase behavior analyze karne ke liye useful hai.
    """
    orders = Order.objects.select_related('user').prefetch_related('items').all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
