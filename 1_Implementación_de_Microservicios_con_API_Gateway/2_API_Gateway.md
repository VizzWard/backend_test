# API Gateway - Arquitectura y Decisiones

## Descripción General
El API Gateway actúa como punto de entrada único para la arquitectura de microservicios. Proporciona una interfaz unificada para los clientes y gestiona la autenticación centralizada.

## Funcionalidades Clave

### Enrutamiento (Routing)
- Redirección de solicitudes a los microservicios apropiados
- Mapeo de rutas externas a rutas internas de servicios
- Uso de expresiones regulares para capturar patrones de URL

### Autenticación Centralizada
- Gestión de tokens JWT
- Reenvío de credenciales al servicio de usuarios
- Propagación de tokens a servicios internos

### Proxying de Solicitudes
- Conservación de headers y parámetros entre servicios
- Manejo de errores y timeouts
- Transformación de respuestas para mantener consistencia

## Decisiones de Diseño

### Clase ServiceProxy
- Encapsula la lógica de comunicación entre servicios
- Proporciona manejo de errores consistente
- Facilita debugging mediante logs detallados

```python
def forward_request(service, path, request, **kwargs):
    service_url = settings.SERVICES.get(service.upper())
    url = f"{service_url}{path}"
    # Lógica para reenviar la solicitud...
```

### Permisos Dinámicos
- Lógica de permisos adaptable según el servicio y la acción
- Permite acceso público a endpoints específicos (registro, ver productos)
- Requiere autenticación para operaciones sensibles

### Vistas de Autenticación Personalizadas
- Reenvío de solicitudes de autenticación al servicio de usuarios
- Proporciona tokens válidos para toda la arquitectura
- Simplifica la experiencia del cliente

## Consideraciones para Producción

### Rendimiento y Escalabilidad
- Implementar caché de respuestas frecuentes
- Considerar soluciones dedicadas como Kong, Traefik o AWS API Gateway
- Configurar balanceo de carga para múltiples instancias

### Seguridad
- Implementar rate limiting para prevenir abusos
- Añadir validación de entradas y filtrado de respuestas
- Considerar HTTPS obligatorio para toda comunicación

### Monitoreo
- Mejorar logs para tracking de solicitudes entre servicios
- Implementar métricas de rendimiento y latencia
- Añadir sistema de alerta para fallos de servicios

### Mejoras Futuras
- Implementar circuit breaker para mayor resiliencia
- Añadir versionado de API
- Documentación automática de API (Swagger/OpenAPI)
- Implementar políticas de throttling por usuario/cliente