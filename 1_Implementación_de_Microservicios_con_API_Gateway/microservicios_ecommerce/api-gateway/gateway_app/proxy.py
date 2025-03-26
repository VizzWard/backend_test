import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
import logging
import json

logger = logging.getLogger(__name__)


class ServiceProxy:
    @staticmethod
    def forward_request(service, path, request, **kwargs):
        service_url = settings.SERVICES.get(service.upper())
        if not service_url:
            return Response(
                {"error": f"Servicio '{service}' no configurado"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # Importante: si path está vacío, aseguramos que se use la barra al final del servicio_url
        # Si service_url termina con / y path está vacío, no agregamos otra /
        if not path and not service_url.endswith('/'):
            url = f"{service_url}/"
        else:
            url = f"{service_url}{path}"

        method = request.method.lower()

        # Log detallado para depurar
        logger.info(f"Forward Request:")
        logger.info(f"Service: {service}")
        logger.info(f"Path: '{path}'")
        logger.info(f"URL Completa: {url}")
        logger.info(f"Método: {method}")

        # Preparar headers
        headers = {
            'Content-Type': 'application/json',
        }

        if 'HTTP_AUTHORIZATION' in request.META:
            headers['Authorization'] = request.META['HTTP_AUTHORIZATION']

        logger.info(f"Headers: {headers}")

        # Preparar datos
        data = None
        if method in ['post', 'put', 'patch'] and request.data:
            data = request.data
            logger.info(f"Datos: {json.dumps(data)}")

        # Realizar la solicitud al servicio
        try:
            if method == 'get':
                response = requests.get(url, headers=headers, params=request.query_params, timeout=10)
            elif method == 'post':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == 'put':
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == 'patch':
                response = requests.patch(url, headers=headers, json=data, timeout=10)
            elif method == 'delete':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return Response({"error": f"Método {method} no soportado"}, status=status.HTTP_400_BAD_REQUEST)

            # Log de la respuesta
            logger.info(f"Respuesta del servicio {service}:")
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Contenido: {response.text[:500]}")

            try:
                data = response.json() if response.content else None
                return Response(data=data, status=response.status_code)
            except ValueError:
                # Si no es JSON válido, devolver el texto
                logger.error(f"Respuesta no es JSON válido: {response.text}")
                return Response(
                    {"error": "Respuesta no válida del servicio", "detail": response.text[:500]},
                    status=status.HTTP_502_BAD_GATEWAY
                )

        except requests.RequestException as e:
            logger.error(f"Error al comunicarse con el servicio {service}: {str(e)}")
            return Response(
                {"error": f"Error al comunicarse con el servicio {service}", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )