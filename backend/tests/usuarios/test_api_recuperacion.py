import pytest
from django.conf import settings
from django.core import mail
from rest_framework.test import APIClient

from apps.usuarios.servicios import enlace_recuperacion
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

URL_RECUPERAR = "/api/auth/recuperar"
URL_CONFIRMAR = "/api/auth/recuperar/confirmar"
URL_INGRESAR = "/api/auth/ingresar"
URL_SALIR = "/api/auth/salir"
URL_YO = "/api/auth/yo"
URL_CSRF = "/api/auth/csrf"
MENSAJE_CUENTA_INEXISTENTE = "La cuenta no existe. Revisá el correo ingresado."
MENSAJE_ENLACE_INVALIDO = "El enlace no es válido."
MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
MENSAJE_POLITICA = (
    "La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número."
)
CAMPOS_CONFIRMAR = ("uid", "token", "contrasena")


@pytest.fixture
def cliente() -> APIClient:
    return APIClient()


@pytest.fixture
def usuario():
    return crear_usuario(
        email="tomas.rios@example.com", password="clave1234", nombre="Tomás", apellido="Ríos"
    )


def partes_del_enlace(usuario) -> dict:
    uid, token = enlace_recuperacion(usuario).split("/recuperar/")[1].split("/")
    return {"uid": uid, "token": token}


def url_enlace(partes: dict) -> str:
    return f"{URL_RECUPERAR}/{partes['uid']}/{partes['token']}"


def test_hu003_c1_envia_el_correo_y_responde_204(cliente, usuario):
    respuesta = cliente.post(URL_RECUPERAR, {"email": "Tomas.Rios@example.com"}, format="json")

    assert respuesta.status_code == 204
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["tomas.rios@example.com"]


def test_hu003_p4_el_correo_enlaza_a_la_ruta_del_frontend(cliente, usuario):
    cliente.post(URL_RECUPERAR, {"email": "tomas.rios@example.com"}, format="json")

    assert f"{settings.URL_FRONTEND}/recuperar/" in mail.outbox[0].body
    assert "/api/" not in mail.outbox[0].body


def test_hu003_c2_correo_no_registrado_responde_400_en_el_campo(cliente, usuario):
    respuesta = cliente.post(URL_RECUPERAR, {"email": "valentina.sosa@example.com"}, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"email": [MENSAJE_CUENTA_INEXISTENTE]}}
    assert mail.outbox == []


@pytest.mark.parametrize("datos", [{}, {"email": ""}, {"email": None}])
def test_hu003_recuperar_avisa_el_campo_vacio(cliente, datos):
    respuesta = cliente.post(URL_RECUPERAR, datos, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"email": [MENSAJE_CAMPO_VACIO]}}


def test_hu003_enlace_valido_devuelve_el_correo(cliente, usuario):
    respuesta = cliente.get(url_enlace(partes_del_enlace(usuario)))

    assert respuesta.status_code == 200
    assert respuesta.json() == {"email": "tomas.rios@example.com"}


def test_hu003_enlace_invalido_responde_400(cliente, usuario):
    partes = {**partes_del_enlace(usuario), "token": "token-alterado"}

    respuesta = cliente.get(url_enlace(partes))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"detalle": MENSAJE_ENLACE_INVALIDO}


def test_hu003_enlace_funciona_con_otra_sesion_iniciada(cliente, usuario):
    cliente.force_login(crear_usuario(email="valentina.sosa@example.com"))

    respuesta = cliente.get(url_enlace(partes_del_enlace(usuario)))

    assert respuesta.status_code == 200
    assert respuesta.json() == {"email": "tomas.rios@example.com"}


def test_hu003_p5_guardar_inicia_la_sesion(cliente, usuario):
    datos = {**partes_del_enlace(usuario), "contrasena": "nueva5678"}

    respuesta = cliente.post(URL_CONFIRMAR, datos, format="json")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": usuario.id_usuario,
        "nombre": "Tomás",
        "apellido": "Ríos",
        "email": "tomas.rios@example.com",
        "onboarding": "perfil",
    }
    assert cliente.get(URL_YO).json()["id"] == usuario.id_usuario


def test_hu003_c3_ingresa_con_la_nueva_contrasena(cliente, usuario):
    datos = {**partes_del_enlace(usuario), "contrasena": "nueva5678"}
    cliente.post(URL_CONFIRMAR, datos, format="json")
    cliente.post(URL_SALIR)

    anterior = cliente.post(
        URL_INGRESAR, {"email": "tomas.rios@example.com", "contrasena": "clave1234"}, format="json"
    )
    nueva = cliente.post(
        URL_INGRESAR, {"email": "tomas.rios@example.com", "contrasena": "nueva5678"}, format="json"
    )

    assert anterior.status_code == 400
    assert nueva.status_code == 200


def test_hu003_p2_contrasena_invalida_responde_400_en_el_campo(cliente, usuario):
    datos = {**partes_del_enlace(usuario), "contrasena": "corta1"}

    respuesta = cliente.post(URL_CONFIRMAR, datos, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"contrasena": [MENSAJE_POLITICA]}}
    assert cliente.get(URL_YO).status_code == 401


def test_hu003_p3_enlace_usado_no_vuelve_a_servir(cliente, usuario):
    partes = partes_del_enlace(usuario)
    cliente.post(URL_CONFIRMAR, {**partes, "contrasena": "nueva5678"}, format="json")

    validar = cliente.get(url_enlace(partes))
    confirmar = cliente.post(URL_CONFIRMAR, {**partes, "contrasena": "otra9012"}, format="json")

    assert validar.status_code == 400
    assert validar.json() == {"detalle": MENSAJE_ENLACE_INVALIDO}
    assert confirmar.status_code == 400
    assert confirmar.json() == {"detalle": MENSAJE_ENLACE_INVALIDO}


@pytest.mark.parametrize(
    "datos", [{}, dict.fromkeys(CAMPOS_CONFIRMAR, ""), dict.fromkeys(CAMPOS_CONFIRMAR)]
)
def test_hu003_confirmar_avisa_campos_vacios(cliente, datos):
    respuesta = cliente.post(URL_CONFIRMAR, datos, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": dict.fromkeys(CAMPOS_CONFIRMAR, [MENSAJE_CAMPO_VACIO])}


def test_hu003_recuperar_y_confirmar_exigen_token_csrf(usuario):
    cliente = APIClient(enforce_csrf_checks=True)
    datos_confirmar = {**partes_del_enlace(usuario), "contrasena": "nueva5678"}

    sin_token = [
        cliente.post(URL_RECUPERAR, {"email": "tomas.rios@example.com"}, format="json"),
        cliente.post(URL_CONFIRMAR, datos_confirmar, format="json"),
    ]
    assert [respuesta.status_code for respuesta in sin_token] == [403, 403]

    cliente.get(URL_CSRF)
    cabeceras = {"X-CSRFToken": cliente.cookies[settings.CSRF_COOKIE_NAME].value}
    recuperar = cliente.post(
        URL_RECUPERAR, {"email": "tomas.rios@example.com"}, format="json", headers=cabeceras
    )
    confirmar = cliente.post(URL_CONFIRMAR, datos_confirmar, format="json", headers=cabeceras)
    assert recuperar.status_code == 204
    assert confirmar.status_code == 200
