# Explicación: test_load.py

## Propósito General
Este archivo contiene pruebas diseñadas para simular una carga elevada de peticiones sobre los endpoints de la API de productos y evaluar cómo se comporta el sistema de caché bajo estas condiciones.

## Estructura del Archivo
El archivo define una clase `LoadTestCase` que hereda de `TestCase` de Django, con un método de prueba específico para simular múltiples consultas consecutivas.

## Configuración Inicial (setUp)
```python
def setUp(self):
    # Crear algunos productos de prueba
    for i in range(50):
        Product.objects.create(name=f"Producto {i}", price=10.99 + i)

    self.client = APIClient()
    self.list_url = reverse('product-list')

    # Limpiar la caché antes de empezar
    cache.clear()
```

Este método:
1. Crea 50 productos de prueba en la base de datos, con nombres numerados secuencialmente y precios que aumentan gradualmente
2. Configura un cliente de API para realizar las peticiones
3. Define la URL para acceder al listado de productos
4. Limpia la caché del sistema para asegurar que las pruebas comiencen con un estado conocido

## Test Principal: Múltiples Consultas Consecutivas
```python
def test_multiple_requests(self):
```

Este test simula una carga de trabajo mediante múltiples consultas consecutivas:

1. **Primera ronda de consultas (sin caché)**:
   - Realiza 10 peticiones GET consecutivas al endpoint de listado de productos
   - Mide el tiempo total que toman estas 10 peticiones
   - Verifica que cada respuesta tenga el código de estado HTTP 200 (éxito)
   - La primera petición llena la caché, pero las siguientes 9 también se benefician de ella

2. **Segunda ronda de consultas (con caché)**:
   - Realiza otras 10 peticiones GET consecutivas al mismo endpoint
   - Mide el tiempo total que toman estas 10 peticiones
   - Verifica que cada respuesta tenga el código de estado HTTP 200
   - En esta segunda ronda, todas las consultas deberían utilizar la caché creada durante la primera ronda

3. **Verificaciones y resultados**:
   - Imprime los tiempos totales de cada ronda de consultas
   - Calcula y muestra la mejora de rendimiento (cuántas veces más rápida es la segunda ronda)
   - Verifica mediante un assert que la segunda ronda sea efectivamente más rápida que la primera

## Diferencias con test_cache.py
A diferencia del archivo `test_cache.py` que se enfoca en medir el rendimiento de consultas individuales, este test:

1. **Crea más datos de prueba**: 50 productos en lugar de 3, lo que genera una carga mayor en la base de datos
2. **Simula carga**: Realiza múltiples consultas consecutivas (10 en cada ronda) para simular un entorno más cercano a la producción con múltiples usuarios
3. **Mide rendimiento acumulado**: Evalúa el tiempo total de múltiples consultas, no solo de consultas individuales

## Objetivo de la Prueba
Esta prueba está diseñada para:

1. **Evaluar escalabilidad**: Comprobar cómo se comporta el sistema bajo una carga similar a la de un entorno de producción
2. **Verificar persistencia de caché**: Confirmar que la caché persiste correctamente entre múltiples consultas
3. **Cuantificar beneficios a escala**: Medir la mejora de rendimiento cuando múltiples peticiones aprovechan el mismo conjunto de datos cacheados

## Interpretación de Resultados
- Si la prueba pasa, significa que el sistema de caché mantiene su eficacia incluso bajo una carga más elevada
- La diferencia de tiempo entre la primera y segunda ronda indica el impacto potencial que tendría la implementación de caché en un entorno de producción con múltiples usuarios
- Cuanto mayor sea la relación entre los tiempos (el valor "más rápido"), más efectivo es el sistema de caché para mitigar la carga del servidor