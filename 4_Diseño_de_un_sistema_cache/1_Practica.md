# 4. Diseño y Ejecución de un Sistema de Caché

Implementa una capa de caché para un servicio de productos que almacena datos en una base de datos. El servicio debe devolver datos desde el caché para evitar llamadas repetidas a la base de datos y actualizar el caché cada 5 minutos.

__Tareas:__

1. Crear una función que consulte la base de datos solo cuando el caché no tenga los datos.
2. Implementar una estrategia de expiración automática del caché cada 5 minutos.
3. Proporciona un test donde se muestren tiempos de consulta antes y después de implementar la caché.