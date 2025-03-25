from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, Product
from .serializers import OrderSerializer
from .services import AuthenticationService, InventoryService

# Create your views here.
class OrderCreateAPIView(APIView):
    """
    API endpoint para crear nuevos pedidos.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthenticationService()
        self.inventory_service = InventoryService()

    def post(self, request, *args, **kwargs):
        """
        Crea un nuevo pedido verificando autenticación e inventario.
        """
        # Extraer datos del request
        user_id = request.data.get('user_id')
        items = request.data.get('items', [])

        # Verificar autenticación
        if not self.auth_service.is_authenticated(user_id):
            return Response(
                {"error": "Usuario no autenticado"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verificar disponibilidad de inventario
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)

            if not self.inventory_service.check_availability(product_id, quantity):
                return Response(
                    {"error": f"Inventario insuficiente para el producto {product_id}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Crear el pedido
        try:
            from django.db import transaction

            with transaction.atomic():
                order = Order.objects.create(user_id=user_id)

                for item in items:
                    product = Product.objects.get(id=item['product_id'])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item['quantity']
                    )

                # Serializar para la respuesta
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Error al crear el pedido: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )