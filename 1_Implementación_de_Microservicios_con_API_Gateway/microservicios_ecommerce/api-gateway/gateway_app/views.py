from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .proxy import ServiceProxy

# Create your views here.
class LoginView(TokenObtainPairView):
    pass

class RefreshTokenView(TokenRefreshView):
    pass

class ProxyView(APIView):
    def initialize_request(self, request, *args, **kwargs):
        self.service = kwargs.get('service', '')
        self.path = kwargs.get('path', '')
        return super().initialize_request(request, *args, **kwargs)

    def get_permissions(self):
        # API root
        if not self.service:
            return [AllowAny()]

        # Servicio de usuarios - registro sin autenticación
        if self.service == 'usuarios' and self.request.method == 'POST' and not self.path:
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