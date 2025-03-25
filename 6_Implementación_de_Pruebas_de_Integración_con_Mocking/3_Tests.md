# Pruebas de Integración

## ¿Qué son las pruebas de integración?

Las pruebas de integración verifican que diferentes módulos o servicios de una aplicación funcionan correctamente en conjunto. A diferencia de las pruebas unitarias que aíslan funciones individuales, las pruebas de integración evalúan cómo los componentes interactúan entre sí.

## Características de las pruebas de integración

1. **Alcance**: Prueban múltiples componentes o módulos a la vez.
2. **Complejidad**: Son más complejas que las pruebas unitarias.
3. **Velocidad**: Suelen ser más lentas que las pruebas unitarias.
4. **Recursos**: Pueden requerir más recursos (bases de datos, APIs, etc.).
5. **Realismo**: Se acercan más a cómo funciona la aplicación en producción.

## Tipos de pruebas de integración

1. **Top-down**: Se comienza probando los módulos de nivel superior y se va descendiendo.
2. **Bottom-up**: Se prueban primero los componentes más básicos y luego se integran.
3. **Big bang**: Se integran todos los componentes a la vez y se prueban en conjunto.
4. **Sandwich (Híbrido)**: Combinación de top-down y bottom-up.

## Desafíos de las pruebas de integración

1. **Dependencias externas**: APIs, bases de datos, servicios de terceros.
2. **Entorno de prueba**: Configurar un entorno adecuado puede ser difícil.
3. **Complejidad**: Más puntos de fallo y escenarios a probar.
4. **Determinismo**: Resultados que pueden variar en cada ejecución.
5. **Aislamiento de fallos**: Difícil identificar exactamente qué causó un fallo.

## Pruebas de integración en Django

Django facilita las pruebas de integración a través de:

1. **TestCase**: Clase base que proporciona una base de datos limpia para cada test.
2. **Client**: Permite simular peticiones HTTP para probar vistas.
3. **LiveServerTestCase**: Para pruebas que necesitan un servidor en funcionamiento (selenium).
4. **TransactionTestCase**: Para probar funcionalidades relacionadas con transacciones DB.

## Ejemplo básico en Django

```python
from django.test import TestCase, Client
from django.urls import reverse
from .models import Product

class ProductViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(name="Test Product", price=10.00)
        
    def test_product_list(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")
```

## Mocking en pruebas de integración

Aunque las pruebas de integración verifican cómo interactúan los componentes, a veces es necesario simular algunas dependencias:

1. **Servicios externos**: APIs de terceros, pasarelas de pago.
2. **Servicios costosos**: Operaciones que consumen muchos recursos.
3. **Servicios no disponibles**: En entornos de prueba o CI/CD.
4. **Escenarios difíciles**: Errores, casos límite, condiciones especiales.

## Mejores prácticas

1. **Aislar el contexto**: Cada prueba debe comenzar con un estado conocido.
2. **Datos de prueba representativos**: Usar datos que reflejen casos reales.
3. **Prueba happy path y edge cases**: Cubrir tanto el camino feliz como casos límite.
4. **Limitar el alcance**: No intentar probar demasiado en una sola prueba.
5. **Documentar propósito**: Cada prueba debe tener un propósito claro.
6. **Automatizar**: Integrar pruebas en CI/CD para ejecución automática.