import requests
from django.conf import settings


class AuthenticationService:
    """
    Servicio que realiza la autenticación mediante una API externa.
    """

    def __init__(self):
        self.api_url = getattr(settings, 'AUTH_API_URL', 'https://api.example.com/auth')
        self.api_key = getattr(settings, 'AUTH_API_KEY', 'default_key')

    def is_authenticated(self, user_id):
        """
        Verifica si un usuario está autenticado mediante una API externa.
        """
        try:
            response = requests.get(
                f"{self.api_url}/users/{user_id}/auth-status",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('is_authenticated', False)
            return False

        except Exception as e:
            # Log error
            print(f"Error en la autenticación: {str(e)}")
            return False


class InventoryService:
    """
    Servicio que verifica el inventario mediante una API externa.
    """

    def __init__(self):
        self.api_url = getattr(settings, 'INVENTORY_API_URL', 'https://api.example.com/inventory')
        self.api_key = getattr(settings, 'INVENTORY_API_KEY', 'default_key')

    def check_availability(self, product_id, quantity):
        """
        Verifica si hay suficiente inventario para un producto.
        """
        try:
            response = requests.get(
                f"{self.api_url}/products/{product_id}/availability",
                params={"quantity": quantity},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('available', False)
            return False

        except Exception as e:
            # Log error
            print(f"Error al verificar inventario: {str(e)}")
            return False