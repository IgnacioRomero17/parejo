from rest_framework import serializers

from apps.comun.errores import ErrorNegocio
from apps.usuarios import servicios

MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
MENSAJE_CORREO_INVALIDO = "Ingresá un correo válido."
MENSAJE_LARGO_MAXIMO = "Usá como máximo {max_length} caracteres."

MENSAJES_CAMPO_OBLIGATORIO = {
    "required": MENSAJE_CAMPO_VACIO,
    "blank": MENSAJE_CAMPO_VACIO,
    "null": MENSAJE_CAMPO_VACIO,
}


class RegistroSerializer(serializers.Serializer):
    nombre = serializers.CharField(
        max_length=60,
        error_messages={**MENSAJES_CAMPO_OBLIGATORIO, "max_length": MENSAJE_LARGO_MAXIMO},
    )
    apellido = serializers.CharField(
        max_length=60,
        error_messages={**MENSAJES_CAMPO_OBLIGATORIO, "max_length": MENSAJE_LARGO_MAXIMO},
    )
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


class UsuarioActualSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="id_usuario")
    nombre = serializers.CharField()
    apellido = serializers.CharField()
    email = serializers.EmailField()
    onboarding = serializers.SerializerMethodField()

    def get_onboarding(self, usuario):
        return servicios.paso_onboarding_pendiente(usuario)
