# Arquitectura de Microservicios - Sistema de Comercio Electrónico

## Visión General

Este proyecto implementa una arquitectura de microservicios para un sistema de comercio electrónico usando Django y Django REST Framework. La arquitectura incluye cuatro componentes principales:

1. **API Gateway**: Punto de entrada único que enruta solicitudes y centraliza autenticación
2. **Servicio de Usuarios**: Gestiona autenticación y datos de usuarios
3. **Servicio de Productos**: Administra productos y categorías
4. **Servicio de Órdenes**: Gestiona pedidos y su procesamiento

## Diagrama de Arquitectura

```
┌─────────────┐      ┌───────────────────┐
│             │      │                   │
│   Cliente   │◄────►│    API Gateway    │
│             │      │                   │
└─────────────┘      └───────┬───────────┘
                           ┌─┴─┐
               ┌───────────┤   ├───────────┐
               │           └───┘           │
               ▼             │             ▼
┌─────────────────────┐      │      ┌─────────────────────┐
│                     │      │      │                     │
│ Servicio Usuarios   │◄─────┼─────►│ Servicio Productos  │
│                     │      │      │                     │
└─────────────────────┘      │      └─────────────────────┘
               ▲             │             ▲
               │             ▼             │
               │      ┌─────────────────────┐
               │      │                     │
               └─────►│ Servicio Órdenes    │
                      │                     │
                      └─────────────────────┘
```

## Estructura del Proyecto

```
microservicios-ecommerce/
│
├── api-gateway/                  # API Gateway
│   ├── api_gateway/              # Configuración principal
│   ├── gateway_app/              # Lógica de proxy y autenticación
│   ├── Dockerfile
│   └── requirements.txt
│
├── usuarios/                     # Servicio de Usuarios
│   ├── usuarios_service/         # Configuración principal
│   ├── usuarios_app/             # Modelos y lógica de usuarios
│   ├── Dockerfile
│   └── requirements.txt
│
├── productos/                    # Servicio de Productos
│   ├── productos_service/        # Configuración principal
│   ├── productos_app/            # Modelos y lógica de productos
│   ├── Dockerfile
│   └── requirements.txt
│
├── ordenes/                      # Servicio de Órdenes
│   ├── ordenes_service/          # Configuración principal
│   ├── ordenes_app/              # Modelos y lógica de órdenes
│   ├── Dockerfile
│   └── requirements.txt
│
└── docker-compose.yml            # Configuración de Docker Compose
```

## Principios de Diseño

1. **Independencia**: Cada servicio tiene su propia base de datos y lógica de negocio
2. **Comunicación vía API**: Los servicios se comunican entre sí mediante HTTP/REST
3. **Autenticación centralizada**: JWT gestionados por el API Gateway
4. **Resiliencia**: Manejo de errores de comunicación entre servicios

## Flujo de Operación

1. El cliente envía solicitudes al API Gateway
2. El API Gateway autentica al usuario (si es necesario)
3. Las solicitudes se redirigen al servicio adecuado
4. Los servicios se comunican entre sí cuando necesitan datos de otros dominios
5. Las respuestas se devuelven al cliente a través del API Gateway
