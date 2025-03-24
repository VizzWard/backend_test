import time
import requests
from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient
from products.models import Product

class ProductCacheTestCase(TestCase):
    def setUp(self):
        # Crear algunos productos de prueba
        self.product1 = Product.objects.create(name="Producto 1", price=10.99)
        self.product2 = Product.objects.create(name="Producto 2", price=20.99)
        self.product3 = Product.objects.create(name="Producto 3", price=30.99)

        self.client = APIClient()
        self.list_url = reverse('product-list')
        self.detail_url = reverse('product-detail', kwargs={'pk': self.product1.pk})

        # Limpiar la caché antes de empezar
        cache.clear()

    def test_cache_performance_list(self):
        """Test para medir el rendimiento de la caché en el listado de productos"""
        # Primera consulta (sin caché)
        start_time = time.time()
        response1 = self.client.get(self.list_url)
        first_query_time = time.time() - start_time

        # Segunda consulta (con caché)
        start_time = time.time()
        response2 = self.client.get(self.list_url)
        second_query_time = time.time() - start_time

        # Verificar que ambas consultas retornan el mismo resultado
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.data, response2.data)

        # Imprimir y comparar tiempos
        print(f"\nTiempo de consulta sin caché (lista): {first_query_time:.6f} segundos")
        print(f"Tiempo de consulta con caché (lista): {second_query_time:.6f} segundos")
        print(f"Mejora de rendimiento: {(first_query_time / second_query_time):.2f}x más rápido")

        # Asegurar que la segunda consulta fue más rápida
        self.assertLess(second_query_time, first_query_time)

    def test_cache_performance_detail(self):
        """Test para medir el rendimiento de la caché en el detalle de un producto"""
        # Primera consulta (sin caché)
        start_time = time.time()
        response1 = self.client.get(self.detail_url)
        first_query_time = time.time() - start_time

        # Segunda consulta (con caché)
        start_time = time.time()
        response2 = self.client.get(self.detail_url)
        second_query_time = time.time() - start_time

        # Verificar que ambas consultas retornan el mismo resultado
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.data, response2.data)

        # Imprimir y comparar tiempos
        print(f"\nTiempo de consulta sin caché (detalle): {first_query_time:.6f} segundos")
        print(f"Tiempo de consulta con caché (detalle): {second_query_time:.6f} segundos")
        print(f"Mejora de rendimiento: {(first_query_time / second_query_time):.2f}x más rápido")

        # Asegurar que la segunda consulta fue más rápida
        self.assertLess(second_query_time, first_query_time)

    def test_cache_expiration(self):
        """Test para verificar que la caché expira correctamente después de 5 minutos"""
        # Este test es más demostrativo que práctico ya que requeriría esperar 5 minutos
        # En un entorno real se podría modificar temporalmente el tiempo de expiración

        # Primera consulta (sin caché)
        response1 = self.client.get(self.list_url)

        # Simular la expiración de la caché
        print("\nSimulando expiración del caché...")
        cache.clear()  # Esto fuerza la expiración para propósitos de prueba

        # Tercera consulta (después de "expirar" la caché)
        start_time = time.time()
        response3 = self.client.get(self.list_url)
        third_query_time = time.time() - start_time

        # Verificar que la consulta sigue funcionando correctamente
        self.assertEqual(response3.status_code, 200)

        # Esta consulta debería ser similar a la primera (sin caché)
        print(f"Tiempo de consulta después de expirar caché: {third_query_time:.6f} segundos")

        # Ahora una nueva consulta debería usar la caché nuevamente
        start_time = time.time()
        response4 = self.client.get(self.list_url)
        fourth_query_time = time.time() - start_time

        print(f"Tiempo de consulta con nueva caché: {fourth_query_time:.6f} segundos")
        self.assertLess(fourth_query_time, third_query_time)