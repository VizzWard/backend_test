import time
import requests
from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient
from products.models import Product

# Test de carga para simular múltiples consultas simultáneas
class LoadTestCase(TestCase):
    def setUp(self):
        # Crear algunos productos de prueba
        for i in range(50):
            Product.objects.create(name=f"Producto {i}", price=10.99 + i)

        self.client = APIClient()
        self.list_url = reverse('product-list')

        # Limpiar la caché antes de empezar
        cache.clear()

    def test_multiple_requests(self):
        """Test para simular múltiples consultas y medir el rendimiento de la caché"""
        # Primera ronda de consultas (sin caché)
        start_time = time.time()
        for _ in range(10):
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, 200)
        first_batch_time = time.time() - start_time

        # Segunda ronda de consultas (con caché)
        start_time = time.time()
        for _ in range(10):
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, 200)
        second_batch_time = time.time() - start_time

        # Imprimir y comparar tiempos
        print(f"\n10 consultas sin caché: {first_batch_time:.6f} segundos")
        print(f"10 consultas con caché: {second_batch_time:.6f} segundos")
        print(f"Mejora de rendimiento total: {(first_batch_time / second_batch_time):.2f}x más rápido")

        # Asegurar que la segunda ronda fue más rápida
        self.assertLess(second_batch_time, first_batch_time)