# Referencia de Endpoints

## Base URL: `http://localhost:8000/api`

## Autenticación

| Método | Endpoint | Descripción | Payload | Respuesta |
|--------|----------|-------------|---------|-----------|
| POST | `/token/` | Obtener token JWT | `{"username": "string", "password": "string"}` | `{"access": "string", "refresh": "string"}` |
| POST | `/token/refresh/` | Renovar token | `{"refresh": "string"}` | `{"access": "string"}` |

## Usuarios

| Método | Endpoint | Descripción | Payload | Respuesta |
|--------|----------|-------------|---------|-----------|
| GET | `/usuarios/` | Listar usuarios | - | Array de usuarios |
| POST | `/usuarios/` | Crear usuario | ```{"username": "string", "password": "string", "email": "string", "first_name": "string", "last_name": "string", "telefono": "string", "direccion": "string"}``` | Datos del usuario creado |
| GET | `/usuarios/{id}/` | Ver usuario | - | Datos del usuario |
| PUT | `/usuarios/{id}/` | Actualizar usuario completo | Igual que crear | Datos actualizados |
| PATCH | `/usuarios/{id}/` | Actualizar parcialmente | Campos a actualizar | Datos actualizados |
| DELETE | `/usuarios/{id}/` | Eliminar usuario | - | - |
| GET | `/usuarios/me/` | Ver usuario actual | - | Datos del usuario autenticado |

## Categorías

| Método | Endpoint | Descripción | Payload | Respuesta |
|--------|----------|-------------|---------|-----------|
| GET | `/categorias/` | Listar categorías | - | Array de categorías |
| POST | `/categorias/` | Crear categoría | `{"nombre": "string", "descripcion": "string"}` | Datos de la categoría |
| GET | `/categorias/{id}/` | Ver categoría | - | Datos de la categoría |
| PUT | `/categorias/{id}/` | Actualizar categoría | Igual que crear | Datos actualizados |
| DELETE | `/categorias/{id}/` | Eliminar categoría | - | - |

## Productos

| Método | Endpoint | Descripción | Payload | Respuesta |
|--------|----------|-------------|---------|-----------|
| GET | `/productos/` | Listar productos | - | Array de productos |
| GET | `/productos/?categoria={id}` | Filtrar por categoría | - | Array de productos filtrados |
| POST | `/productos/` | Crear producto | ```{"nombre": "string", "descripcion": "string", "precio": 0.00, "stock": 0, "categoria": 1}``` | Datos del producto |
| GET | `/productos/{id}/` | Ver producto | - | Datos del producto |
| PUT | `/productos/{id}/` | Actualizar producto | Igual que crear | Datos actualizados |
| PATCH | `/productos/{id}/` | Actualizar parcialmente | Campos a actualizar | Datos actualizados |
| DELETE | `/