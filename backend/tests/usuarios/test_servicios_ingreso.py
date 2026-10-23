import pytest

from apps.comun.errores import ErrorNegocio
from apps.usuarios.servicios import autenticar_usuario
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

MENSAJE_CREDENCIALES_INVALIDAS = "Las credenciales ingresadas no son válidas."


@pytest.mark.parametrize(
    "email", ["tomas.rios@example.com", "Tomas.Rios@Example.COM", " tomas.rios@example.com "]
)
def test_hu002_c1_autentica_con_credenciales_correctas(email):
    usuario = crear_usuario(email="tomas.rios@example.com", password="clave1234")

    assert autenticar_usuario(email, "clave1234") == usuario


def test_hu002_c2_rechaza_contrasena_incorrecta():
    crear_usuario(email="tomas.rios@example.com", password="clave1234")

    with pytest.raises(ErrorNegocio) as error:
        autenticar_usuario("tomas.rios@example.com", "clave12345")

    assert error.value.campo is None
    assert error.value.mensaje == MENSAJE_CREDENCIALES_INVALIDAS


def test_hu002_c3_rechaza_correo_no_registrado_con_el_mismo_mensaje():
    crear_usuario(email="tomas.rios@example.com", password="clave1234")

    with pytest.raises(ErrorNegocio) as error:
        autenticar_usuario("valentina.sosa@example.com", "clave1234")

    assert error.value.campo is None
    assert error.value.mensaje == MENSAJE_CREDENCIALES_INVALIDAS


def test_ingreso_rechaza_usuario_inactivo():
    crear_usuario(email="tomas.rios@example.com", password="clave1234", is_active=False)

    with pytest.raises(ErrorNegocio) as error:
        autenticar_usuario("tomas.rios@example.com", "clave1234")

    assert error.value.mensaje == MENSAJE_CREDENCIALES_INVALIDAS
