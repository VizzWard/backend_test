import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .proxy import ServiceProxy
from django.conf import settings

# Create your views here.
class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        """
        Reenvía la solicitud de autenticación al servicio de usuarios
        y devuelve el token JWT generado
        """
        login_url = f"{settings.SERVICES['USUARIOS']}token/"
        print(f"URL de autenticación: {login_url}")

        try:
            response = requests.post(
                login_url,
                json=request.data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return Response(
                data=response.json() if response.content else None,
                status=response.status_code
            )
        except requests.RequestException as e:
            return Response(
                {"error": f"Error al comunicarse con el servicio de autenticación: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )


class RefreshTokenView(APIView):
    permission_classes = []

    def post(self, request):
        """
        Reenvía la solicitud de refresh token al servicio de usuarios
        """
        refresh_url = f"{settings.SERVICES['USUARIOS']}token/refresh/"

        try:
            response = requests.post(
                refresh_url,
                json=request.data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return Response(
                data=response.json() if response.content else None,
                status=response.status_code
            )
        except requests.RequestException as e:
            return Response(
                {"error": f"Error al comunicarse con el servicio de autenticación: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )

class ProxyView(APIView):
    def initialize_request(self, request, *args, **kwargs):
        self.service = kwargs.get('service', '')
        # Asegurarse de que path nunca sea None
        self.path = kwargs.get('path', '')
        if self.path is None:
            self.path = ''
        return super().initialize_request(request, *args, **kwargs)

    def get_permissions(self):
        # API root
        if not self.service:
            return [AllowAny()]

        # Registro de usuarios - permitir POST sin autenticación
        if self.service == 'usuarios' and self.request.method == 'POST':
            return [AllowAny()]
        # Ver productos sin autenticación
        elif self.service == 'productos' and self.request.method == 'GET':
            return [AllowAny()]
        # Otros endpoints requieren autenticación
        return [IsAuthenticated()]

    def handle_request(self, request, *args, **kwargs):
        # Respuesta base para API root sin servicio
        if not self.service:
            return Response({
                "usuarios_endpoint": "/api/usuarios/",
                "productos_endpoint": "/api/productos/",
                "ordenes_endpoint": "/api/ordenes/",
                "token_endpoint": "/api/token/",
                "token_refresh_endpoint": "/api/token/refresh/"
            })

        return ServiceProxy.forward_request(
            self.service,
            self.path,
            request
        )

    def get(self, request, *args, **kwargs):
        return self.handle_request(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.handle_request(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.handle_request(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.handle_request(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.handle_request(request, *args, **kwargs)