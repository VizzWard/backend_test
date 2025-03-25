# Implementación de Concurrencia en el Sistema de Transacciones

En esta guía analizaremos cómo se implementó la concurrencia en el sistema de transacciones financieras desarrollado con Django y Django Rest Framework.

## Mecanismos de concurrencia utilizados

### 1. Transacciones atómicas (`transaction.atomic`)

Las transacciones atómicas garantizan que un conjunto de operaciones se ejecute completamente o no se ejecute en absoluto.

```python
# En el método retirar de la clase Cuenta
with transaction.atomic():
    cuenta = Cuenta.objects.select_for_update().get(pk=self.pk)
    
    if cuenta.saldo < cantidad:
        raise ValueError("Saldo insuficiente")
    
    cuenta.saldo = F('saldo') - cantidad
    cuenta.save()
```

**¿Dónde se usa?**
- En el método `retirar` de la clase `Cuenta`
- En el método `realizar_transaccion` del `CuentaViewSet`

**Beneficio:** Si ocurre cualquier error dentro del bloque `with`, todas las operaciones realizadas se revierten, manteniendo la consistencia de los datos.

### 2. Bloqueos pesimistas (`select_for_update`)

El método `select_for_update()` implementa un bloqueo pesimista que impide que otros procesos modifiquen el mismo registro mientras se ejecuta la transacción.

```python
# Obtener el registro con bloqueo exclusivo
cuenta = Cuenta.objects.select_for_update().get(pk=cuenta_id)
```

**¿Dónde se usa?**
- Dentro del método `retirar` de la clase `Cuenta`
- En el método `realizar_transaccion` del `CuentaViewSet`

**Funcionamiento:** Cuando se ejecuta `select_for_update()`, la base de datos genera un bloqueo exclusivo en el registro. Si otra transacción intenta acceder al mismo registro con `select_for_update()`, tendrá que esperar hasta que se libere el bloqueo.

### 3. Expresiones F para actualizaciones a nivel de base de datos

Las expresiones `F()` permiten realizar operaciones directamente en la base de datos sin traer primero los valores a Python.

```python
# En el método depositar de la clase Cuenta
self.saldo = F('saldo') + cantidad
self.save()
```

**¿Dónde se usa?**
- En el método `depositar` de la clase `Cuenta`
- En el método `retirar` de la clase `Cuenta`

**Beneficio:** Evita condiciones de carrera cuando múltiples procesos intentan actualizar el mismo campo, ya que la operación se realiza a nivel de base de datos en una sola consulta.

## Flujo de una transacción con manejo de concurrencia

Veamos paso a paso cómo se maneja la concurrencia cuando se realiza una transacción:

1. **Inicio de transacción atómica:**
   ```python
   with transaction.atomic():
   ```

2. **Obtención del registro con bloqueo:**
   ```python
   cuenta = Cuenta.objects.select_for_update().get(pk=cuenta_id)
   ```
   - Este paso es crítico. Si otra transacción ya tiene bloqueado este registro, esta línea esperará hasta que se libere.

3. **Validación de condiciones:**
   ```python
   if cuenta.saldo < cantidad:
       raise ValueError("Saldo insuficiente")
   ```
   - Dentro del bloqueo, podemos verificar de forma segura que se cumplan todas las condiciones necesarias.

4. **Actualización usando expresiones F:**
   ```python
   cuenta.saldo = F('saldo') - cantidad
   cuenta.save()
   ```
   - La actualización se realiza de forma segura dentro del bloqueo.

5. **Liberación automática del bloqueo:**
   - Al salir del bloque `with transaction.atomic()`, se confirman los cambios y se libera el bloqueo.

## Diferencias en el manejo de depósitos y retiros

Es interesante notar que hay una diferencia en cómo se implementa la concurrencia para depósitos y retiros:

### Depósitos (menor nivel de protección)
```python
def depositar(self, cantidad):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva")
    
    # Usamos F() para actualizar el saldo a nivel de base de datos
    self.saldo = F('saldo') + cantidad
    self.save()
    self.refresh_from_db()
    return self.saldo
```

- **Usa expresiones F** para evitar condiciones de carrera
- **No usa bloqueos pesimistas** directamente en el método
- Esto es apropiado porque un depósito no requiere validación del saldo actual

### Retiros (mayor nivel de protección)
```python
def retirar(self, cantidad):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva")
    
    with transaction.atomic():
        cuenta = Cuenta.objects.select_for_update().get(pk=self.pk)
        
        if cuenta.saldo < cantidad:
            raise ValueError("Saldo insuficiente")
        
        cuenta.saldo = F('saldo') - cantidad
        cuenta.save()
        
        cuenta.refresh_from_db()
        self.refresh_from_db()
        
    return self.saldo
```

- **Usa expresiones F** para evitar condiciones de carrera
- **Usa bloqueos pesimistas** con `select_for_update()`
- **Usa transacciones atómicas** para garantizar consistencia
- Esto es necesario porque debemos validar que haya saldo suficiente antes de retirar

## Manejo de concurrencia en el ViewSet

En la capa de API, el manejo de concurrencia se implementa en el método `realizar_transaccion`:

```python
@action(detail=False, methods=['post'])
def realizar_transaccion(self, request):
    # Validación de datos omitida
    
    try:
        with transaction.atomic():
            # Bloqueo pesimista
            cuenta = Cuenta.objects.select_for_update().get(pk=cuenta_id)
            
            if tipo == Transaccion.DEPOSITO:
                nuevo_saldo = cuenta.depositar(cantidad)
            elif tipo == Transaccion.RETIRO:
                if cuenta.saldo < cantidad:
                    return Response({"error": "Saldo insuficiente"}, status=status.HTTP_400_BAD_REQUEST)
                nuevo_saldo = cuenta.retirar(cantidad)
            
            # Registrar la transacción
            transaccion = Transaccion.objects.create(
                cuenta=cuenta,
                tipo=tipo,
                cantidad=cantidad,
                saldo_resultante=nuevo_saldo
            )
            
            return Response({
                "mensaje": f"Transacción realizada exitosamente",
                "transaccion_id": transaccion.id,
                "nuevo_saldo": nuevo_saldo
            }, status=status.HTTP_201_CREATED)
    except Cuenta.DoesNotExist:
        return Response({"error": "Cuenta no encontrada"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

**Características clave:**
- Usa transacción atómica para englobar toda la operación
- Obtiene la cuenta con bloqueo pesimista
- Maneja correctamente las excepciones
- Registra la transacción como parte de la misma transacción atómica

## Consideraciones finales sobre la implementación

1. **Posible redundancia de bloqueos:** En el caso de retiro, hay doble bloqueo (`select_for_update()` tanto en el ViewSet como en el método `retirar`). Esto es redundante pero no afecta el funcionamiento.

2. **Granularidad del bloqueo:** Los bloqueos se aplican a nivel de registro (fila), no a toda la tabla, lo que permite concurrencia máxima para transacciones que afectan a diferentes cuentas.

3. **Captura de excepciones:** El código maneja correctamente las excepciones para garantizar que los bloqueos se liberen incluso si ocurre un error.

4. **Transacciones anidadas:** Django maneja correctamente las transacciones anidadas, por lo que no hay problemas con tener bloques `transaction.atomic()` dentro de otros.

Este manejo de concurrencia garantiza que el sistema pueda procesar múltiples transacciones simultáneas de forma segura, manteniendo la consistencia de los datos y evitando condiciones de carrera.