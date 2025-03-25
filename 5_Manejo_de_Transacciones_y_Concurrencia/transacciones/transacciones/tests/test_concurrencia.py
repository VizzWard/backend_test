from django.test import TransactionTestCase
from django.db import connections
from concurrent.futures import ThreadPoolExecutor
import random
from decimal import Decimal
from cuenta.models import Cuenta, Transaccion


class ConcurrenciaTestCase(TransactionTestCase):
    def setUp(self):
        # Crear una cuenta con saldo inicial
        self.cuenta = Cuenta.objects.create(
            numero_cuenta="123456789",
            propietario="Usuario Test",
            saldo=Decimal("1000.00")
        )

    def _realizar_transaccion(self, tipo, cantidad):
        try:
            # Cerramos la conexión de este hilo para evitar compartir conexiones
            # entre hilos (Django usa el mismo objeto de conexión)
            connections.close_all()

            cuenta = Cuenta.objects.get(pk=self.cuenta.pk)
            if tipo == Transaccion.DEPOSITO:
                saldo = cuenta.depositar(cantidad)
            else:
                saldo = cuenta.retirar(cantidad)

            Transaccion.objects.create(
                cuenta=cuenta,
                tipo=tipo,
                cantidad=cantidad,
                saldo_resultante=saldo
            )
            return True
        except Exception as e:
            print(f"Error en transacción: {e}")
            return False
        finally:
            # Asegurarnos de cerrar las conexiones siempre
            connections.close_all()

    def test_concurrencia_sin_control(self):
        try:
            # Esta prueba simularía el problema sin control de concurrencia
            # (en realidad, lo omitimos porque el código ya incluye control)
            print("Saldo inicial:", self.cuenta.saldo)

            # Preparar transacciones aleatorias
            transacciones = []
            for _ in range(100):
                tipo = random.choice([Transaccion.DEPOSITO, Transaccion.RETIRO])
                cantidad = Decimal(str(random.uniform(10, 50))).quantize(Decimal('0.01'))
                transacciones.append((tipo, cantidad))

            # Calcular el resultado esperado
            saldo_esperado = self.cuenta.saldo
            for tipo, cantidad in transacciones:
                if tipo == Transaccion.DEPOSITO:
                    saldo_esperado += cantidad
                else:
                    # Simplificamos para la prueba asumiendo que hay saldo suficiente
                    saldo_esperado -= cantidad

            # Ejecutar transacciones concurrentemente
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for tipo, cantidad in transacciones:
                    futures.append(executor.submit(self._realizar_transaccion, tipo, cantidad))

                # Esperar a que todas las transacciones terminen
                for future in futures:
                    future.result()

            # Refrescar el objeto cuenta
            self.cuenta.refresh_from_db()
            print("Saldo final esperado:", saldo_esperado)
            print("Saldo final actual:", self.cuenta.saldo)

            # Verificar el resultado
            # Nota: Con control de concurrencia, estos deberían ser iguales
            self.assertEqual(self.cuenta.saldo, saldo_esperado)

            # Contar transacciones
            total_transacciones = Transaccion.objects.filter(cuenta=self.cuenta).count()
            self.assertEqual(total_transacciones, 100)
        finally:
            # Forzar cierre de todas las conexiones
            connections.close_all()