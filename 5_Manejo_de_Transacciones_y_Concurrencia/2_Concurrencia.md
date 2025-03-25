# Concurrencia en Django

## ¿Qué es la concurrencia?

La concurrencia ocurre cuando múltiples procesos o hilos intentan acceder y modificar los mismos recursos (datos) simultáneamente. En sistemas de información, especialmente aquellos que manejan transacciones financieras, es crucial manejarla correctamente para evitar:

- **Condiciones de carrera**: Cuando el resultado final depende del orden específico en que se ejecutan operaciones concurrentes.
- **Inconsistencias de datos**: Por ejemplo, que dos usuarios retiren el mismo dinero o que los saldos no reflejen con precisión el resultado de múltiples operaciones.

## Problemas de concurrencia en sistemas financieros

Imaginemos este escenario sin control de concurrencia:

1. El usuario A verifica que tiene $100 y quiere retirar $50
2. El usuario B verifica que tiene $100 y quiere retirar $80
3. El usuario A completa su retiro, dejando $50
4. El usuario B completa su retiro, dejando $20

¡Problema! Realmente no había $130 disponibles para retirar, pero ambas transacciones se procesaron, creando una inconsistencia grave.

## Soluciones de concurrencia en Django

### 1. Transacciones atómicas

Las transacciones atómicas garantizan que un conjunto de operaciones se ejecute completamente o no se ejecute en absoluto.

```python
from django.db import transaction

with transaction.atomic():
    # Operaciones dentro de una transacción
    # Si ocurre un error, todas las operaciones son revertidas
```

### 2. Bloqueos pesimistas

Los bloqueos pesimistas asumen que habrá conflictos y los previenen, bloqueando el acceso a los recursos.

```python
# Bloqueo pesimista con select_for_update()
cuenta = Cuenta.objects.select_for_update().get(pk=self.pk)
```

Este método bloquea el registro en la base de datos hasta que la transacción se complete, impidiendo que otros procesos lo modifiquen.

### 3. Operaciones a nivel de base de datos con F()

La expresión `F()` de Django permite realizar operaciones directamente en la base de datos sin traer primero el valor a Python.

```python
from django.db.models import F

# En lugar de:
cuenta.saldo = cuenta.saldo + cantidad
cuenta.save()

# Usa:
cuenta.saldo = F('saldo') + cantidad
cuenta.save()
```

Esto evita problemas de concurrencia cuando múltiples operaciones intentan actualizar el mismo campo.

## ¿Dónde ocurre realmente el bloqueo?

El bloqueo ocurre a nivel de la **base de datos**, no en el código Python ni en la vista:

- Cuando ejecutas `select_for_update()`, esto se traduce a SQL con `FOR UPDATE`, que le indica a la base de datos que bloquee esa fila específica.
- El bloqueo afecta sólo a la fila específica, no a toda la tabla.
- Las operaciones de solo lectura (consultas SELECT normales) generalmente no son bloqueadas, a menos que la base de datos esté configurada con niveles altos de aislamiento.

## Flujo de peticiones concurrentes

Cuando varias peticiones llegan al mismo tiempo a un endpoint:

1. Todas las peticiones entran a la vista de forma concurrente (según la capacidad de hilos del servidor).
2. Cada una ejecuta el código hasta llegar a `select_for_update()`.
3. En ese punto exacto, la base de datos determina qué petición obtiene el bloqueo primero.
4. Las demás peticiones que intentan acceder al mismo registro esperan (son bloqueadas a nivel de base de datos).
5. A medida que cada transacción termina, se liberan los bloqueos y las peticiones en espera avanzan una a una.

## Preguntas frecuentes sobre concurrencia

### ¿El bloqueo afecta a las operaciones de lectura?

En general, las operaciones de solo lectura (sin `select_for_update()`) no se bloquean y pueden leer datos incluso si hay un bloqueo de escritura activo. Sin embargo, esto depende del nivel de aislamiento configurado en la base de datos.

### ¿Cómo se manejan múltiples peticiones a diferentes recursos?

