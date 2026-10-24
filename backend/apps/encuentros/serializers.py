from rest_framework import serializers

from apps.comun.horarios import MENSAJE_HORA_INVALIDA
from apps.comun.mensajes import (
    MENSAJE_LARGO_MAXIMO,
    MENSAJE_OPCION_INVALIDA,
    MENSAJES_CAMPO_OBLIGATORIO,
    MENSAJES_OPCION,
)
from apps.encuentros import servicios
from apps.encuentros.models import DURACIONES_MINUTOS
from apps.localidades.serializers import CampoLocalidad, LocalidadSerializer
from apps.usuarios.models import TipoEncuentro

MENSAJE_FECHA_INVALIDA = "Elegí una fecha válida."


class CrearEncuentroSerializer(serializers.Serializer):
    """Entrada de `POST encuentros`: las condiciones del encuentro, todas obligatorias."""

    fecha = serializers.DateField(
        input_formats=["iso-8601"],
        error_messages={**MENSAJES_CAMPO_OBLIGATORIO, "invalid": MENSAJE_FECHA_INVALIDA},
    )
    hora_inicio = serializers.TimeField(
        input_formats=["%H:%M"],
        error_messages={**MENSAJES_CAMPO_OBLIGATORIO, "invalid": MENSAJE_HORA_INVALIDA},
    )
    duracion_minutos = serializers.ChoiceField(
        choices=DURACIONES_MINUTOS, error_messages=MENSAJES_OPCION
    )
    localidad = CampoLocalidad(
        error_messages={**MENSAJES_CAMPO_OBLIGATORIO, "invalid": MENSAJE_OPCION_INVALIDA}
    )
    ubicacion = serializers.CharField(
        max_length=150,
        error_messages={**MENSAJES_CAMPO_OBLIGATORIO, "max_length": MENSAJE_LARGO_MAXIMO},
    )
    tipo_encuentro = serializers.ChoiceField(
        choices=TipoEncuentro.choices, error_messages=MENSAJES_OPCION
    )


class EncuentroSerializer(serializers.Serializer):
    """Respuesta con las condiciones del encuentro, su estado y los participantes confirmados."""

    id = serializers.IntegerField(source="id_encuentro")
    fecha = serializers.DateField()
    hora_inicio = serializers.TimeField(format="%H:%M")
    duracion_minutos = serializers.IntegerField()
    localidad = LocalidadSerializer()
    ubicacion = serializers.CharField()
    tipo_encuentro = serializers.CharField()
    estado = serializers.CharField()
    confirmados = serializers.SerializerMethodField()

    def get_confirmados(self, encuentro):
        return servicios.cantidad_confirmados(encuentro)
