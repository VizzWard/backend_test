from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Product
from .serializer import ProductSerializer

# Create your views here.
class ProductViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ProductViewSetNoCache(viewsets.ModelViewSet):
    """
    Un ViewSet idéntico al ProductViewSet pero sin caché.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer