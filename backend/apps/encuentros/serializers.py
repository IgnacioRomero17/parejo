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
MENSAJE_SIN_SELECCION = "Seleccioná al menos un jugador."


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


class FranjaRecomendadoSerializer(serializers.Serializer):
    dia_semana = serializers.IntegerField(source="dia")
    hora_inicio = serializers.TimeField(source="inicio", format="%H:%M")
    hora_fin = serializers.TimeField(source="fin", format="%H:%M")


class JugadorRecomendadoSerializer(serializers.Serializer):
    """Lo que la pantalla 10 muestra de cada recomendado; el puntaje no se expone."""

    id = serializers.IntegerField(source="usuario.id_usuario")
    nombre = serializers.CharField(source="usuario.nombre")
    apellido = serializers.CharField(source="usuario.apellido")
    localidad = LocalidadSerializer(source="usuario.localidad")
    nivel = serializers.DecimalField(
        source="usuario.nivel_estimado", max_digits=2, decimal_places=1
    )
    franja = FranjaRecomendadoSerializer()


class RecomendadosSerializer(serializers.Serializer):
    """Respuesta de `GET encuentros/{id}/recomendados`, en el orden del motor."""

    lugares_libres = serializers.IntegerField()
    suficientes = serializers.BooleanField()
    recomendados = JugadorRecomendadoSerializer(source="jugadores", many=True)


class JugadorSerializer(serializers.Serializer):
    """Un jugador como lo muestran las listas del encuentro: nombre, localidad y nivel."""

    id = serializers.IntegerField(source="id_usuario")
    nombre = serializers.CharField()
    apellido = serializers.CharField()
    localidad = LocalidadSerializer()
    nivel = serializers.DecimalField(source="nivel_estimado", max_digits=2, decimal_places=1)


class ParticipanteSerializer(JugadorSerializer):
    lado = serializers.CharField(source="preferencia.lado_preferido")


class InvitacionEnviadaSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="id_invitacion")
    jugador = JugadorSerializer(source="usuario_invitado")
    estado = serializers.CharField()
    fecha_envio = serializers.DateTimeField()


class DetalleEncuentroSerializer(serializers.Serializer):
    """Respuesta de `GET encuentros/{id}`: el encuentro, sus lugares, sus participantes y, solo
    para el organizador, las invitaciones enviadas."""

    def to_representation(self, detalle):
        datos = EncuentroSerializer(detalle.encuentro).data
        datos["lugares_libres"] = detalle.lugares_libres
        datos["participantes"] = ParticipanteSerializer(
            [participante.usuario for participante in detalle.participantes], many=True
        ).data
        if detalle.invitaciones is not None:
            datos["invitaciones"] = InvitacionEnviadaSerializer(
                detalle.invitaciones, many=True
            ).data
        return datos


class CampoIdsJugadores(serializers.ListField):
    """Lista de ids de jugadores; un id inválido se informa con un solo mensaje para el campo,
    no uno por posición, para respetar el formato `{"campo": ["mensaje"]}`."""

    child = serializers.IntegerField(min_value=1)

    def run_child_validation(self, data):
        try:
            return super().run_child_validation(data)
        except serializers.ValidationError as error:
            raise serializers.ValidationError(MENSAJE_OPCION_INVALIDA) from error


class InvitarSerializer(serializers.Serializer):
    """Entrada de `POST encuentros/{id}/invitaciones`: los ids de los jugadores elegidos."""

    usuarios = CampoIdsJugadores(
        allow_empty=False,
        error_messages={
            **MENSAJES_CAMPO_OBLIGATORIO,
            "not_a_list": MENSAJE_OPCION_INVALIDA,
            "empty": MENSAJE_SIN_SELECCION,
        },
    )

    def validate_usuarios(self, valor):
        if len(set(valor)) != len(valor):
            raise serializers.ValidationError(MENSAJE_OPCION_INVALIDA)
        return valor


class OrganizadorSerializer(serializers.Serializer):
    """El organizador de una invitación recibida; el género define cómo se lo nombra."""

    id = serializers.IntegerField(source="id_usuario")
    nombre = serializers.CharField()
    apellido = serializers.CharField()
    genero = serializers.CharField()


class EncuentroInvitacionSerializer(EncuentroSerializer):
    # Los confirmados vienen contados en la consulta de la bandeja (`confirmados`).
    confirmados = serializers.IntegerField()


class InvitacionRecibidaSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="id_invitacion")
    estado = serializers.CharField()
    fecha_envio = serializers.DateTimeField()
    organizador = OrganizadorSerializer(source="encuentro.organizador")
    encuentro = EncuentroInvitacionSerializer()


class BandejaSerializer(serializers.Serializer):
    """Respuesta de `GET invitaciones`."""

    pendientes = InvitacionRecibidaSerializer(many=True)
    respondidas = InvitacionRecibidaSerializer(many=True)


class EncuentroActivoSerializer(EncuentroInvitacionSerializer):
    """Un encuentro de `GET encuentros` (pantalla 08). Recibe en el contexto el `usuario` que
    consulta: `invitaciones_pendientes` (contadas en la consulta) va solo si lo organiza."""

    organizador = OrganizadorSerializer()

    def to_representation(self, encuentro):
        datos = super().to_representation(encuentro)
        organizas = servicios.es_organizador(self.context["usuario"], encuentro)
        datos["organizas"] = organizas
        if organizas:
            datos["invitaciones_pendientes"] = encuentro.invitaciones_pendientes
        return datos


class ParejaSerializer(serializers.Serializer):
    numero = serializers.IntegerField()
    promedio = serializers.FloatField()
    integrantes = ParticipanteSerializer(many=True)


class CombinacionSerializer(serializers.Serializer):
    """Una combinación evaluada: el puntaje es el guardado; promedios y equilibrios, los
    recalculados con el nivel y el lado actuales."""

    numero = serializers.IntegerField()
    puntaje_equilibrio = serializers.DecimalField(max_digits=5, decimal_places=4)
    equilibrio_nivel = serializers.FloatField()
    equilibrio_lado = serializers.FloatField()
    parejas = ParejaSerializer(many=True)


class PropuestaSerializer(serializers.Serializer):
    """Respuesta de `POST encuentros/{id}/formar-parejas` y `GET encuentros/{id}/propuesta`: el
    encuentro, las 3 combinaciones y el número y el puntaje guardado de la elegida."""

    encuentro = EncuentroSerializer()
    combinacion_elegida = serializers.IntegerField()
    puntaje_equilibrio = serializers.DecimalField(max_digits=5, decimal_places=4)
    combinaciones = CombinacionSerializer(many=True)
