# Servicio de Productos - Arquitectura y Decisiones

## Descripción General
El Servicio de Productos gestiona el catálogo de productos y sus categorías. Permite crear, listar, actualizar y eliminar productos, así como organizar productos en categorías.

## Estructura de Datos

### Modelos
- **Categoría**: Agrupación lógica de productos
- **Producto**: Artículos disponibles para compra con detalles como precio y stock

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
```

## Decisiones de Diseño

### Persistencia de Categorías
- Modelo separado para categorías permite mejor organización y filtrado
- La relación ForeignKey facilita las consultas de productos por categoría

### Permisos READ/WRITE
- **IsAuthenticatedOrReadOnly**: Cualquiera puede ver productos, solo usuarios autenticados pueden modificarlos
- Balance entre accesibilidad del catálogo y protección contra modificaciones no autorizadas

### Búsqueda y Filtrado
- Implementación de búsqueda por categoría mediante query parameters
- Personalización de `get_queryset()` para soportar filtros dinámicos

### Timestamps Automáticos
- Campos `fecha_creacion` y `fecha_actualizacion` con valores automáticos
- Facilita auditoría y seguimiento de cambios sin código adicional

## Consideraciones para Producción

### Rendimiento
- Implementar caché para productos frecuentemente accedidos
- Considerar paginación para catálogos grandes
- Indexar campos de búsqueda frecuente para optimizar consultas

### Imágenes y Archivos
- En una implementación completa, añadir soporte para imágenes de productos
- Considerar almacenamiento en CDN para archivos multimedia

### Mejoras Futuras
- Implementar búsqueda full-text
- Añadir soporte para variantes de productos (tallas, colores)
- Sistema de inventario más avanzado con alertas de stock bajo