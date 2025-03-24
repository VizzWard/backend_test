from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, ProductViewSetNoCache

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'products-no-cache', ProductViewSetNoCache, basename='product-no-cache')

urlpatterns = [
    path('', include(router.urls)),
]
