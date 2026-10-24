from decimal import Decimal
from unittest import mock

import pytest
from django.contrib.auth.hashers import get_hasher, identify_hasher

from apps.comun.errores import ErrorNegocio
from apps.usuarios.models import Usuario
from apps.usuarios.servicios import paso_onboarding_pendiente, registrar_usuario
from apps.usuarios.validadores import MENSAJE_POLITICA_CONTRASENA
from tests.fabricas import crear_localidad, crear_preferencia, crear_usuario

pytestmark = pytest.mark.django_db


def registrar(**campos) -> Usuario:
    datos = {
        "nombre": "Tomás",
        "apellido": "Ríos",
        "email": "tomas.rios@example.com",
        "contrasena": "clave1234",
    }
    datos.update(campos)
    return registrar_usuario(**datos)


@pytest.mark.parametrize("email", ["tomas.rios@example.com", "Tomas.Rios@Example.COM"])
def test_hu001_c1_rechaza_correo_registrado(email):
    crear_usuario(email="tomas.rios@example.com")

    with pytest.raises(ErrorNegocio) as error:
        registrar(email=email)

    assert error.value.campo == "email"
    assert error.value.mensaje == "Este correo ya está registrado."
    assert Usuario.objects.count() == 1


@pytest.mark.parametrize("contrasena", ["clave12", "a1" + "x" * 63, "sinnumeros", "12345678"])
def test_hu001_c2_rechaza_contrasena_fuera_de_politica(contrasena):
    with pytest.raises(ErrorNegocio) as error:
        registrar(contrasena=contrasena)

    assert error.value.campo == "contrasena"
    assert error.value.mensaje == MENSAJE_POLITICA_CONTRASENA
    assert not Usuario.objects.exists()


def test_hu001_p2_acepta_otros_caracteres_en_la_contrasena():
    usuario = registrar(contrasena="Pádel 2 vs 2!")

    assert usuario.check_password("Pádel 2 vs 2!")


def test_hu001_p3_guarda_correo_en_minusculas():
    usuario = registrar(email="  Tomas.Rios@Example.COM ")

    usuario.refresh_from_db()
    assert usuario.email == "tomas.rios@example.com"


def test_hu001_p3_correo_repetido_por_registro_simultaneo():
    crear_usuario(email="tomas.rios@example.com")

    # Simula que el otro registro entró después de la verificación previa.
    with mock.patch("apps.usuarios.servicios.validar_correo_disponible"):
        with pytest.raises(ErrorNegocio) as error:
            registrar()

    assert error.value.campo == "email"
    assert error.value.mensaje == "Este correo ya está registrado."


def test_hu001_p4_guarda_contrasena_hasheada():
    usuario = registrar(contrasena="clave1234")

    usuario.refresh_from_db()
    assert usuario.password != "clave1234"
    assert identify_hasher(usuario.password).algorithm == get_hasher("default").algorithm
    assert usuario.check_password("clave1234")


def test_hu001_registro_crea_jugador_con_perfil_incompleto():
    usuario = registrar()

    assert usuario.nombre == "Tomás"
    assert usuario.apellido == "Ríos"
    assert usuario.is_active
    assert not usuario.is_staff
    assert paso_onboarding_pendiente(usuario) == "perfil"


def test_onboarding_sin_paso_pendiente_con_perfil_y_preferencia():
    usuario = crear_usuario(localidad=crear_localidad(), nivel_estimado=Decimal("3.5"))
    crear_preferencia(usuario)

    assert paso_onboarding_pendiente(usuario) is None
