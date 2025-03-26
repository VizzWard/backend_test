from django.db import models

# Create your models here.
class Orden(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('enviada', 'Enviada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    )

    usuario_id = models.IntegerField()  # Referencia al ID del usuario en el servicio de usuarios
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion_envio = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Orden #{self.id} - Usuario {self.usuario_id}"

    class Meta:
        db_table = 'ordenes'


class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='detalles')
    producto_id = models.IntegerField()  # Referencia al ID del producto en el servicio de productos
    producto_nombre = models.CharField(
        max_length=200)  # Guardamos el nombre para evitar llamadas constantes al servicio de productos
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto_nombre}"

    class Meta:
        db_table = 'detalles_orden'