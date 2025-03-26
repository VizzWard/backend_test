import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class UsuariosService:
    @staticmethod
    def get_user(user_id, token):
        """Obtiene información de un usuario desde el servicio de usuarios"""
        url = f"{settings.USUARIOS_SERVICE_URL}usuarios/{user_id}/"
        headers = {'Authorization': f'Bearer {token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Lanza excepción si hay error
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al comunicarse con el servicio de usuarios: {str(e)}")
            return None

    @staticmethod
    def verify_user_exists(user_id, token):
        """Verifica si un usuario existe en el servicio de usuarios"""
        user_data = UsuariosService.get_user(user_id, token)
        return user_data is not None


class ProductosService:
    @staticmethod
    def get_product(product_id, token):
        """Obtiene información de un producto desde el servicio de productos"""
        url = f"{settings.PRODUCTOS_SERVICE_URL}productos/{product_id}/"
        headers = {'Authorization': f'Bearer {token}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al comunicarse con el servicio de productos: {str(e)}")
            return None

    @staticmethod
    def verify_product_exists(product_id, token):
        """Verifica si un producto existe en el servicio de productos"""
        product_data = ProductosService.get_product(product_id, token)
        return product_data is not None

    @staticmethod
    def verify_product_stock(product_id, quantity, token):
        """Verifica si hay suficiente stock de un producto"""
        product_data = ProductosService.get_product(product_id, token)

        if not product_data:
            return False

        return product_data.get('stock', 0) >= quantity

    @staticmethod
    def update_product_stock(product_id, quantity, token):
        """Actualiza el stock de un producto después de una compra"""
        product_data = ProductosService.get_product(product_id, token)

        if not product_data:
            return False

        current_stock = product_data.get('stock', 0)
        new_stock = current_stock - quantity

        if new_stock < 0:
            return False

        url = f"{settings.PRODUCTOS_SERVICE_URL}productos/{product_id}/"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = {'stock': new_stock}

        try:
            response = requests.patch(url, json=data, headers=headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Error al actualizar stock del producto {product_id}: {str(e)}")
            return False