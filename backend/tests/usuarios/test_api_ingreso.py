from decimal import Decimal

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from tests.fabricas import crear_localidad, crear_preferencia, crear_usuario

pytestmark = pytest.mark.django_db

URL_INGRESAR = "/api/auth/ingresar"
URL_SALIR = "/api/auth/salir"
URL_YO = "/api/auth/yo"
URL_CSRF = "/api/auth/csrf"
MENSAJE_CREDENCIALES_INVALIDAS = "Las credenciales ingresadas no son válidas."
MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
CAMPOS = ("email", "contrasena")


def datos_ingreso(**campos) -> dict:
    datos = {"email": "tomas.rios@example.com", "contrasena": "clave1234"}
    datos.update(campos)
    return datos


@pytest.fixture
def cliente() -> APIClient:
    return APIClient()


@pytest.fixture
def usuario():
    return crear_usuario(
        email="tomas.rios@example.com", password="clave1234", nombre="Tomás", apellido="Ríos"
    )


def test_hu002_c1_ingresa_e_inicia_sesion(cliente, usuario):
    respuesta = cliente.post(URL_INGRESAR, datos_ingreso(), format="json")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": usuario.id_usuario,
        "nombre": "Tomás",
        "apellido": "Ríos",
        "email": "tomas.rios@example.com",
        "onboarding": "perfil",
        "invitaciones_pendientes": 0,
    }

    sesion = cliente.get(URL_YO)
    assert sesion.status_code == 200
    assert sesion.json()["id"] == usuario.id_usuario


def test_hu002_c1_ingresa_con_el_correo_en_mayusculas(cliente, usuario):
    respuesta = cliente.post(
        URL_INGRESAR, datos_ingreso(email="Tomas.Rios@Example.COM"), format="json"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == usuario.id_usuario


def test_hu002_p1_informa_el_paso_de_onboarding_pendiente(cliente, usuario):
    respuesta = cliente.post(URL_INGRESAR, datos_ingreso(), format="json")

    assert respuesta.json()["onboarding"] == "perfil"


def test_hu002_p1_con_el_perfil_completo_informa_el_paso_disponibilidad(cliente):
    crear_usuario(
        email="tomas.rios@example.com",
        password="clave1234",
        localidad=crear_localidad(),
        nivel_estimado=Decimal("3.5"),
    )

    respuesta = cliente.post(URL_INGRESAR, datos_ingreso(), format="json")

    assert respuesta.status_code == 200
    assert respuesta.json()["onboarding"] == "disponibilidad"


def test_hu002_p1_sin_paso_pendiente_con_el_onboarding_completo(cliente):
    usuario = crear_usuario(
        email="tomas.rios@example.com",
        password="clave1234",
        localidad=crear_localidad(),
        nivel_estimado=Decimal("3.5"),
    )
    crear_preferencia(usuario)

    respuesta = cliente.post(URL_INGRESAR, datos_ingreso(), format="json")

    assert respuesta.status_code == 200
    assert respuesta.json()["onboarding"] is None


def test_hu002_c2_contrasena_incorrecta_responde_400(cliente, usuario):
    respuesta = cliente.post(URL_INGRESAR, datos_ingreso(contrasena="clave12345"), format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"detalle": MENSAJE_CREDENCIALES_INVALIDAS}
    assert cliente.get(URL_YO).status_code == 401


@pytest.mark.parametrize("email", ["valentina.sosa@example.com", "tomas.rios"])
def test_hu002_c3_correo_no_registrado_responde_el_mismo_mensaje(cliente, usuario, email):
    respuesta = cliente.post(URL_INGRESAR, datos_ingreso(email=email), format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"detalle": MENSAJE_CREDENCIALES_INVALIDAS}
    assert cliente.get(URL_YO).status_code == 401


@pytest.mark.parametrize("datos", [{}, dict.fromkeys(CAMPOS, ""), dict.fromkeys(CAMPOS)])
def test_hu002_avisa_campos_vacios(cliente, datos):
    respuesta = cliente.post(URL_INGRESAR, datos, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": dict.fromkeys(CAMPOS, [MENSAJE_CAMPO_VACIO])}


def test_hu002_ingreso_exige_token_csrf(usuario):
    cliente = APIClient(enforce_csrf_checks=True)

    sin_token = cliente.post(URL_INGRESAR, datos_ingreso(), format="json")
    assert sin_token.status_code == 403

    cliente.get(URL_CSRF)
    token = cliente.cookies[settings.CSRF_COOKIE_NAME].value
    con_token = cliente.post(
        URL_INGRESAR, datos_ingreso(), format="json", headers={"X-CSRFToken": token}
    )
    assert con_token.status_code == 200


def test_hu002_salir_cierra_la_sesion(cliente, usuario):
    cliente.post(URL_INGRESAR, datos_ingreso(), format="json")

    respuesta = cliente.post(URL_SALIR)

    assert respuesta.status_code == 204
    assert cliente.get(URL_YO).status_code == 401


def test_hu002_salir_sin_sesion_responde_401(cliente):
    respuesta = cliente.post(URL_SALIR)

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detalle": "Iniciá sesión para continuar."}
