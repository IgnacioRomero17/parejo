import pytest
from django.core.exceptions import ValidationError

from apps.usuarios.validadores import MENSAJE_POLITICA_CONTRASENA, ValidadorPoliticaContrasena


@pytest.mark.parametrize("contrasena", ["abcdefg1", "a1" + "x" * 62, "clave 1234!ñ", "ÑANDÚ123"])
def test_validador_contrasena_acepta_dentro_de_la_politica(contrasena):
    ValidadorPoliticaContrasena().validate(contrasena)


@pytest.mark.parametrize(
    "contrasena",
    ["abcdef1", "a1" + "x" * 63, "abcdefgh", "12345678", "!!!!!!!!", ""],
)
def test_validador_contrasena_rechaza_fuera_de_la_politica(contrasena):
    with pytest.raises(ValidationError) as error:
        ValidadorPoliticaContrasena().validate(contrasena)

    assert error.value.messages == [MENSAJE_POLITICA_CONTRASENA]
