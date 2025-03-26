from django.shortcuts import render
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
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.service = kwargs.get('service')
        self.path = kwargs.get('path', '')

    def get_permissions(self):
        if self.service == 'usuarios' and self.request.method == 'POST' and not self.path:
            # Permitir registro de usuarios sin autenticación
            return [AllowAny()]
        elif self.service == 'productos' and self.request.method == 'GET':
            # Permitir ver productos sin autenticación
            return [AllowAny()]
        return [IsAuthenticated()]

    def handle_request(self, request, *args, **kwargs):
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