# Mocking en Pruebas

## ¿Qué es el mocking?

El mocking es una técnica utilizada en pruebas de software donde reemplazamos componentes reales (como bases de datos, APIs externas o servicios) con objetos simulados que imitan su comportamiento. Estos objetos simulados son conocidos como "mocks".

## ¿Por qué necesitamos mocking?

Cuando realizamos pruebas unitarias o de integración, queremos probar nuestro código de forma aislada, sin depender de servicios externos que podrían:

1. **Ser lentos**: Las API externas pueden tardar en responder.
2. **Ser impredecibles**: Pueden devolver respuestas diferentes cada vez.
3. **Requerir configuración adicional**: Como credenciales o conexiones.
4. **No estar disponibles**: Durante el desarrollo o en entornos de CI/CD.
5. **Tener costos asociados**: Algunas APIs cobran por petición.

## Tipos de objetos simulados

1. **Dummy objects**: Objetos que se pasan pero nunca se utilizan realmente.
2. **Fake objects**: Implementaciones simplificadas de objetos reales (ej. una base de datos en memoria).
3. **Stubs**: Proporcionan respuestas predefinidas a las llamadas.
4. **Spies**: Registran las llamadas que se hacen a ellos para verificarlas después.
5. **Mocks**: Objetos preprogramados con expectativas que forman una especificación de las llamadas que se espera que reciban.

## Ventajas del mocking

1. **Aislamiento**: Prueba solo el código que te interesa, no sus dependencias.
2. **Velocidad**: Las pruebas son más rápidas al eliminar dependencias lentas.
3. **Determinismo**: Siempre tendrás el mismo resultado bajo las mismas condiciones.
4. **Completitud**: Puedes probar escenarios difíciles de reproducir (como errores o límites).

## Desventajas del mocking

1. **Acoplamiento al código**: Las pruebas pueden estar demasiado ligadas a la implementación.
2. **Falsa confianza**: Puedes pasar pruebas con mocks pero fallar en producción.
3. **Mantenimiento**: Si la interfaz del objeto real cambia, debes actualizar los mocks.

## Herramientas de mocking en Python

1. **unittest.mock**: Biblioteca estándar de Python para mocking.
2. **pytest-mock**: Plugin de pytest que facilita el uso de mocks.
3. **MagicMock**: Clase extendida de Mock que implementa muchos métodos mágicos.

## Conceptos clave en unittest.mock

1. **Mock**: Clase básica para crear objetos simulados.
2. **patch**: Decorador o context manager para reemplazar objetos en un módulo.
3. **return_value**: Define el valor que devuelve un método simulado.
4. **side_effect**: Define comportamientos más complejos (como excepciones).
5. **assert_called_with**: Verifica que el mock fue llamado con ciertos argumentos.

## Ejemplo básico

```python
from unittest.mock import Mock

# Crear un mock básico
mock_service = Mock()

# Configurar el comportamiento
mock_service.get_data.return_value = {"status": "success", "data": [1, 2, 3]}

# Usar el mock
result = mock_service.get_data()
print(result)  # {"status": "success", "data": [1, 2, 3]}

# Verificar cómo se usó
mock_service.get_data.assert_called_once()
```

## Mejores prácticas

1. **Usar spec**: Define la interfaz que debe tener el mock para evitar errores sutiles.
2. **Mockear a nivel de función o método**: Mejor que mockear módulos enteros.
3. **No mockear todo**: Algunas dependencias pueden ser reales en pruebas de integración.
4. **Verificar interacciones**: No solo el resultado, sino cómo se interactuó con el mock.
5. **Mantener mocks simples**: Evita lógica compleja en los mocks.