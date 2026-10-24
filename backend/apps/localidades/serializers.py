from rest_framework import serializers

from apps.comun.errores import ErrorNegocio
from apps.localidades import servicios


class LocalidadSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="id_localidad")
    nombre = serializers.CharField()


class CampoLocalidad(serializers.IntegerField):
    """Recibe el id de una localidad del catálogo y entrega la Localidad; se muestra como id.

    Sirve para cualquier objeto con una clave foránea `localidad` (usuario, encuentro).
    """

    def to_internal_value(self, data):
        id_localidad = super().to_internal_value(data)
        try:
            return servicios.obtener_localidad(id_localidad)
        except ErrorNegocio as error:
            raise serializers.ValidationError(error.mensaje) from error

    def get_attribute(self, instancia):
        # El id alcanza para responder; leer `instancia.localidad` haría otra consulta.
        return instancia.localidad_id