- Las peticiones que afectan a diferentes recursos (diferentes filas o tablas) no se bloquean entre sí.
- Por ejemplo, si hay transacciones sobre la cuenta #1 y otras sobre la cuenta #2, pueden procesarse simultáneamente sin interferir.

### ¿Cómo funciona a nivel de servidor web?

Django/DRF utiliza por defecto un modelo sincrónico:
- Cada petición ocupa un hilo del servidor hasta completarse.
- El número de peticiones concurrentes está limitado por la cantidad de hilos disponibles.
- Los bloqueos a nivel de base de datos no impiden que el servidor procese otras peticiones, solo hacen que los hilos afectados esperen.

## Escalabilidad y concurrencia

### Escalamiento horizontal vs. vertical

- **Escalamiento vertical**: Aumentar la potencia de un solo servidor (más CPU, RAM, etc.)
- **Escalamiento horizontal**: Añadir más servidores para distribuir la carga

El manejo de concurrencia implementado con bloqueos a nivel de base de datos es compatible con ambos enfoques, especialmente útil para el escalamiento horizontal donde múltiples servidores comparten la misma base de datos.

### Limitaciones de los hilos

- El número de hilos no está limitado 1:1 con los núcleos físicos, pero hay overhead cuando hay más hilos activos que núcleos.
- Los servidores como Gunicorn o uWSGI permiten configurar el número de workers y threads.
- Una configuración común es: `(2 × núcleos_CPU) + 1` workers.

## Casos donde los bloqueos son necesarios

### 1. Transacciones financieras y monetarias
- Saldos de cuenta
- Procesamiento de pagos
- Transferencias entre cuentas
- Sistemas de puntos o créditos con valor monetario

### 2. Gestión de inventario y stock
- Sistemas de e-commerce donde múltiples usuarios pueden comprar los mismos productos limitados
- Sistemas de reserva donde los recursos son finitos (habitaciones, asientos)
- Gestión de entradas para eventos

### 3. Sistemas de reserva y agendamiento
- Citas médicas
- Reserva de salas
- Alquiler de vehículos o equipos

### 4. Sistemas de votación o encuestas
- Donde es necesario asegurar que cada usuario vote solo una vez
- Donde los totales deben ser precisos

### 5. Sistemas de asignación de recursos únicos
- Nombres de usuario o dominios únicos
- Asignación de identificadores secuenciales
- Cualquier recurso que deba ser exclusivo

## Casos donde posiblemente no se justifique

### 1. Operaciones de solo lectura
- Sistemas principalmente de consulta
- Dashboards y reporting

### 2. Datos que no son críticos para la consistencia
- Contadores de visualizaciones aproximados
- Estadísticas que pueden ser eventualmente consistentes
- Sistemas donde una pequeña discrepancia es aceptable

### 3. Datos que raramente tienen modificaciones concurrentes
- Perfiles de usuario que solo son modificados por el propio usuario
- Configuraciones que se modifican infrecuentemente

## Alternativas a los bloqueos pesimistas

1. **Bloqueos optimistas**: Verificar si el dato ha sido modificado antes de guardarlo, sin bloquear preventivamente.
2. **Arquitecturas de cola**: Enviar operaciones a una cola y procesarlas secuencialmente.
3. **Particionamiento**: Dividir los datos para que las operaciones concurrentes rara vez afecten a la misma partición.
4. **Idempotencia**: Diseñar operaciones que pueden ejecutarse múltiples veces sin efectos secundarios.

## Resumen

La concurrencia es un aspecto fundamental en el desarrollo de aplicaciones robustas, especialmente aquellas que manejan recursos compartidos o limitados. Django ofrece múltiples herramientas para manejarla adecuadamente:

- `transaction.atomic()` para garantizar atomicidad
- `select_for_update()` para bloqueos pesimistas
- Expresiones `F()` para operaciones a nivel de base de datos

La implementación correcta de estos mecanismos permite desarrollar sistemas que mantienen la integridad de los datos incluso bajo alta concurrencia, a la vez que maximizan el rendimiento dentro de las limitaciones impuestas por los requisitos de consistencia.