# Implementación de Rate Limiting en Django Rest Framework

El rate limiting (limitación de tasa) es una técnica fundamental para proteger tus APIs de abusos, ataques de denegación de servicio (DoS) y uso excesivo de recursos. Este documento explica cómo se implementa el rate limiting en Django Rest Framework (DRF) usando el ejemplo básico proporcionado.

## Conceptos Básicos

El rate limiting consiste en limitar la cantidad de solicitudes que un cliente (usuario o dirección IP) puede hacer a tu API en un período de tiempo determinado. Por ejemplo, 10 solicitudes por minuto.

### Beneficios del Rate Limiting

1. **Protección contra abusos**: Evita que usuarios malintencionados sobrecarguen tu sistema.
2. **Equidad en el uso de recursos**: Asegura que ningún usuario consuma demasiados recursos del servidor.
3. **Mejor experiencia de usuario**: Mantiene el servicio disponible para todos los usuarios.
4. **Reducción de costos**: Minimiza el uso innecesario de recursos y ancho de banda.

## Implementación en Django Rest Framework

Django Rest Framework incluye un sistema integrado de throttling (estrangulamiento/limitación) que facilita la implementación del rate limiting. A continuación se explica cómo funciona cada parte del código:

### 1. Configuración en settings.py

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '10/minute',   # 10 solicitudes por minuto para usuarios autenticados
        'anon': '5/minute',    # 5 solicitudes por minuto para usuarios anónimos
    }
}
```

Esta configuración establece:
- Clases de throttling predeterminadas para diferentes tipos de usuarios
- Límites específicos para cada tipo de usuario
  - Usuarios autenticados: 10 solicitudes por minuto
  - Usuarios anónimos: 5 solicitudes por minuto

### 2. Clases de Throttling Personalizadas

```python
class VisitThrottle(UserRateThrottle):
    rate = '10/minute'  # Sobrescribe la configuración global para este endpoint específico
    scope = 'user'

class AnonVisitThrottle(AnonRateThrottle):
    rate = '5/minute'   # Para usuarios no autenticados
    scope = 'anon'
```

Estas clases personalizan el comportamiento del throttling:
- `VisitThrottle`: Hereda de `UserRateThrottle` y limita a los usuarios autenticados.
- `AnonVisitThrottle`: Hereda de `AnonRateThrottle` y limita a los usuarios anónimos.
- El atributo `scope` conecta estas clases con las tasas definidas en la configuración.

### 3. Aplicación del Throttling a una Vista

```python
class VisitView(APIView):
    throttle_classes = [VisitThrottle, AnonVisitThrottle]
    
    def get(self, request, format=None):
        # Lógica de la vista
        return Response({
            'message': 'Visita registrada correctamente',
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
```

Aquí:
- La vista `VisitView` utiliza las clases de throttling definidas anteriormente.
- El throttling se aplica automáticamente antes de que se ejecute el método `get`.
- Si un usuario excede su límite, DRF devuelve automáticamente un código de estado HTTP 429 (Too Many Requests).

## Cómo Funciona Internamente

1. **Identificación del usuario**: DRF identifica al usuario mediante su ID de usuario (si está autenticado) o su dirección IP (si es anónimo).

2. **Registro de solicitudes**: Cada vez que un usuario hace una solicitud, DRF la registra en caché con una marca de tiempo.

3. **Verificación de límites**: Antes de procesar una solicitud, DRF cuenta cuántas solicitudes ha hecho el usuario en el período actual (por ejemplo, el último minuto).

4. **Aplicación de límites**: Si el usuario ha excedido su límite, DRF rechaza la solicitud con un código 429 y un mensaje que indica cuándo podrá hacer la próxima solicitud.

5. **Respuesta al usuario**: Si la solicitud es aceptada, se procesa normalmente; si no, el usuario recibe el mensaje de error.

## Formatos de Tasa (Rate)

DRF permite especificar las tasas de límite en varios formatos:
- `'10/second'` - 10 solicitudes por segundo
- `'100/minute'` - 100 solicitudes por minuto
- `'1000/hour'` - 1000 solicitudes por hora
- `'10000/day'` - 10000 solicitudes por día

## Personalización Avanzada

Aunque no se muestra en el ejemplo básico, DRF permite personalizar aún más el comportamiento del throttling:

1. **Throttling basado en la acción**: Limitar diferentes tasas para diferentes métodos HTTP (GET, POST, etc.).

2. **Throttling por IP o rango de IPs**: Aplicar límites diferentes basados en el origen de la solicitud.

3. **Throttling basado en contenido**: Limitar según el contenido de la solicitud.

4. **Backends de almacenamiento alternativo**: Usar Redis u otras soluciones de almacenamiento en lugar de la caché predeterminada.
