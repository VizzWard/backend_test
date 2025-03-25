from rest_framework import serializers
from .models import Cuenta, Transaccion


class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = ['id', 'numero_cuenta', 'propietario', 'saldo', 'ultima_actualizacion']
        read_only_fields = ['ultima_actualizacion']


class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = ['id', 'cuenta', 'tipo', 'cantidad', 'fecha', 'saldo_resultante']
        read_only_fields = ['fecha', 'saldo_resultante']


class RealizarTransaccionSerializer(serializers.Serializer):
    cuenta_id = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=Transaccion.TIPOS_TRANSACCION)
    cantidad = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser positiva")
        return value