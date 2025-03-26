from rest_framework import serializers
from .models import Orden, DetalleOrden
import requests

from rest_framework import serializers
from .models import Orden, DetalleOrden
import requests
from .services import UsuariosService, ProductosService


class DetalleOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleOrden
        fields = [
            'id', 'producto_id', 'producto_nombre',
            'cantidad', 'precio_unitario', 'subtotal'
        ]


class OrdenSerializer(serializers.ModelSerializer):
    detalles = DetalleOrdenSerializer(many=True, read_only=True)
    detalles_datos = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Orden
        fields = [
            'id', 'usuario_id', 'fecha_creacion',
            'fecha_actualizacion','estado', 'direccion_envio',
            'total', 'detalles', 'detalles_datos'
        ]

    def validate(self, data):
        # Obtenemos el token del contexto
        request = self.context.get('request')
        if not request or not hasattr(request, 'META'):
            raise serializers.ValidationError("No se pudo obtener información de la solicitud")

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            raise serializers.ValidationError("Se requiere token de autenticación")

        token = auth_header.split(' ')[1]

        # Verificar si el usuario existe
        usuario_id = data.get('usuario_id')
        if usuario_id and not UsuariosService.verify_user_exists(usuario_id, token):
            raise serializers.ValidationError({"usuario_id": "El usuario no existe"})

        # Verificar stock de productos
        detalles_datos = data.get('detalles_datos', [])
        for detalle in detalles_datos:
            producto_id = detalle.get('producto_id')
            cantidad = detalle.get('cantidad', 0)

            if not ProductosService.verify_product_exists(producto_id, token):
                raise serializers.ValidationError(
                    {"detalles_datos": f"El producto con ID {producto_id} no existe"}
                )

            if not ProductosService.verify_product_stock(producto_id, cantidad, token):
                raise serializers.ValidationError(
                    {"detalles_datos": f"Stock insuficiente para el producto con ID {producto_id}"}
                )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]

        detalles_datos = validated_data.pop('detalles_datos', [])
        orden = Orden.objects.create(**validated_data)

        total = 0
        for detalle_dato in detalles_datos:
            producto_id = detalle_dato['producto_id']
            cantidad = detalle_dato['cantidad']

            # Obtener datos actualizados del producto
            producto_data = ProductosService.get_product(producto_id, token)

            if producto_data:
                # Usar el precio actual del producto
                precio_actual = producto_data.get('precio', detalle_dato['precio_unitario'])
                nombre_producto = producto_data.get('nombre', detalle_dato['producto_nombre'])

                subtotal = cantidad * precio_actual

                DetalleOrden.objects.create(
                    orden=orden,
                    producto_id=producto_id,
                    producto_nombre=nombre_producto,
                    cantidad=cantidad,
                    precio_unitario=precio_actual,
                    subtotal=subtotal
                )

                # Actualizar el stock del producto
                ProductosService.update_product_stock(producto_id, cantidad, token)

                total += subtotal

        orden.total = total
        orden.save()
        return orden