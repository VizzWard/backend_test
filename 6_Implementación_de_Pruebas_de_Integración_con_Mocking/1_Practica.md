# 6. Implementación de Pruebas de Integración con Mocking

Implementa pruebas de integración para un sistema de pedidos que dependa de un servicio de autenticación externo y de una base de datos de inventario. Usa técnicas de mocking para simular las respuestas de estos servicios.

Tareas:

1. Desarrolla una función que cree un nuevo pedido solo si el usuario está autenticado y el inventario es suficiente.
2. Escribe pruebas de integración para verificar el comportamiento en escenarios:
   - Usuario autenticado y con inventario. 
   - Usuario autenticado sin inventario. 
   - Usuario no autenticado.
3. Usa técnicas de mocking para simular el servicio de autenticación y de inventario.