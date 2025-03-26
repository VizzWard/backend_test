import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status


class ServiceProxy:
    @staticmethod
    def forward_request(service, path, request, **kwargs):
        service_url = settings.SERVICES.get(service.upper())
        if not service_url:
            return Response(
                {"error": f"Servicio '{service}' no configurado"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        url = f"{service_url}{path}"
        method = request.method.lower()

        # Preparar headers
        headers = {}
        if 'HTTP_AUTHORIZATION' in request.META:
            headers['Authorization'] = request.META['HTTP_AUTHORIZATION']

        # Realizar la solicitud al servicio
        try:
            request_kwargs = {
                'headers': headers,
            }

            if method in ['post', 'put', 'patch']:
                request_kwargs['json'] = request.data
            elif method == 'get':
                request_kwargs['params'] = request.query_params

            response = getattr(requests, method)(url, **request_kwargs)

            return Response(
                data=response.json() if response.content else None,
                status=response.status_code
            )
        except requests.RequestException as e:
            return Response(
                {"error": f"Error al comunicarse con el servicio: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )