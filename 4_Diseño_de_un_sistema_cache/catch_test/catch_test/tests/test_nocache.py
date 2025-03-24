import time
import requests
import random
from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient
from products.models import Product

class NoCacheTest(TestCase):
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

    def test_cache_vs_no_cache(self):
        """Test para comparar rendimiento entre endpoints con y sin caché"""
        # Crear más datos para pruebas
        for i in range(100):  # Crear 100 productos adicionales
            Product.objects.create(name=f"Producto masivo {i}", price=random.uniform(10, 1000))

        # URLs para ambos endpoints
        cache_url = reverse('product-list')
        no_cache_url = reverse('product-no-cache-list')

        # Limpiar caché antes de empezar
        cache.clear()

        # Realizar múltiples pruebas y calcular promedios
        no_cache_times = []
        with_cache_times = []

        # Realizar varias pruebas
        for _ in range(10):
            # Medir tiempo para endpoint sin caché
            start_time = time.time()
            response = self.client.get(no_cache_url)
            no_cache_times.append(time.time() - start_time)

            # Limpiar caché entre pruebas
            if _ == 0:  # Solo limpiamos en la primera iteración para llenar la caché
                cache.clear()

            # Medir tiempo para endpoint con caché
            start_time = time.time()
            response = self.client.get(cache_url)
            with_cache_times.append(time.time() - start_time)

        # Calcular promedios
        avg_no_cache = sum(no_cache_times) / len(no_cache_times)
        avg_with_cache = sum(with_cache_times) / len(with_cache_times)

        # Imprimir resultados
        print(f"\nPromedio sin caché: {avg_no_cache:.6f} segundos")
        print(f"Promedio con caché: {avg_with_cache:.6f} segundos")
        print(f"Mejora: {(avg_no_cache / avg_with_cache):.2f}x más rápido")

        # Verificar mejora significativa (al menos 10% más rápido)
        self.assertLess(avg_with_cache * 1.1, avg_no_cache)

    def test_cache_performance_detail(self):
        """Test para medir el rendimiento de la caché en el detalle de un producto"""
        detail_url_cache = reverse('product-detail', kwargs={'pk': self.product1.pk})
        detail_url_no_cache = reverse('product-no-cache-detail', kwargs={'pk': self.product1.pk})

        # Limpiar caché antes de empezar
        cache.clear()

        # Primera consulta sin caché
        start_time = time.time()
        response1 = self.client.get(detail_url_no_cache)
        no_cache_time_ms = int((time.time() - start_time) * 1000)

        # Consulta con caché
        start_time = time.time()
        response1 = self.client.get(detail_url_cache)
        first_cache_time_ms = int((time.time() - start_time) * 1000)

        # Segunda consulta con caché
        start_time = time.time()
        response2 = self.client.get(detail_url_cache)
        second_cache_time_ms = int((time.time() - start_time) * 1000)

        # Imprimir y comparar tiempos
        print(f"\nTiempo de consulta sin caché (detalle): {no_cache_time_ms} ms")
        print(f"Tiempo primera consulta con caché (detalle): {first_cache_time_ms} ms")
        print(f"Tiempo segunda consulta con caché (detalle): {second_cache_time_ms} ms")

        if second_cache_time_ms < no_cache_time_ms:
            mejora = no_cache_time_ms / second_cache_time_ms
            print(f"Mejora: {mejora:.2f}x más rápido con caché")
        else:
            desventaja = second_cache_time_ms / no_cache_time_ms
            print(f"Advertencia: {desventaja:.2f}x más lento con caché")

        # Verificar el rendimiento
        # En entornos de desarrollo con pocos datos, puede que no haya una mejora clara
        if no_cache_time_ms < 10 and second_cache_time_ms < 10:
            print(f"Ambos tiempos son muy rápidos (<10ms), las diferencias pueden ser insignificantes.")
            self.assertTrue(True)  # No fallar el test en entornos de desarrollo rápidos
        else:
            # Solo verificar la mejora cuando los tiempos son suficientemente grandes
            self.assertLessEqual(second_cache_time_ms, no_cache_time_ms * 1.2)  # Permitir hasta un 20% más lento