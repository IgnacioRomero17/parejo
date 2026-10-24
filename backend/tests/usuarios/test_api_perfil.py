from decimal import Decimal

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from apps.usuarios.models import Usuario
from tests.fabricas import crear_localidad, crear_usuario, crear_usuario_con_perfil

pytestmark = pytest.mark.django_db

URL_PERFIL = "/api/perfil"
URL_YO = "/api/auth/yo"
URL_CSRF = "/api/auth/csrf"
MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
MENSAJE_EDAD_INVALIDA = "Ingresá una edad entre 18 y 99."
MENSAJE_OPCION_INVALIDA = "Elegí una opción del listado."
MENSAJE_NIVEL_INVALIDO = "Elegí un nivel entre 1,0 y 7,0, en pasos de 0,5."
CAMPOS_PERFIL_DEPORTIVO = ("edad", "genero", "localidad", "frecuencia_juego", "nivel_estimado")


@pytest.fixture
def localidad():
    return crear_localidad()


@pytest.fixture
def usuario():
    return crear_usuario(email="tomas.rios@example.com", nombre="Tomás", apellido="Ríos")


@pytest.fixture
def cliente(usuario) -> APIClient:
    cliente = APIClient()
    cliente.force_login(usuario)
    return cliente


def perfil_deportivo(localidad_elegida, **campos) -> dict:
    datos = {
        "edad": 34,
        "genero": "MASCULINO",
        "localidad": localidad_elegida.id_localidad,
        "frecuencia_juego": "2_3_SEMANA",
        "nivel_estimado": 4.5,
    }
    datos.update(campos)
    return datos


def guardar_perfil_deportivo(cliente, datos):
    return cliente.patch(URL_PERFIL, {"perfil_deportivo": datos}, format="json")


def test_hu004_get_devuelve_el_perfil_vacio_en_el_primer_ingreso(cliente, usuario):
    respuesta = cliente.get(URL_PERFIL)

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "datos_personales": {
            "nombre": "Tomás",
            "apellido": "Ríos",
            "email": "tomas.rios@example.com",
        },
        "perfil_deportivo": dict.fromkeys(CAMPOS_PERFIL_DEPORTIVO),
        "disponibilidad": {
            "franjas": [],
            "tipo_encuentro": None,
            "lado_preferido": None,
            "disponible_para_invitaciones": False,
        },
    }


def test_hu004_guarda_el_perfil_deportivo_y_lo_devuelve(cliente, usuario, localidad):
    respuesta = guardar_perfil_deportivo(cliente, perfil_deportivo(localidad))

    assert respuesta.status_code == 200
    assert respuesta.json()["perfil_deportivo"] == perfil_deportivo(localidad)
    usuario.refresh_from_db()
    assert usuario.nivel_estimado == Decimal("4.5")
    assert usuario.localidad == localidad


def test_hu004_p8_auth_yo_deja_de_pedir_el_paso_perfil_al_guardarlo(cliente, localidad):
    assert cliente.get(URL_YO).json()["onboarding"] == "perfil"

    guardar_perfil_deportivo(cliente, perfil_deportivo(localidad))

    assert cliente.get(URL_YO).json()["onboarding"] == "disponibilidad"


@pytest.mark.parametrize("datos", [{}, dict.fromkeys(CAMPOS_PERFIL_DEPORTIVO)])
def test_hu004_c1_indica_todos_los_campos_pendientes(cliente, usuario, datos):
    respuesta = guardar_perfil_deportivo(cliente, datos)

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "errores": {
            "perfil_deportivo": dict.fromkeys(CAMPOS_PERFIL_DEPORTIVO, [MENSAJE_CAMPO_VACIO])
        }
    }
    usuario.refresh_from_db()
    assert not usuario.perfil_completo


def test_hu004_c1_impide_guardar_si_falta_un_dato(cliente, usuario, localidad):
    datos = perfil_deportivo(localidad)
    del datos["frecuencia_juego"]

    respuesta = guardar_perfil_deportivo(cliente, datos)

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "errores": {"perfil_deportivo": {"frecuencia_juego": [MENSAJE_CAMPO_VACIO]}}
    }
    usuario.refresh_from_db()
    assert usuario.edad is None


@pytest.mark.parametrize(
    ("campo", "valor", "mensaje"),
    [
        ("edad", 17, MENSAJE_EDAD_INVALIDA),
        ("edad", 100, MENSAJE_EDAD_INVALIDA),
        ("edad", 20.5, MENSAJE_EDAD_INVALIDA),
        ("edad", "veinte", MENSAJE_EDAD_INVALIDA),
        ("genero", "OTRO", MENSAJE_OPCION_INVALIDA),
        ("frecuencia_juego", "DIARIA", MENSAJE_OPCION_INVALIDA),
        ("localidad", 999_999, MENSAJE_OPCION_INVALIDA),
        ("localidad", 99_999_999_999, MENSAJE_OPCION_INVALIDA),
        ("localidad", "Río Ceballos", MENSAJE_OPCION_INVALIDA),
        ("nivel_estimado", 0.5, MENSAJE_NIVEL_INVALIDO),
        ("nivel_estimado", 7.5, MENSAJE_NIVEL_INVALIDO),
        ("nivel_estimado", 4.3, MENSAJE_NIVEL_INVALIDO),
        ("nivel_estimado", 4.25, MENSAJE_NIVEL_INVALIDO),
        ("nivel_estimado", 10, MENSAJE_NIVEL_INVALIDO),
        ("nivel_estimado", "alto", MENSAJE_NIVEL_INVALIDO),
    ],
)
def test_hu004_c2_impide_guardar_un_valor_invalido(
    cliente, usuario, localidad, campo, valor, mensaje
):
    respuesta = guardar_perfil_deportivo(cliente, perfil_deportivo(localidad, **{campo: valor}))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"perfil_deportivo": {campo: [mensaje]}}}
    usuario.refresh_from_db()
    assert not usuario.perfil_completo


