from decimal import Decimal

from rest_framework import serializers

from apps.comun.errores import ErrorNegocio
from apps.comun.horarios import MENSAJE_HORA_INVALIDA
from apps.comun.mensajes import (
    MENSAJE_LARGO_MAXIMO,
    MENSAJE_OPCION_INVALIDA,
    MENSAJES_CAMPO_OBLIGATORIO,
    MENSAJES_OPCION,
)
from apps.encuentros import servicios as servicios_encuentros
from apps.localidades.serializers import CampoLocalidad
from apps.usuarios import servicios
from apps.usuarios.models import DiaSemana, FrecuenciaJuego, Genero, LadoPreferido, TipoEncuentro

MENSAJE_CORREO_INVALIDO = "Ingresá un correo válido."
MENSAJE_EDAD_INVALIDA = "Ingresá una edad entre 18 y 99."
MENSAJE_NIVEL_INVALIDO = "Elegí un nivel entre 1,0 y 7,0, en pasos de 0,5."

MENSAJES_NOMBRE = {**MENSAJES_CAMPO_OBLIGATORIO, "max_length": MENSAJE_LARGO_MAXIMO}
MENSAJES_EDAD = {
    **MENSAJES_CAMPO_OBLIGATORIO,
    **dict.fromkeys(
        ("invalid", "min_value", "max_value", "max_string_length"), MENSAJE_EDAD_INVALIDA
    ),
}
MENSAJES_HORA = {**MENSAJES_CAMPO_OBLIGATORIO, "invalid": MENSAJE_HORA_INVALIDA}
# Solo llegan desde fuera de la pantalla: una lista o un valor con un tipo que no corresponde.
MENSAJES_DATO_MAL_FORMADO = {
    **MENSAJES_CAMPO_OBLIGATORIO,
    **dict.fromkeys(("invalid", "not_a_list"), MENSAJE_OPCION_INVALIDA),
}
MENSAJES_NIVEL = {
    **MENSAJES_CAMPO_OBLIGATORIO,
    **dict.fromkeys(
        (
            "invalid",
            "min_value",
            "max_value",
            "max_digits",
            "max_decimal_places",
            "max_whole_digits",
            "max_string_length",
        ),
        MENSAJE_NIVEL_INVALIDO,
    ),
}


class RegistroSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=60, error_messages=MENSAJES_NOMBRE)
    apellido = serializers.CharField(max_length=60, error_messages=MENSAJES_NOMBRE)
    email = serializers.EmailField(
        max_length=254,
        error_messages={
            **MENSAJES_CAMPO_OBLIGATORIO,
            "invalid": MENSAJE_CORREO_INVALIDO,
            "max_length": MENSAJE_CORREO_INVALIDO,
        },
    )
    contrasena = serializers.CharField(
        write_only=True, trim_whitespace=False, error_messages=MENSAJES_CAMPO_OBLIGATORIO
    )

    # El servicio vuelve a verificar ambas reglas; acá se adelantan para devolver todos los
    # errores de campo juntos (por ejemplo, correo repetido y contraseña inválida a la vez).
    def validate_email(self, valor):
        valor = servicios.normalizar_correo(valor)
        try:
            servicios.validar_correo_disponible(valor)
        except ErrorNegocio as error:
            raise serializers.ValidationError(error.mensaje) from error
        return valor

    def validate_contrasena(self, valor):
        try:
            servicios.validar_contrasena(valor)
        except ErrorNegocio as error:
            raise serializers.ValidationError(error.mensaje) from error
        return valor


class IngresoSerializer(serializers.Serializer):
    # CharField y no EmailField: un correo mal formado tampoco está registrado y recibe el
    # mensaje de credenciales inválidas, no un error de formato (HU-002, criterio 3).
    email = serializers.CharField(error_messages=MENSAJES_CAMPO_OBLIGATORIO)
    contrasena = serializers.CharField(
        write_only=True, trim_whitespace=False, error_messages=MENSAJES_CAMPO_OBLIGATORIO
    )


class RecuperacionSerializer(serializers.Serializer):
    # CharField por el mismo motivo que en el ingreso: un correo mal formado tampoco está
    # registrado y recibe "La cuenta no existe" (HU-003, criterio 2).
    email = serializers.CharField(error_messages=MENSAJES_CAMPO_OBLIGATORIO)


class ConfirmarRecuperacionSerializer(serializers.Serializer):
    uid = serializers.CharField(error_messages=MENSAJES_CAMPO_OBLIGATORIO)
    token = serializers.CharField(error_messages=MENSAJES_CAMPO_OBLIGATORIO)
    contrasena = serializers.CharField(
        write_only=True, trim_whitespace=False, error_messages=MENSAJES_CAMPO_OBLIGATORIO
    )


class CuentaRecuperacionSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UsuarioActualSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="id_usuario")
    nombre = serializers.CharField()
    apellido = serializers.CharField()
    email = serializers.EmailField()
    onboarding = serializers.SerializerMethodField()
    invitaciones_pendientes = serializers.SerializerMethodField()

    def get_onboarding(self, usuario):
        return servicios.paso_onboarding_pendiente(usuario)

    def get_invitaciones_pendientes(self, usuario):
        # Para el indicador de la barra superior; se lee por el servicio de encuentros.
        return servicios_encuentros.cantidad_invitaciones_pendientes(usuario)


class DatosPersonalesSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=60, error_messages=MENSAJES_NOMBRE)
    apellido = serializers.CharField(max_length=60, error_messages=MENSAJES_NOMBRE)
    # Sin HU para cambiar el correo: solo se muestra.
    email = serializers.EmailField(read_only=True)


class PerfilDeportivoSerializer(serializers.Serializer):
    edad = serializers.IntegerField(min_value=18, max_value=99, error_messages=MENSAJES_EDAD)
    genero = serializers.ChoiceField(choices=Genero.choices, error_messages=MENSAJES_OPCION)
    localidad = CampoLocalidad(
        error_messages={**MENSAJES_CAMPO_OBLIGATORIO, "invalid": MENSAJE_OPCION_INVALIDA}
    )
    frecuencia_juego = serializers.ChoiceField(
        choices=FrecuenciaJuego.choices, error_messages=MENSAJES_OPCION
    )
    nivel_estimado = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
        min_value=Decimal("1.0"),
        max_value=Decimal("7.0"),
        error_messages=MENSAJES_NIVEL,
    )

    def validate_nivel_estimado(self, valor):
        if valor * 2 % 1 != 0:
            raise serializers.ValidationError(MENSAJE_NIVEL_INVALIDO)
        return valor


def _error_de_campo(error: ErrorNegocio) -> serializers.ValidationError:
    return serializers.ValidationError({error.campo: [error.mensaje]})


class FranjaSerializer(serializers.Serializer):
    dia_semana = serializers.ChoiceField(choices=DiaSemana.choices, error_messages=MENSAJES_OPCION)
    hora_inicio = serializers.TimeField(
        format="%H:%M", input_formats=["%H:%M"], error_messages=MENSAJES_HORA
    )
    hora_fin = serializers.TimeField(
        format="%H:%M", input_formats=["%H:%M"], error_messages=MENSAJES_HORA
    )

    # El servicio vuelve a verificar la franja; acá se adelanta para marcar cada fila.
    def validate(self, datos):
        try:
            servicios.validar_franja(datos["hora_inicio"], datos["hora_fin"])
        except ErrorNegocio as error:
            raise _error_de_campo(error) from error
        return datos


class DisponibilidadSerializer(serializers.Serializer):
    """Entrada de la sección "Disponibilidad y preferencias", siempre completa (HU-005)."""

    franjas = FranjaSerializer(many=True, error_messages=MENSAJES_DATO_MAL_FORMADO)
    tipo_encuentro = serializers.ChoiceField(
        choices=TipoEncuentro.choices, error_messages=MENSAJES_OPCION
    )
    lado_preferido = serializers.ChoiceField(
        choices=LadoPreferido.choices, error_messages=MENSAJES_OPCION
    )
    disponible_para_invitaciones = serializers.BooleanField(
        error_messages=MENSAJES_DATO_MAL_FORMADO
    )

    def validate(self, datos):
        try:
            servicios.validar_disponible_con_franjas(
                datos["franjas"], datos["disponible_para_invitaciones"]
            )
        except ErrorNegocio as error:
            raise _error_de_campo(error) from error
        return datos


class CampoPreferencia(serializers.ReadOnlyField):
    """Un dato de la preferencia del usuario; null mientras no la guardó en el onboarding."""

    def get_attribute(self, usuario):
        preferencia = getattr(usuario, "preferencia", None)
        return getattr(preferencia, self.source, None)


class DisponibilidadGuardadaSerializer(serializers.Serializer):
    franjas = FranjaSerializer(many=True, source="disponibilidades")
    tipo_encuentro = CampoPreferencia()
    lado_preferido = CampoPreferencia()
    disponible_para_invitaciones = serializers.BooleanField()


class PerfilSerializer(serializers.Serializer):
    """Respuesta de `GET perfil` y `PATCH perfil`, agrupada en las secciones de la pantalla."""

    datos_personales = DatosPersonalesSerializer(source="*")
    perfil_deportivo = PerfilDeportivoSerializer(source="*")
    disponibilidad = DisponibilidadGuardadaSerializer(source="*")


class ActualizarPerfilSerializer(serializers.Serializer):
    """Entrada de `PATCH perfil`: solo las secciones que cambian, cada una completa."""

    datos_personales = DatosPersonalesSerializer(required=False)
    perfil_deportivo = PerfilDeportivoSerializer(required=False)
    disponibilidad = DisponibilidadSerializer(required=False)
