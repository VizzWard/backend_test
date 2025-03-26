# 7. Implementación de Rate Limiting en un Endpoint

Implementa una limitación de tasa (rate limiting) en un endpoint de una API que permita a cada usuario realizar hasta 10 solicitudes por minuto. Si el usuario supera este límite, la API debe devolver un código de error 429 (Too Many Requests).

__Tareas:__
1. Crear un endpoint que permita registrar visitas de un usuario.
2. Implementar una función de rate limiting que limite las solicitudes a 10 por minuto por usuario.
3. Proporciona un test que simule más de 10 solicitudes en un minuto y muestre el código de error esperado.