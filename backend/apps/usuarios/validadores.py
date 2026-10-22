from django.core.exceptions import ValidationError

LARGO_MINIMO_CONTRASENA = 8
LARGO_MAXIMO_CONTRASENA = 64
MENSAJE_POLITICA_CONTRASENA = (
    "La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número."
)


class ValidadorPoliticaContrasena:
    """Política de contraseña de parejo: 8 a 64 caracteres, al menos una letra y un número."""

    def validate(self, password, user=None):
        largo_valido = LARGO_MINIMO_CONTRASENA <= len(password) <= LARGO_MAXIMO_CONTRASENA
        tiene_letra = any(caracter.isalpha() for caracter in password)
        tiene_numero = any(caracter.isdigit() for caracter in password)
        if not (largo_valido and tiene_letra and tiene_numero):
            raise ValidationError(MENSAJE_POLITICA_CONTRASENA, code="politica_contrasena")

    def get_help_text(self):
        return MENSAJE_POLITICA_CONTRASENA
