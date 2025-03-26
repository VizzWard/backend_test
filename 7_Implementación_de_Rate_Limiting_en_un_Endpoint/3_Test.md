# Explicación de los Tests para Rate Limiting en Django Rest Framework

Este documento explica en detalle los tests implementados para verificar el funcionamiento correcto del rate limiting en nuestra API. Los tests están diseñados para comprobar que los límites se aplican correctamente tanto para usuarios anónimos como para usuarios autenticados.

## Estructura General de los Tests

Los tests utilizan el framework de testing de Django, que extiende el módulo `unittest` de Python. La clase `RateLimitingTestCase` hereda de `django.test.TestCase` y contiene dos métodos de test principales, uno para usuarios anónimos y otro para usuarios autenticados.

```python
class RateLimitingTestCase(TestCase):
    def setUp(self):
        # Configuración inicial
        
    def tearDown(self):
        # Limpieza final
        
    def test_anonymous_rate_limiting(self):
        # Test para usuarios anónimos
        
    def test_authenticated_rate_limiting(self):
        # Test para usuarios autenticados
```

## Métodos de Configuración y Limpieza

### El método `setUp`

```python
def setUp(self):
    # Crear un usuario para las pruebas
    self.user = User.objects.create_user(
        username='testuser',
        password='testpassword'
    )
    self.client = APIClient()
    
    # Para una mejor visualización en la terminal
    print("\n" + "="*70)
    print(f"INICIANDO TEST: {self._testMethodName}")
    print("="*70)
```

Este método se ejecuta antes de cada test y realiza las siguientes tareas:

1. **Crear un usuario de prueba**: Crea un usuario llamado 'testuser' que utilizaremos para probar el rate limiting de usuarios autenticados.
2. **Inicializar el cliente API**: Crea una instancia de `APIClient` de DRF que usaremos para hacer solicitudes a nuestra API.
3. **Imprimir mensaje de inicio**: Muestra un encabezado en la terminal para indicar el inicio del test, mejorando la legibilidad de los resultados.

### El método `tearDown`

```python
def tearDown(self):
    # Para una mejor visualización en la terminal
    print("\n" + "-"*70)
    print(f"FINALIZADO TEST: {self._testMethodName}")
    print("-"*70 + "\n")
```

Este método se ejecuta después de cada test y simplemente imprime un mensaje de finalización para mejorar la legibilidad de los resultados en la terminal.

## Test para Usuarios Anónimos

```python
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
            
        print(f"Petición #{i+1}: {result}")
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
```

Este test verifica el comportamiento del rate limiting para usuarios anónimos (no autenticados). Veamos cómo funciona:

1. **Obtener la URL**: Utiliza `reverse('register-visit')` para obtener la URL del endpoint que queremos probar.

2. **Imprimir información**: Muestra información sobre la prueba que se va a realizar, incluyendo el límite configurado.

3. **Realizar solicitudes**: Hace 6 solicitudes GET consecutivas al endpoint. Según nuestra configuración, las primeras 5 deberían ser exitosas, pero la sexta debería ser rechazada.

4. **Registrar resultados**: Para cada solicitud:
   - Almacena el código de respuesta en la lista `responses`.
   - Imprime si la solicitud fue exitosa (código 200) o bloqueada (código 429).
   - Si fue bloqueada, muestra el mensaje de error que incluye cuándo estará disponible la próxima solicitud.

5. **Verificar resultados**: Utiliza las aserciones de testing para confirmar que:
   - Las primeras 5 solicitudes devolvieron código 200 (OK).
   - La sexta solicitud devolvió código 429 (Too Many Requests).

6. **Mostrar resultado final**: Imprime un mensaje indicando si el test pasó o falló.

## Test para Usuarios Autenticados

```python
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
            
        print(f"Petición #{i+1}: {result}")
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
```

Este test es similar al anterior, pero verifica el comportamiento para usuarios autenticados. Las diferencias clave son:

1. **Autenticación del usuario**: Utiliza `self.client.login()` para autenticar al usuario de prueba.

2. **Límite diferente**: Prueba el límite de 10 solicitudes por minuto (en lugar de 5) que hemos configurado para usuarios autenticados.

3. **11 solicitudes**: Realiza 11 solicitudes, esperando que las primeras 10 sean exitosas y la undécima sea rechazada.
