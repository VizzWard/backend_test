# Implementación de Mocking en Tests de APIView

En este documento, explicaré detalladamente cómo se implementa el mocking en los tests de una APIView de Django REST Framework, analizando diferentes enfoques y las consideraciones técnicas importantes.

## Contexto del Ejemplo

Tenemos una APIView (`OrderCreateAPIView`) que depende de servicios externos:
- Un servicio de autenticación que verifica si un usuario está autenticado
- Un servicio de inventario que verifica disponibilidad de productos

Estos servicios realizan llamadas HTTP a APIs externas, por lo que necesitamos mockearlos para nuestras pruebas.

## Desafíos Específicos al Probar APIViews

Probar una APIView presenta desafíos particulares:

1. **Integración con middleware de Django**: Las vistas pasan por el sistema de middleware
2. **Ciclo de vida complejo**: Instanciación, dispatch, manejo de request/response
3. **Múltiples dependencias**: Autenticación, permisos, validación, serialización
4. **Servicios externos**: Llamadas a APIs o bases de datos externas

## Técnicas de Mocking Implementadas

### 1. Mocking de Bibliotecas HTTP (requests.get)

```python
@patch('requests.get')
def test_create_order_success(self, mock_get):
    # Configurar respuestas simuladas
    def mock_response(*args, **kwargs):
        mock_resp = Mock()
        mock_resp.status_code = 200
        
        if 'auth-status' in args[0]:
            mock_resp.json.return_value = {'is_authenticated': True}
        elif 'availability' in args[0]:
            mock_resp.json.return_value = {'available': True}
        
        return mock_resp
    
    mock_get.side_effect = mock_response
    
    # Hacer la petición al endpoint
    response = self.client.post(self.url, self.valid_payload, format='json')
    
    # Verificar resultado
    self.assertEqual(response.status_code, 201)
```

**Detalles de implementación:**
- Usamos el decorador `@patch('requests.get')` para interceptar todas las llamadas a `requests.get`
- Creamos una función `mock_response` que devuelve diferentes respuestas según la URL
- Asignamos esta función como `side_effect` del mock para manejar múltiples llamadas
- La función verifica qué parte de la URL contiene ('auth-status' o 'availability') para determinar qué tipo de respuesta devolver
- Luego construimos un objeto de respuesta mock con el código de estado y JSON adecuados

**¿Por qué funciona?**
- Django instancia nuestra vista cuando llega una petición
- La vista crea instancias de los servicios
- Los servicios llaman a `requests.get`, que ha sido reemplazado por nuestro mock
- Nuestro mock devuelve las respuestas predefinidas, simulando APIs externas

### 2. Mocking de Métodos de Servicio

```python
@patch('products.services.AuthenticationService.is_authenticated')
@patch('products.services.InventoryService.check_availability')
def test_create_order_success_with_service_mocks(self, mock_check_availability, mock_is_authenticated):
    # Configurar comportamiento
    mock_is_authenticated.return_value = True
    mock_check_availability.return_value = True
    
    # Hacer la petición al endpoint
    response = self.client.post(self.url, self.valid_payload, format='json')
    
    # Verificar resultado
    self.assertEqual(response.status_code, 201)
    mock_is_authenticated.assert_called_once_with(1)
    mock_check_availability.assert_called_once_with(self.product.id, 2)
```

**Detalles de implementación:**
- En lugar de mockear la biblioteca HTTP, mockeamos directamente los métodos de los servicios
- Usamos `@patch` con la ruta completa a cada método (`products.services.AuthenticationService.is_authenticated`)
- Configuramos valores de retorno fijos (True) para ambos métodos
- Verificamos que los métodos fueron llamados con los argumentos correctos

**¿Por qué funciona?**
- Cuando la vista instancia los servicios, obtiene las clases reales
- Pero los métodos específicos que hacen el trabajo real han sido reemplazados por nuestros mocks
- Esto evita las llamadas HTTP reales mientras mantiene el resto de la lógica intacta

**Nota sobre el orden de decoradores:**
- Los decoradores se aplican de abajo hacia arriba
- Los mocks se pasan como argumentos de derecha a izquierda
- Por eso `mock_check_availability` corresponde al segundo decorador, y `mock_is_authenticated` al primero

### 3. Mocking de Clases de Servicio Completas (Versión Corregida)

