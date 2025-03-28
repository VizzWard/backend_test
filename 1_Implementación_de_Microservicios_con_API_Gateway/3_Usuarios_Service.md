# Servicio de Usuarios - Arquitectura y Decisiones

## Descripción General
El Servicio de Usuarios gestiona la autenticación y los datos de usuario en la arquitectura de microservicios. Es responsable de registrar usuarios, autenticarlos y proporcionar información de perfil.

## Estructura de Datos

### Modelo de Usuario
- Extiende `AbstractUser` de Django para aprovechar la funcionalidad de autenticación incorporada
- Añade campos adicionales como teléfono y dirección
- Usa `related_name` personalizados para evitar conflictos con el modelo de usuario predeterminado

```python
class Usuario(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
```

## Decisiones de Diseño

### Extender AbstractUser en lugar de crear un modelo personalizado
- **Ventajas**: Aprovecha el sistema de autenticación de Django
- **Consideraciones**: Requiere configurar `AUTH_USER_MODEL` en settings.py

### Uso de Django REST Framework y JWT
- Proporciona un sistema de autenticación basado en tokens seguro
- Gestiona la caducidad de sesión y renovación de tokens
- Permite escalar horizontalmente sin compartir estado

### API Independiente
- Cada ruta tiene sus propios permisos
- Registro sin autenticación, pero acceso a datos protegido
- Endpoint `/me/` para que los usuarios accedan a su propia información

## Consideraciones para Producción

### Seguridad
- En producción, implementar validación adicional para registro
- Considerar añadir autenticación de dos factores
- Implementar rate limiting para prevenir ataques de fuerza bruta

### Escalabilidad
- El servicio puede escalar horizontalmente al ser stateless
- Considerar caché distribuida para tokens frecuentemente usados

### Mejoras Futuras
- Implementar recuperación de contraseña
- Añadir roles y permisos más granulares
- Soporte para autenticación con proveedores externos (OAuth)