from django.shortcuts import render
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# Create your views here.
class VisitThrottle(UserRateThrottle):
    rate = '10/minute'  # Sobrescribe la configuración global para este endpoint específico
    scope = 'visit'

class AnonVisitThrottle(AnonRateThrottle):
    rate = '5/minute'  # Para usuarios no autenticados
    scope = 'anon_visit'

# Implementamos la vista que registrará las visitas
class VisitView(APIView):
    throttle_classes = [VisitThrottle, AnonVisitThrottle]

    def get(self, request, format=None):
        """
        Endpoint que registra una visita.
        Se limita a 10 solicitudes por minuto por usuario autenticado,
        o 5 solicitudes por minuto para usuarios anónimos.
        """
        # Aquí podríamos registrar la visita en la base de datos si fuera necesario

        # Devolvemos una respuesta exitosa
        return Response({
            'message': 'Visita registrada correctamente',
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)