```python
def test_create_order_with_simple_mocks(self):
    # Primero, crear los parches
    original_auth_service = patch('products.views.AuthenticationService')
    original_inventory_service = patch('products.views.InventoryService')
    
    # Aplicar los parches
    mock_auth_service = original_auth_service.start()
    mock_inventory_service = original_inventory_service.start()
    
    try:
        # Configurar instancias mock
        mock_auth_instance = Mock()
        mock_inventory_instance = Mock()
        
        # Configurar constructores
        mock_auth_service.return_value = mock_auth_instance
        mock_inventory_service.return_value = mock_inventory_instance
        
        # Configurar métodos
        mock_auth_instance.is_authenticated.return_value = True
        mock_inventory_instance.check_availability.return_value = True
        
        # Hacer la petición
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        # Verificar resultado
        self.assertEqual(response.status_code, 201)
        mock_auth_instance.is_authenticated.assert_called_once_with(1)
        mock_inventory_instance.check_availability.assert_called_once_with(self.product.id, 2)
    
    finally:
        # Detener los parches
        original_auth_service.stop()
        original_inventory_service.stop()
```

**Detalles de implementación:**
- Creamos parches para las clases completas tal como son importadas en la vista (`products.views.AuthenticationService`)
- Usamos `start()` y `stop()` en lugar de context managers para mayor control
- Creamos instancias mock separadas para devolver cuando se instancien las clases
- Configuramos el comportamiento de los métodos en estas instancias mock
- Usamos un bloque `try/finally` para asegurar que los parches siempre se detengan

**¿Por qué funciona y por qué falló originalmente?**
- La vista importa las clases con `from .services import AuthenticationService, InventoryService`
- Esto significa que debemos hacer patch donde la vista usa las clases (`products.views`) no donde están definidas (`products.services`)
- En el test original, hacíamos patch en el lugar equivocado, por lo que las llamadas reales seguían sucediendo

## Punto Crítico: Ubicación del Patch

El error más común al mockear en Django es hacer patch en el lugar equivocado. Para entender esto, necesitamos comprender cómo funciona la importación en Python:

```python
# En views.py
from .services import AuthenticationService, InventoryService

# Esto es equivalente a:
import products.services
AuthenticationService = products.services.AuthenticationService
InventoryService = products.services.InventoryService
```

Una vez importado, el módulo que usa las clases (views.py) tiene sus propias referencias a esas clases. Por lo tanto:

- **Incorrecto**: `@patch('products.services.AuthenticationService')`
  - Esto reemplaza la clase en su definición original, pero no afecta a las referencias ya importadas

- **Correcto**: `@patch('products.views.AuthenticationService')`
  - Esto reemplaza la clase en el módulo donde se está usando realmente

## Ventajas de cada Enfoque

1. **Mocking de requests.get**:
   - Más cercano a probar la funcionalidad real
   - Prueba la integración con la biblioteca HTTP
   - Útil si la lógica de servicio es compleja

2. **Mocking de métodos de servicio**:
   - Más simple y directo
   - Menos propenso a errores
   - Enfocado en comportamiento, no implementación
   - Mejor para probar escenarios específicos

3. **Mocking de clases completas**:
   - Mayor control sobre todo el proceso
   - Útil cuando hay lógica en el constructor
   - Necesario cuando la vista instancia servicios directamente

## Mejores Prácticas y Lecciones Aprendidas

1. **Patch en el punto de uso**: Siempre hacer patch donde se usa la clase/función, no donde se define
2. **Usar bloques try/finally**: Garantizar que los parches se detengan para no afectar otros tests
3. **Verificar llamadas**: No solo comprobar resultados, sino también cómo se usaron los mocks
4. **Ser explícito**: Configurar claramente el comportamiento esperado de los mocks
5. **Considerar la inyección de dependencias**: Diseñar clases para facilitar el testing:

```python
class OrderCreateAPIView(APIView):
    def __init__(self, auth_service=None, inventory_service=None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service or AuthenticationService()
        self.inventory_service = inventory_service or InventoryService()
```

Este diseño permite pruebas más simples sin necesidad de patch:

```python
def test_with_dependency_injection(self):
    mock_auth = Mock()
    mock_inventory = Mock()
    
    mock_auth.is_authenticated.return_value = True
    mock_inventory.check_availability.return_value = True
    
    view = OrderCreateAPIView(
        auth_service=mock_auth,
        inventory_service=mock_inventory
    )
    
    # Configurar y enviar la petición directamente a la vista
    factory = APIRequestFactory()
    request = factory.post('/orders/', self.valid_payload, format='json')
    response = view.dispatch(request)
    
    self.assertEqual(response.status_code, 201)
```
