from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Orden, DetalleOrden
from .serializers import OrdenSerializer, DetalleOrdenSerializer

# Create your views here.
class OrdenViewSet(viewsets.ModelViewSet):
    serializer_class = OrdenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        return Orden.objects.filter(usuario_id=user_id)

    def perform_create(self, serializer):
        serializer.save(usuario_id=self.request.user.id)