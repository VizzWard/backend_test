# Guía de Instalación con Docker

## Requisitos Previos
- Docker y Docker Compose instalados
- Git (opcional)

## Pasos de Instalación

### 1. Preparar la Estructura de Directorios

```bash
mkdir microservicios-ecommerce
cd microservicios-ecommerce
mkdir usuarios productos ordenes api-gateway
```

### 2. Preparar Archivos de Configuración

En cada carpeta de servicio (`usuarios`, `productos`, `ordenes`, `api-gateway`), asegurarse que existe:
- `Dockerfile`
- `requirements.txt`

En el directorio raíz, asegurarse de tener:
- `docker-compose.yml`

### 3. Creación de la Base de Datos PostgreSQL

Si no tienes PostgreSQL:

```bash
docker run --name postgresql -e POSTGRES_PASSWORD=180219 -p 5454:5432 -d postgres
```

Luego, crea las bases de datos:

```bash
docker exec -it postgresql psql -U postgres -c "CREATE DATABASE usuarios_service;"
docker exec -it postgresql psql -U postgres -c "CREATE DATABASE productos_service;"
docker exec -it postgresql psql -U postgres -c "CREATE DATABASE ordenes_service;"
docker exec -it postgresql psql -U postgres -c "CREATE DATABASE gateway_service;"
```

### 4. Configurar Servicios para Conexión a BD Externa

En cada archivo `settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "nombre_de_base_datos",  # ej: usuarios_service
        "USER": "postgres",
        "PASSWORD": "180219",
        "HOST": "host.docker.internal",  # Para acceder al host desde Docker
        "PORT": "5454",
    }
}
```

> Crear una DB dentro de Postgres (o la DB que uses) por cada servicio

### 5. Construir e Iniciar Servicios

```bash
docker-compose build
docker-compose up -d
```

Para ver logs:

```bash
docker-compose logs -f
```

### 6. Aplicar Migraciones

```bash
docker-compose exec usuarios-service python manage.py migrate
docker-compose exec productos-service python manage.py migrate
docker-compose exec ordenes-service python manage.py migrate
docker-compose exec api-gateway python manage.py migrate
```

### 7. Crear Superusuario (opcional)

```bash
docker-compose exec usuarios-service python manage.py createsuperuser
```

### 8. Acceder a la API

- API Gateway: http://localhost:8000/api/
- Autenticación: http://localhost:8000/api/token/
- Usuarios: http://localhost:8000/api/usuarios/
- Productos: http://localhost:8000/api/productos/
- Órdenes: http://localhost:8000/api/ordenes/

## Comandos Útiles

### Reiniciar un Servicio
```bash
docker-compose restart nombre-servicio
```

### Detener Servicios
```bash
docker-compose down
```

### Ver Logs de un Servicio Específico
```bash
docker-compose logs -f nombre-servicio
```

### Ejecutar Comandos en un Contenedor
```bash
docker-compose exec nombre-servicio comando
```

### Reconstruir Servicio con Cambios
```bash
docker-compose up -d --build nombre-servicio
```

## Solución de Problemas

### Error de Conexión a la Base de Datos
- Verificar que PostgreSQL está corriendo: `docker ps`
- Comprobar las credenciales en settings.py
- Para PostgreSQL local, usar `host.docker.internal` en lugar de `localhost`

### Error 405 Method Not Allowed
- Verificar que la vista tiene el método HTTP correcto permitido
- Comprobar las URLs en settings.py y urls.py

### Error en Comunicación entre Servicios
- Verificar las URLs de servicios en settings.py
- Comprobar logs para ver errores detallados
- Asegurar que ALLOWED_HOSTS incluya los nombres de servicio