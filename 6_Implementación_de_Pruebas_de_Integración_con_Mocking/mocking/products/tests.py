# tests.py para un endpoint
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch, Mock
from .models import Product


class OrderEndpointTest(TestCase):
    def setUp(self):
        # Cliente API para hacer peticiones
        self.client = APIClient()

        # URL del endpoint
        self.url = reverse('order-create')

        # Crear un producto de prueba
        self.product = Product.objects.create(
            name='Producto de prueba',
            price=100.00
        )

        # Datos para el pedido
        self.valid_payload = {
            'user_id': 1,
            'items': [
                {'product_id': self.product.id, 'quantity': 2}
            ]
        }

    # Método 1: Usando patch para mockear las llamadas a requests.get
    @patch('requests.get')
    def test_create_order_success(self, mock_get):
        """
        Prueba la creación exitosa de un pedido cuando el usuario está autenticado
        y hay inventario disponible.
        """

        # Configurar las respuestas simuladas para las diferentes llamadas a requests.get
        # Simulamos dos tipos de respuestas para las diferentes URLs
        def mock_response(*args, **kwargs):
            mock_resp = Mock()
            mock_resp.status_code = 200

            # Verificar qué API estamos llamando basándonos en la URL
            if 'auth-status' in args[0]:
                # Respuesta del servicio de autenticación
                mock_resp.json.return_value = {'is_authenticated': True}
            elif 'availability' in args[0]:
                # Respuesta del servicio de inventario
                mock_resp.json.return_value = {'available': True}

            return mock_resp

        # Asignar la función mock como side_effect
        mock_get.side_effect = mock_response

        # Hacer la petición al endpoint
        response = self.client.post(self.url, self.valid_payload, format='json')

        # Verificar que la petición fue exitosa
        self.assertEqual(response.status_code, 201)

        # Verificar que se llamaron ambos servicios
        self.assertEqual(mock_get.call_count, 2)

    # Método 2: Usando patch para mockear servicios completos
    @patch('products.services.AuthenticationService.is_authenticated')
    @patch('products.services.InventoryService.check_availability')
    def test_create_order_success_with_service_mocks(self, mock_check_availability, mock_is_authenticated):
        """
        Prueba la creación exitosa de un pedido mockeando directamente los métodos de servicio.
        """
        # Configurar los mocks para devolver valores predefinidos
        mock_is_authenticated.return_value = True
        mock_check_availability.return_value = True

        # Hacer la petición al endpoint
        response = self.client.post(self.url, self.valid_payload, format='json')

        # Verificar que la petición fue exitosa
        self.assertEqual(response.status_code, 201)

        # Verificar que los mocks fueron llamados correctamente
        mock_is_authenticated.assert_called_once_with(1)
        mock_check_availability.assert_called_once_with(self.product.id, 2)

    @patch('products.services.AuthenticationService.is_authenticated')
    def test_create_order_unauthenticated(self, mock_is_authenticated):
        """
        Prueba que el endpoint rechaza un pedido cuando el usuario no está autenticado.
        """
        # Configurar el mock para simular usuario no autenticado
        mock_is_authenticated.return_value = False

        # Hacer la petición al endpoint
        response = self.client.post(self.url, self.valid_payload, format='json')

        # Verificar que la petición fue rechazada con 401 Unauthorized
        self.assertEqual(response.status_code, 401)

        # Verificar que solo se llamó al servicio de autenticación
        mock_is_authenticated.assert_called_once_with(1)

    @patch('products.services.AuthenticationService.is_authenticated')
    @patch('products.services.InventoryService.check_availability')
    def test_create_order_insufficient_inventory(self, mock_check_availability, mock_is_authenticated):
        """
        Prueba que el endpoint rechaza un pedido cuando no hay suficiente inventario.
        """
        # Configurar los mocks
        mock_is_authenticated.return_value = True
        mock_check_availability.return_value = False  # No hay inventario

        # Hacer la petición al endpoint
        response = self.client.post(self.url, self.valid_payload, format='json')

        # Verificar que la petición fue rechazada con 400 Bad Request
        self.assertEqual(response.status_code, 400)

        # Verificar que los mocks fueron llamados correctamente
        mock_is_authenticated.assert_called_once_with(1)
        mock_check_availability.assert_called_once_with(self.product.id, 2)

    # Método 3: Usando Mock sin spec para simular respuestas de servicio
    def test_create_order_with_simple_mocks(self):
        """
        Prueba usando mocks simples sin spec.
        """
        # Primero, guarda las clases originales
        original_auth_service = patch('products.views.AuthenticationService')
        original_inventory_service = patch('products.views.InventoryService')

        # Aplica los parches
        mock_auth_service = original_auth_service.start()
        mock_inventory_service = original_inventory_service.start()

        try:
            # Configurar las instancias mock
            mock_auth_instance = Mock()
            mock_inventory_instance = Mock()

            # Configurar los retornos de los constructores
            mock_auth_service.return_value = mock_auth_instance
            mock_inventory_service.return_value = mock_inventory_instance

            # Configurar el comportamiento de los métodos
            mock_auth_instance.is_authenticated.return_value = True
            mock_inventory_instance.check_availability.return_value = True

            # Hacer la petición al endpoint
            response = self.client.post(self.url, self.valid_payload, format='json')

            # Verificar que la petición fue exitosa
            self.assertEqual(response.status_code, 201)

            # Verificar llamadas a los mocks
            mock_auth_instance.is_authenticated.assert_called_once_with(1)
            mock_inventory_instance.check_availability.assert_called_once_with(self.product.id, 2)

        finally:
            # Detener los parches pase lo que pase
            original_auth_service.stop()
            original_inventory_service.stop()