@pytest.mark.parametrize(("edad", "nivel"), [(18, 1.0), (99, 7.0), (45, 3)])
def test_hu004_p2_acepta_los_limites(cliente, localidad, edad, nivel):
    respuesta = guardar_perfil_deportivo(
        cliente, perfil_deportivo(localidad, edad=edad, nivel_estimado=nivel)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["perfil_deportivo"]["edad"] == edad
    assert respuesta.json()["perfil_deportivo"]["nivel_estimado"] == nivel


def test_hu004_c3_modifica_el_perfil_ya_registrado(localidad):
    usuario = crear_usuario_con_perfil(localidad=localidad)
    otra_localidad = crear_localidad(nombre="Unquillo")
    cliente = APIClient()
    cliente.force_login(usuario)

    respuesta = cliente.patch(
        URL_PERFIL,
        {
            "datos_personales": {"nombre": "Valentina", "apellido": "Sosa"},
            "perfil_deportivo": perfil_deportivo(otra_localidad, nivel_estimado=5),
        },
        format="json",
    )

    assert respuesta.status_code == 200
    actual = cliente.get(URL_PERFIL).json()
    assert actual["datos_personales"]["nombre"] == "Valentina"
    assert actual["datos_personales"]["apellido"] == "Sosa"
    assert actual["perfil_deportivo"]["localidad"] == otra_localidad.id_localidad
    assert actual["perfil_deportivo"]["nivel_estimado"] == 5.0


def test_hu004_c3_solo_cambia_la_seccion_enviada(localidad):
    usuario = crear_usuario_con_perfil(localidad=localidad)
    cliente = APIClient()
    cliente.force_login(usuario)

    respuesta = cliente.patch(
        URL_PERFIL, {"datos_personales": {"nombre": "Ana", "apellido": "Gómez"}}, format="json"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["perfil_deportivo"]["nivel_estimado"] == 4.0
    assert respuesta.json()["datos_personales"]["apellido"] == "Gómez"


def test_hu004_c2_con_un_error_no_guarda_ninguna_seccion(localidad):
    usuario = crear_usuario_con_perfil(localidad=localidad, nombre="Ana")
    cliente = APIClient()
    cliente.force_login(usuario)

    respuesta = cliente.patch(
        URL_PERFIL,
        {
            "datos_personales": {"nombre": "Valentina", "apellido": "Sosa"},
            "perfil_deportivo": perfil_deportivo(localidad, edad=15),
        },
        format="json",
    )

    assert respuesta.status_code == 400
    usuario.refresh_from_db()
    assert usuario.nombre == "Ana"
    assert usuario.edad == 30


@pytest.mark.parametrize(
    ("datos", "errores"),
    [
        (
            {"nombre": "", "apellido": " "},
            {"nombre": [MENSAJE_CAMPO_VACIO], "apellido": [MENSAJE_CAMPO_VACIO]},
        ),
        ({"nombre": "A" * 61, "apellido": "Sosa"}, {"nombre": ["Usá como máximo 60 caracteres."]}),
    ],
)
def test_hu004_c2_valida_los_datos_personales(cliente, usuario, datos, errores):
    respuesta = cliente.patch(URL_PERFIL, {"datos_personales": datos}, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"datos_personales": errores}}
    usuario.refresh_from_db()
    assert usuario.nombre == "Tomás"


def test_hu004_el_correo_no_se_modifica(cliente, usuario):
    respuesta = cliente.patch(
        URL_PERFIL,
        {"datos_personales": {"nombre": "Tomás", "apellido": "Ríos", "email": "otro@example.com"}},
        format="json",
    )

    assert respuesta.status_code == 200
    usuario.refresh_from_db()
    assert usuario.email == "tomas.rios@example.com"


def test_hu004_cada_jugador_solo_ve_y_modifica_su_perfil(cliente, usuario, localidad):
    otro = crear_usuario_con_perfil(email="valentina.sosa@example.com", localidad=localidad)

    guardar_perfil_deportivo(cliente, perfil_deportivo(localidad, edad=50))

    otro.refresh_from_db()
    assert otro.edad == 30
    assert cliente.get(URL_PERFIL).json()["datos_personales"]["email"] == "tomas.rios@example.com"


@pytest.mark.parametrize("metodo", ["get", "patch"])
def test_hu004_perfil_sin_sesion_responde_401(metodo):
    respuesta = getattr(APIClient(), metodo)(URL_PERFIL, {}, format="json")

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detalle": "Iniciá sesión para continuar."}


def test_hu004_patch_perfil_exige_token_csrf(usuario, localidad):
    cliente = APIClient(enforce_csrf_checks=True)
    cliente.force_login(usuario)

    sin_token = guardar_perfil_deportivo(cliente, perfil_deportivo(localidad))
    assert sin_token.status_code == 403

    cliente.get(URL_CSRF)
    token = cliente.cookies[settings.CSRF_COOKIE_NAME].value
    con_token = cliente.patch(
        URL_PERFIL,
        {"perfil_deportivo": perfil_deportivo(localidad)},
        format="json",
        headers={"X-CSRFToken": token},
    )
    assert con_token.status_code == 200
    assert Usuario.objects.get(pk=usuario.pk).perfil_completo
