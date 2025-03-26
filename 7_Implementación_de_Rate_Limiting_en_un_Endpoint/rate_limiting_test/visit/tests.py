from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import time

# Create your tests here.
class RateLimitingTestCase(TestCase):
    def setUp(self):
        # Crear un usuario para las pruebas
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()

        # Para una mejor visualización en la terminal
        print("\n" + "=" * 70)
        print(f"INICIANDO TEST: {self._testMethodName}")
        print("=" * 70)

    def tearDown(self):
        # Para una mejor visualización en la terminal
        print("\n" + "-" * 70)
        print(f"FINALIZADO TEST: {self._testMethodName}")
        print("-" * 70 + "\n")

    def test_anonymous_rate_limiting(self):
        """Probar rate limiting para usuarios anónimos."""
        url = reverse('register-visit')
        print("\nPrueba de rate limiting para usuarios anónimos:")
        print("Límite configurado: 5 peticiones por minuto\n")

        # Realizamos 6 solicitudes (superando el límite de 5)
        responses = []
        for i in range(6):
            response = self.client.get(url)
            status_code = response.status_code
            responses.append(status_code)

            # Mejorar la visibilidad de los resultados
            if status_code == status.HTTP_200_OK:
                result = "ÉXITO"
            else:
                result = f"BLOQUEADO ({status_code})"

            print(f"Petición #{i + 1}: {result}")
            if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                print(f"  - Mensaje: {response.data['detail']}")

            # Pequeña pausa para mejor visualización en consola
            time.sleep(0.1)

        # Verificamos que las primeras 5 sean exitosas y la última sea 429 (Too Many Requests)
        self.assertEqual(responses[:5], [status.HTTP_200_OK] * 5)
        self.assertEqual(responses[5], status.HTTP_429_TOO_MANY_REQUESTS)

        print("\nResultado del test: ", end="")
        if responses[:5] == [status.HTTP_200_OK] * 5 and responses[5] == status.HTTP_429_TOO_MANY_REQUESTS:
            print("✅ CORRECTO - El rate limiting funciona como se esperaba")
        else:
            print("❌ INCORRECTO - El rate limiting no funciona como debería")

    def test_authenticated_rate_limiting(self):
        """Probar rate limiting para usuarios autenticados."""
        self.client.login(username='testuser', password='testpassword')
        url = reverse('register-visit')

        print("\nPrueba de rate limiting para usuarios autenticados:")
        print(f"Usuario: {self.user.username}")
        print("Límite configurado: 10 peticiones por minuto\n")

        # Realizamos 11 solicitudes (superando el límite de 10)
        responses = []
        for i in range(11):
            response = self.client.get(url)
            status_code = response.status_code
            responses.append(status_code)

            # Mejorar la visibilidad de los resultados
            if status_code == status.HTTP_200_OK:
                result = "ÉXITO"
            else:
                result = f"BLOQUEADO ({status_code})"

            print(f"Petición #{i + 1}: {result}")
            if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                print(f"  - Mensaje: {response.data['detail']}")

            # Pequeña pausa para mejor visualización en consola
            time.sleep(0.1)

        # Verificamos que las primeras 10 sean exitosas y la última sea 429 (Too Many Requests)
        self.assertEqual(responses[:10], [status.HTTP_200_OK] * 10)
        self.assertEqual(responses[10], status.HTTP_429_TOO_MANY_REQUESTS)

        print("\nResultado del test: ", end="")
        if responses[:10] == [status.HTTP_200_OK] * 10 and responses[10] == status.HTTP_429_TOO_MANY_REQUESTS:
            print("✅ CORRECTO - El rate limiting funciona como se esperaba")
        else:
            print("❌ INCORRECTO - El rate limiting no funciona como debería")