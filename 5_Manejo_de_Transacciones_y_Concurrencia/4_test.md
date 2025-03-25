# Análisis del Test de Concurrencia

En este documento analizaremos el test de concurrencia implementado para el sistema de transacciones financieras, explicando su funcionamiento, componentes y cómo verifica la consistencia de los datos bajo condiciones de alta concurrencia.

## Código del test

Primero, revisemos el código completo del test:

```python
# test_concurrencia.py
from django.test import TransactionTestCase
from django.db import connections
from concurrent.futures import ThreadPoolExecutor
import random
from decimal import Decimal
from .models import Cuenta, Transaccion

class ConcurrenciaTestCase(TransactionTestCase):
    def setUp(self):
        # Crear una cuenta con saldo inicial
        self.cuenta = Cuenta.objects.create(
            numero_cuenta="123456789",
            propietario="Usuario Test",
            saldo=Decimal("1000.00")
        )
    
    def _realizar_transaccion(self, tipo, cantidad):
        # Cerramos la conexión de este hilo para evitar compartir conexiones
        # entre hilos (Django usa el mismo objeto de conexión)
        connections.close_all()
        
        try:
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
    
    def test_concurrencia_sin_control(self):
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
```

## Componentes clave del test

### 1. Uso de `TransactionTestCase`

```python
class ConcurrenciaTestCase(TransactionTestCase):
```

`TransactionTestCase` es una clase especial de Django para tests que necesitan manipular transacciones. A diferencia de `TestCase` normal, no envuelve cada test en una transacción, lo que es esencial para probar concurrencia.

### 2. Configuración inicial (`setUp`)

```python
def setUp(self):
    # Crear una cuenta con saldo inicial
    self.cuenta = Cuenta.objects.create(
        numero_cuenta="123456789",
        propietario="Usuario Test",
        saldo=Decimal("1000.00")
    )
```

Crea una cuenta de prueba con un saldo inicial de 1000.00.

### 3. Método auxiliar para realizar transacciones

```python
def _realizar_transaccion(self, tipo, cantidad):
    # Cerramos la conexión de este hilo para evitar compartir conexiones
    connections.close_all()
    
    try:
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
```

Puntos importantes:
- `connections.close_all()`: Cierra las conexiones existentes para evitar compartir conexiones entre hilos, lo que podría causar errores.
- Realiza depósitos o retiros según el tipo especificado.
- Registra la transacción en la base de datos.
- Maneja excepciones para que un error en una transacción no detenga todo el test.

### 4. Simulación de operaciones concurrentes con `ThreadPoolExecutor`

```python
# Ejecutar transacciones concurrentemente
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for tipo, cantidad in transacciones:
        futures.append(executor.submit(self._realizar_transaccion, tipo, cantidad))
    
    # Esperar a que todas las transacciones terminen
    for future in futures:
        future.result()
```

Esta es la parte más importante para simular concurrencia:
- `ThreadPoolExecutor(max_workers=10)`: Crea un pool de 10 hilos para ejecutar tareas en paralelo.
- `executor.submit()`: Envía cada transacción para ser ejecutada en un hilo del pool.
- `future.result()`: Espera a que todas las transacciones terminen.

Con 10 hilos trabajando simultáneamente en 100 transacciones, se genera una alta concurrencia que pondría a prueba nuestros mecanismos de control.

### 5. Verificación de resultados

```python
# Refrescar el objeto cuenta
self.cuenta.refresh_from_db()
print("Saldo final esperado:", saldo_esperado)
print("Saldo final actual:", self.cuenta.saldo)

# Verificar el resultado
self.assertEqual(self.cuenta.saldo, saldo_esperado)

# Contar transacciones
total_transacciones = Transaccion.objects.filter(cuenta=self.cuenta).count()
self.assertEqual(total_transacciones, 100)
```

Verifica que:
- El saldo final coincida con el saldo esperado calculado de forma secuencial.
- Se hayan registrado exactamente 100 transacciones.

## Interpretación de los resultados

Cuando ejecutas este test y ves la salida:

```
Saldo inicial: 1000.00
Saldo final esperado: 1450.74
Saldo final actual: 1450.74
.
----------------------------------------------------------------------
Ran 1 test in 0.492s

OK
```

Esto indica que:
1. Se inició con un saldo de 1000.00
2. El saldo esperado después de 100 transacciones aleatorias era 1450.74
3. El saldo actual después de ejecutar las transacciones concurrentes también es 1450.74
4. El test pasó correctamente en 0.492 segundos

**La coincidencia entre saldo esperado y saldo actual demuestra que los mecanismos de control de concurrencia están funcionando correctamente**, ya que se obtiene el mismo resultado que si las transacciones se hubieran procesado secuencialmente.

## Problemas identificados en la ejecución

En la salida del test se ve este error después de que el test pasa correctamente:

```
OperationalError: database "test_transaccion_test" is being accessed by other users
DETAIL: There are 10 other sessions using the database.
```

Este error ocurre porque algunas conexiones a la base de datos no se cerraron correctamente:

1. Aunque el test llama a `connections.close_all()` al inicio de cada transacción, podría no estar cerrándolas correctamente al finalizar.
2. Las 10 conexiones que quedan abiertas corresponden precisamente a los 10 hilos del pool que utilizamos.

## Solución al problema de conexiones

Para solucionar este problema, podríamos modificar el método `_realizar_transaccion` para asegurar que las conexiones se cierren incluso si ocurre una excepción:

```python
def _realizar_transaccion(self, tipo, cantidad):
    try:
        # Cerramos la conexión de este hilo para evitar compartir conexiones
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
        # Cerrar conexiones al finalizar, incluso si hay error
        connections.close_all()
```

Alternativamente, podríamos modificar el método de test para cerrar todas las conexiones al final:

```python
def test_concurrencia_sin_control(self):
    try:
        # Código del test
        # ...
    finally:
        # Forzar cierre de todas las conexiones
        for conn in connections.all():
            conn.close()
        connections.close_all()
```

## Resumen del test

Este test demuestra de forma efectiva que:

1. **Los mecanismos de control de concurrencia funcionan correctamente**, ya que 100 transacciones aleatorias ejecutadas concurrentemente por 10 hilos producen el mismo resultado que si se ejecutaran secuencialmente.

2. **El sistema puede manejar alta concurrencia**, como lo demuestra la velocidad de ejecución (menos de medio segundo para 100 transacciones).

3. **La consistencia de datos se mantiene** incluso bajo alta carga, sin condiciones de carrera ni inconsistencias en el saldo final.

El único problema identificado está relacionado con la gestión de conexiones a la base de datos, lo cual es un aspecto importante a considerar cuando se trabaja con hilos en Django, pero no afecta la validez del test en cuanto a la verificación de los mecanismos de concurrencia.