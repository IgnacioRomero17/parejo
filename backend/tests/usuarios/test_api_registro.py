import pytest
from django.conf import settings
from rest_framework.test import APIClient

from apps.usuarios.models import Usuario
from apps.usuarios.validadores import MENSAJE_POLITICA_CONTRASENA
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

URL_REGISTRO = "/api/auth/registro"
URL_YO = "/api/auth/yo"
URL_CSRF = "/api/auth/csrf"
MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
CAMPOS = ("nombre", "apellido", "email", "contrasena")


def datos_registro(**campos) -> dict:
    datos = {
        "nombre": "Tomás",
        "apellido": "Ríos",
        "email": "tomas.rios@example.com",
        "contrasena": "clave1234",
    }
    datos.update(campos)
    return datos


@pytest.fixture
def cliente() -> APIClient:
    return APIClient()


def test_hu001_registro_crea_la_cuenta_e_inicia_sesion(cliente):
    respuesta = cliente.post(URL_REGISTRO, datos_registro(), format="json")

    assert respuesta.status_code == 201
    usuario = Usuario.objects.get()
    assert respuesta.json() == {
        "id": usuario.id_usuario,
        "nombre": "Tomás",
        "apellido": "Ríos",
        "email": "tomas.rios@example.com",
        "onboarding": "perfil",
    }
    assert "contrasena" not in respuesta.json()

    sesion = cliente.get(URL_YO)
    assert sesion.status_code == 200
    assert sesion.json()["id"] == usuario.id_usuario


def test_hu001_p5_tras_registrarse_falta_el_paso_perfil(cliente):
    cliente.post(URL_REGISTRO, datos_registro(), format="json")

    assert cliente.get(URL_YO).json()["onboarding"] == "perfil"


def test_hu001_p3_guarda_el_correo_en_minusculas(cliente):
    respuesta = cliente.post(
        URL_REGISTRO, datos_registro(email="Tomas.Rios@Example.COM"), format="json"
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["email"] == "tomas.rios@example.com"


@pytest.mark.parametrize("email", ["tomas.rios@example.com", "TOMAS.RIOS@example.com"])
def test_hu001_c1_avisa_correo_ya_registrado(cliente, email):
    crear_usuario(email="tomas.rios@example.com")

    respuesta = cliente.post(URL_REGISTRO, datos_registro(email=email), format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"email": ["Este correo ya está registrado."]}}
    assert Usuario.objects.count() == 1


@pytest.mark.parametrize("contrasena", ["clave", "a1" + "x" * 63, "sinnumeros", "12345678"])
def test_hu001_c2_avisa_la_politica_de_contrasena(cliente, contrasena):
    respuesta = cliente.post(URL_REGISTRO, datos_registro(contrasena=contrasena), format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"contrasena": [MENSAJE_POLITICA_CONTRASENA]}}
    assert not Usuario.objects.exists()


@pytest.mark.parametrize("datos", [{}, dict.fromkeys(CAMPOS, ""), dict.fromkeys(CAMPOS)])
def test_hu001_c3_avisa_que_todos_los_campos_son_requeridos(cliente, datos):
    respuesta = cliente.post(URL_REGISTRO, datos, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": dict.fromkeys(CAMPOS, [MENSAJE_CAMPO_VACIO])}
    assert not Usuario.objects.exists()


def test_hu001_c3_campos_con_solo_espacios_cuentan_como_vacios(cliente):
    datos = datos_registro(nombre="   ", apellido=" ", email="  ")

    respuesta = cliente.post(URL_REGISTRO, datos, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "errores": dict.fromkeys(("nombre", "apellido", "email"), [MENSAJE_CAMPO_VACIO])
    }


def test_hu001_c3_avisa_un_solo_campo_incompleto(cliente):
    respuesta = cliente.post(URL_REGISTRO, datos_registro(apellido=""), format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"apellido": [MENSAJE_CAMPO_VACIO]}}


def test_hu001_muestra_varios_errores_a_la_vez(cliente):
    crear_usuario(email="tomas.rios@example.com")

    respuesta = cliente.post(URL_REGISTRO, datos_registro(contrasena="clave"), format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "errores": {
            "email": ["Este correo ya está registrado."],
            "contrasena": [MENSAJE_POLITICA_CONTRASENA],
        }
    }


@pytest.mark.parametrize("email", ["tomas.rios", "tomas@", "@example.com", "a" * 250 + "@x.com"])
def test_hu001_avisa_correo_invalido(cliente, email):
    respuesta = cliente.post(URL_REGISTRO, datos_registro(email=email), format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"email": ["Ingresá un correo válido."]}}


def test_hu001_limita_nombre_y_apellido_a_60_caracteres(cliente):
    respuesta = cliente.post(
        URL_REGISTRO, datos_registro(nombre="a" * 61, apellido="b" * 61), format="json"
    )

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "errores": {
            "nombre": ["Usá como máximo 60 caracteres."],
            "apellido": ["Usá como máximo 60 caracteres."],
        }
    }


def test_hu001_acepta_nombre_y_apellido_de_60_caracteres(cliente):
    respuesta = cliente.post(
        URL_REGISTRO, datos_registro(nombre="a" * 60, apellido="b" * 60), format="json"
    )

    assert respuesta.status_code == 201


def test_hu001_registro_exige_token_csrf():
    cliente = APIClient(enforce_csrf_checks=True)

    sin_token = cliente.post(URL_REGISTRO, datos_registro(), format="json")
    assert sin_token.status_code == 403
    assert not Usuario.objects.exists()

    cliente.get(URL_CSRF)
    token = cliente.cookies[settings.CSRF_COOKIE_NAME].value
    con_token = cliente.post(
        URL_REGISTRO, datos_registro(), format="json", headers={"X-CSRFToken": token}
    )
    assert con_token.status_code == 201


def test_csrf_entrega_la_cookie_sin_sesion(cliente):
    respuesta = cliente.get(URL_CSRF)

    assert respuesta.status_code == 204
    assert settings.CSRF_COOKIE_NAME in respuesta.cookies


def test_yo_sin_sesion_responde_401(cliente):
    respuesta = cliente.get(URL_YO)

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detalle": "Iniciá sesión para continuar."}
