from decimal import Decimal

from rest_framework import serializers

from apps.comun.errores import ErrorNegocio
from apps.localidades import servicios as servicios_localidades
from apps.usuarios import servicios
from apps.usuarios.models import FrecuenciaJuego, Genero

MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
MENSAJE_CORREO_INVALIDO = "Ingresá un correo válido."
MENSAJE_LARGO_MAXIMO = "Usá como máximo {max_length} caracteres."
MENSAJE_EDAD_INVALIDA = "Ingresá una edad entre 18 y 99."
MENSAJE_OPCION_INVALIDA = "Elegí una opción del listado."
MENSAJE_NIVEL_INVALIDO = "Elegí un nivel entre 1,0 y 7,0, en pasos de 0,5."

MENSAJES_CAMPO_OBLIGATORIO = {
    "required": MENSAJE_CAMPO_VACIO,
    "blank": MENSAJE_CAMPO_VACIO,
    "null": MENSAJE_CAMPO_VACIO,
}
MENSAJES_NOMBRE = {**MENSAJES_CAMPO_OBLIGATORIO, "max_length": MENSAJE_LARGO_MAXIMO}
MENSAJES_EDAD = {
    **MENSAJES_CAMPO_OBLIGATORIO,
    **dict.fromkeys(
        ("invalid", "min_value", "max_value", "max_string_length"), MENSAJE_EDAD_INVALIDA
    ),
}
MENSAJES_OPCION = {**MENSAJES_CAMPO_OBLIGATORIO, "invalid_choice": MENSAJE_OPCION_INVALIDA}
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

    def get_onboarding(self, usuario):
        return servicios.paso_onboarding_pendiente(usuario)


class CampoLocalidad(serializers.IntegerField):
    """Recibe el id de una localidad del catálogo y entrega la Localidad; se muestra como id."""

    def to_internal_value(self, data):
        id_localidad = super().to_internal_value(data)
        try:
            return servicios_localidades.obtener_localidad(id_localidad)
        except ErrorNegocio as error:
            raise serializers.ValidationError(error.mensaje) from error

    def get_attribute(self, usuario):
        # El id alcanza para responder; leer `usuario.localidad` haría otra consulta.
        return usuario.localidad_id


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


class DisponibilidadSerializer(serializers.Serializer):
    # La HU-005 suma las franjas, las preferencias y su edición.
    disponible_para_invitaciones = serializers.BooleanField(read_only=True)


class PerfilSerializer(serializers.Serializer):
    """Respuesta de `GET perfil` y `PATCH perfil`, agrupada en las secciones de la pantalla."""

    datos_personales = DatosPersonalesSerializer(source="*")
    perfil_deportivo = PerfilDeportivoSerializer(source="*")
    disponibilidad = DisponibilidadSerializer(source="*")


class ActualizarPerfilSerializer(serializers.Serializer):
    """Entrada de `PATCH perfil`: solo las secciones que cambian, cada una completa."""

    datos_personales = DatosPersonalesSerializer(required=False)
    perfil_deportivo = PerfilDeportivoSerializer(required=False)
