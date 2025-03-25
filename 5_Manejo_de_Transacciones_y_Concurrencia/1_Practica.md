# 5. Manejo de Transacciones y Concurrencia

Implementa un sistema de transacciones financieras en el que múltiples usuarios pueden hacer depósitos y retiros. Asegúrate de que cada transacción se registre correctamente y evita problemas de concurrencia (condiciones de carrera).

__Tareas:__

1. Implementa una función para realizar depósitos y retiros de manera concurrente.
2. Usa bloqueos de base de datos (optimistas o pesimistas) para evitar problemas de inconsistencias.
3. Proporciona un test que simule 100 transacciones concurrentes y muestre los resultados antes y después de aplicar el control de concurrencia.