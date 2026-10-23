import base64

import pytest
from django.core import mail

from apps.comun.errores import ErrorNegocio
from apps.usuarios.servicios import (
    autenticar_usuario,
    enlace_recuperacion,
    restablecer_contrasena,
    solicitar_recuperacion,
    usuario_por_enlace,
)
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

URL_FRONTEND = "http://localhost:5173"
MENSAJE_CUENTA_INEXISTENTE = "La cuenta no existe. Revisá el correo ingresado."
MENSAJE_ENLACE_INVALIDO = "El enlace no es válido."
MENSAJE_POLITICA = (
    "La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número."
)


@pytest.fixture(autouse=True)
def url_frontend(settings):
    settings.URL_FRONTEND = URL_FRONTEND


@pytest.fixture
def usuario():
    return crear_usuario(email="tomas.rios@example.com", password="clave1234", nombre="Tomás")


def partes_del_enlace(enlace: str) -> tuple[str, str]:
    uid, token = enlace.removeprefix(f"{URL_FRONTEND}/recuperar/").split("/")
    return uid, token


def uid_de(texto: str) -> str:
    return base64.urlsafe_b64encode(texto.encode()).decode().rstrip("=")


def test_hu003_c1_envia_correo_con_enlace(usuario):
    solicitar_recuperacion("tomas.rios@example.com")

    assert len(mail.outbox) == 1
    correo = mail.outbox[0]
    assert correo.to == ["tomas.rios@example.com"]
    assert correo.subject == "Restablecé tu contraseña de parejo"
    assert correo.body.startswith("Hola, Tomás:")
    assert "Si no lo pediste, podés ignorar este correo." in correo.body
    enlace = next(linea for linea in correo.body.splitlines() if linea.startswith("http"))
    assert usuario_por_enlace(*partes_del_enlace(enlace)) == usuario


@pytest.mark.parametrize("email", ["Tomas.Rios@Example.COM", " tomas.rios@example.com "])
def test_hu003_c1_acepta_el_correo_en_cualquier_formato(usuario, email):
    solicitar_recuperacion(email)

    assert mail.outbox[0].to == ["tomas.rios@example.com"]


def test_hu003_p4_enlace_apunta_al_frontend(usuario):
    enlace = enlace_recuperacion(usuario)

    assert enlace.startswith(f"{URL_FRONTEND}/recuperar/")
    assert usuario_por_enlace(*partes_del_enlace(enlace)) == usuario


@pytest.mark.parametrize("email", ["valentina.sosa@example.com", "tomas.rios", ""])
def test_hu003_c2_rechaza_correo_no_registrado(usuario, email):
    with pytest.raises(ErrorNegocio) as error:
        solicitar_recuperacion(email)

    assert error.value.campo == "email"
    assert error.value.mensaje == MENSAJE_CUENTA_INEXISTENTE
    assert mail.outbox == []


def test_hu003_c2_trata_la_cuenta_inactiva_como_inexistente():
    crear_usuario(email="tomas.rios@example.com", is_active=False)

    with pytest.raises(ErrorNegocio) as error:
        solicitar_recuperacion("tomas.rios@example.com")

    assert error.value.mensaje == MENSAJE_CUENTA_INEXISTENTE
    assert mail.outbox == []


def test_hu003_c3_puede_ingresar_con_la_nueva_contrasena(usuario):
    uid, token = partes_del_enlace(enlace_recuperacion(usuario))

    assert restablecer_contrasena(uid, token, "nueva5678") == usuario

    assert autenticar_usuario("tomas.rios@example.com", "nueva5678") == usuario
    with pytest.raises(ErrorNegocio):
        autenticar_usuario("tomas.rios@example.com", "clave1234")


@pytest.mark.parametrize("contrasena", ["corta1", "sololetras", "12345678", "a1" * 33])
def test_hu003_p2_nueva_contrasena_cumple_la_politica(usuario, contrasena):
    uid, token = partes_del_enlace(enlace_recuperacion(usuario))

    with pytest.raises(ErrorNegocio) as error:
        restablecer_contrasena(uid, token, contrasena)

    assert error.value.campo == "contrasena"
    assert error.value.mensaje == MENSAJE_POLITICA
    assert autenticar_usuario("tomas.rios@example.com", "clave1234") == usuario
    assert usuario_por_enlace(uid, token) == usuario


def test_hu003_p3_enlace_deja_de_servir_una_vez_usado(usuario):
    uid, token = partes_del_enlace(enlace_recuperacion(usuario))
    restablecer_contrasena(uid, token, "nueva5678")

    with pytest.raises(ErrorNegocio) as al_validar:
        usuario_por_enlace(uid, token)
    with pytest.raises(ErrorNegocio) as al_restablecer:
        restablecer_contrasena(uid, token, "otra9012")

    assert al_validar.value.mensaje == MENSAJE_ENLACE_INVALIDO
    assert al_validar.value.campo is None
    assert al_restablecer.value.mensaje == MENSAJE_ENLACE_INVALIDO
    assert autenticar_usuario("tomas.rios@example.com", "nueva5678") == usuario


def test_hu003_p3_rechaza_el_token_de_otro_usuario(usuario):
    otro = crear_usuario(email="valentina.sosa@example.com")
    uid, _ = partes_del_enlace(enlace_recuperacion(usuario))
    _, token_ajeno = partes_del_enlace(enlace_recuperacion(otro))

    with pytest.raises(ErrorNegocio) as error:
        usuario_por_enlace(uid, token_ajeno)

    assert error.value.mensaje == MENSAJE_ENLACE_INVALIDO


@pytest.mark.parametrize(
    ("uid", "token"),
    [
        ("%%%", "token"),
        (uid_de("abc"), "token"),
        (uid_de("999999"), "token"),
        (uid_de("99999999999"), "token"),
        (uid_de("-1"), "token"),
        (None, "token-alterado"),
    ],
)
def test_hu003_p3_rechaza_enlace_invalido(usuario, uid, token):
    uid = uid or partes_del_enlace(enlace_recuperacion(usuario))[0]

    with pytest.raises(ErrorNegocio) as error:
        usuario_por_enlace(uid, token)

    assert error.value.mensaje == MENSAJE_ENLACE_INVALIDO


def test_hu003_p3_rechaza_enlace_de_cuenta_inactiva(usuario):
    uid, token = partes_del_enlace(enlace_recuperacion(usuario))
    usuario.is_active = False
    usuario.save()

    with pytest.raises(ErrorNegocio):
        restablecer_contrasena(uid, token, "nueva5678")
