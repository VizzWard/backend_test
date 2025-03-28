# Servicio de Órdenes - Arquitectura y Decisiones

## Descripción General
El Servicio de Órdenes gestiona la creación y seguimiento de pedidos. Integra información de usuarios y productos de otros servicios para crear órdenes completas con líneas de detalle.

## Estructura de Datos

### Modelos
- **Orden**: Pedido principal con información de usuario, dirección y estado
- **DetalleOrden**: Líneas individuales de productos en una orden

```python
class Orden(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('enviada', 'Enviada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    )
    
    usuario_id = models.IntegerField()  # Referencia al ID del usuario
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion_envio = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
```

## Decisiones de Diseño

### Referencias entre Servicios
- Uso de ID enteros en lugar de ForeignKey para referencias entre servicios
- Permite independencia de bases de datos manteniendo integridad referencial lógica

### Desnormalización Estratégica
- Guardar nombre y precio del producto en DetalleOrden
- Evita llamadas constantes al servicio de productos
- Preserva la información histórica aunque el producto cambie posteriormente

### Comunicación entre Servicios
- Implementación de servicios de comunicación (services.py)
- Verificación de existencia de usuario y disponibilidad de stock antes de crear órdenes
- Actualización de stock después de crear órdenes

### Cálculo del Lado del Servidor
- Total de orden calculado en el servidor y no confiando en datos del cliente
- El subtotal se calcula automáticamente en el modelo DetalleOrden

## Consideraciones para Producción

### Transacciones Distribuidas
- Implementar patrón Saga para transacciones distribuidas
- Considerar colas de mensajes (RabbitMQ, Kafka) para comunicación asíncrona
- Implementar compensación en caso de fallos parciales

### Consistencia Eventual
- El diseño actual favorece disponibilidad sobre consistencia inmediata
- Implementar procesos de reconciliación para manejar inconsistencias

### Mejoras Futuras
- Sistema de notificaciones para cambios de estado
- Implementar historial detallado de cambios de estado
- Integración con servicios de pago
- Añadir sistema de devoluciones