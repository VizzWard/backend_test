from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Cuenta, Transaccion
from .serializers import CuentaSerializer, TransaccionSerializer, RealizarTransaccionSerializer


class CuentaViewSet(viewsets.ModelViewSet):
    queryset = Cuenta.objects.all()
    serializer_class = CuentaSerializer

    @action(detail=False, methods=['post'])
    def realizar_transaccion(self, request):
        serializer = RealizarTransaccionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cuenta_id = serializer.validated_data['cuenta_id']
        tipo = serializer.validated_data['tipo']
        cantidad = serializer.validated_data['cantidad']

        try:
            with transaction.atomic():
                # Usamos select_for_update para bloquear el registro durante la transacción
                cuenta = Cuenta.objects.select_for_update().get(pk=cuenta_id)

                if tipo == Transaccion.DEPOSITO:
                    nuevo_saldo = cuenta.depositar(cantidad)
                elif tipo == Transaccion.RETIRO:
                    if cuenta.saldo < cantidad:
                        return Response(
                            {"error": "Saldo insuficiente"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    nuevo_saldo = cuenta.retirar(cantidad)

                # Registrar la transacción
                transaccion = Transaccion.objects.create(
                    cuenta=cuenta,
                    tipo=tipo,
                    cantidad=cantidad,
                    saldo_resultante=nuevo_saldo
                )

                return Response({
                    "mensaje": f"Transacción realizada exitosamente",
                    "transaccion_id": transaccion.id,
                    "nuevo_saldo": nuevo_saldo
                }, status=status.HTTP_201_CREATED)

        except Cuenta.DoesNotExist:
            return Response(
                {"error": "Cuenta no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TransaccionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = TransaccionSerializer

    def get_queryset(self):
        queryset = Transaccion.objects.all()
        cuenta_id = self.request.query_params.get('cuenta_id')

        if cuenta_id:
            queryset = queryset.filter(cuenta_id=cuenta_id)

        return queryset