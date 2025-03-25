from django.db import models
from django.db import transaction
from django.db.models import F
from decimal import Decimal


class Cuenta(models.Model):
    numero_cuenta = models.CharField(max_length=20, unique=True)
    propietario = models.CharField(max_length=100)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cuenta {self.numero_cuenta} de {self.propietario}: ${self.saldo}"

    def depositar(self, cantidad):
        """
        Realiza un depósito utilizando F() para evitar condiciones de carrera.
        F() permite realizar operaciones a nivel de base de datos sin traer primero el valor al Python.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")

        # Usamos F() para actualizar el saldo a nivel de base de datos
        self.saldo = F('saldo') + cantidad
        self.save()
        # Refrescamos la instancia para obtener el saldo actualizado
        self.refresh_from_db()
        return self.saldo

    def retirar(self, cantidad):
        """
        Realiza un retiro utilizando transacción y bloqueo pesimista.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")

        # Usamos transacción para asegurar atomicidad
        with transaction.atomic():
            # select_for_update() bloquea el registro durante la transacción (bloqueo pesimista)
            cuenta = Cuenta.objects.select_for_update().get(pk=self.pk)

            if cuenta.saldo < cantidad:
                raise ValueError("Saldo insuficiente")

            cuenta.saldo = F('saldo') - cantidad
            cuenta.save()

            cuenta.refresh_from_db()
            self.refresh_from_db()

        return self.saldo


class Transaccion(models.Model):
    DEPOSITO = 'DEP'
    RETIRO = 'RET'

    TIPOS_TRANSACCION = [
        (DEPOSITO, 'Depósito'),
        (RETIRO, 'Retiro'),
    ]

    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='transacciones')
    tipo = models.CharField(max_length=3, choices=TIPOS_TRANSACCION)
    cantidad = models.DecimalField(max_digits=15, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    saldo_resultante = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.get_tipo_display()} de ${self.cantidad} en cuenta {self.cuenta.numero_cuenta}"