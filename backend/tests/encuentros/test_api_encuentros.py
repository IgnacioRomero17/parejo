from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.encuentros.models import Encuentro, EstadoEncuentro
from tests.fabricas import (
    crear_encuentro,
    crear_localidad,
    crear_usuario_con_onboarding,
    crear_usuario_con_perfil,
    proximo_sabado,
)

pytestmark = pytest.mark.django_db

URL_ENCUENTROS = "/api/encuentros"
MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
MENSAJE_OPCION_INVALIDA = "Elegí una opción del listado."
MENSAJE_HORA_INVALIDA = "Elegí un horario entre las 08:00 y las 23:30, en pasos de 30 minutos."
MENSAJE_FIN_TARDE = "El encuentro tiene que terminar a las 23:30 como máximo."
MENSAJE_EN_EL_PASADO = "Elegí una fecha y hora futuras."
MENSAJE_FECHA_LEJANA = "Elegí una fecha dentro de los próximos 60 días."
CAMPOS = ("fecha", "hora_inicio", "duracion_minutos", "localidad", "ubicacion", "tipo_encuentro")


@pytest.fixture
def organizador():
    return crear_usuario_con_onboarding(email="tomas.rios@example.com")


@pytest.fixture
def cliente(organizador) -> APIClient:
    cliente = APIClient()
    cliente.force_login(organizador)
    return cliente


def condiciones(organizador, **campos) -> dict:
    datos = {
        "fecha": proximo_sabado().isoformat(),
        "hora_inicio": "18:00",
        "duracion_minutos": 90,
        "localidad": organizador.localidad_id,
        "ubicacion": "Av. San Martín 4500",
        "tipo_encuentro": "COMPETITIVO",
    }
    datos.update(campos)
    return datos


def crear(cliente, datos):
    return cliente.post(URL_ENCUENTROS, datos, format="json")


def test_hu006_c1_c3_crea_el_encuentro_y_devuelve_sus_condiciones(cliente, organizador):
    datos = condiciones(organizador)

    respuesta = crear(cliente, datos)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    encuentro = Encuentro.objects.get()
    assert cuerpo == {
        "id": encuentro.pk,
        "fecha": datos["fecha"],
        "hora_inicio": "18:00",
        "duracion_minutos": 90,
        "localidad": {"id": organizador.localidad_id, "nombre": "Río Ceballos"},
        "ubicacion": "Av. San Martín 4500",
        "tipo_encuentro": "COMPETITIVO",
        "estado": EstadoEncuentro.BUSCANDO_PARTICIPANTES,
        "confirmados": 1,
    }


def test_hu006_c3_el_encuentro_creado_se_puede_consultar(cliente, organizador):
    creado = crear(cliente, condiciones(organizador)).json()

    respuesta = cliente.get(f"{URL_ENCUENTROS}/{creado['id']}")

    assert respuesta.status_code == 200
    # Además de las condiciones, la versión completa de HU-008 suma lugares y participantes.
    assert respuesta.json() == {
        **creado,
        "lugares_libres": 3,
        "participantes": [
            {
                "id": organizador.pk,
                "nombre": "Ana",
                "apellido": "Pérez",
                "localidad": {"id": organizador.localidad_id, "nombre": "Río Ceballos"},
                "nivel": 4.0,
                "lado": "DRIVE",
            }
        ],
        "invitaciones": [],
    }


def test_hu006_p5_la_localidad_puede_ser_otra_que_la_del_organizador(cliente, organizador):
    unquillo = crear_localidad(nombre="Unquillo")

    respuesta = crear(cliente, condiciones(organizador, localidad=unquillo.pk))

    assert respuesta.json()["localidad"] == {"id": unquillo.pk, "nombre": "Unquillo"}


def test_hu006_c2_indica_cada_condicion_faltante(cliente):
    respuesta = crear(cliente, {})

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": dict.fromkeys(CAMPOS, [MENSAJE_CAMPO_VACIO])}
    assert not Encuentro.objects.exists()


@pytest.mark.parametrize("campo", CAMPOS)
def test_hu006_c2_una_condicion_vacia_impide_crear(cliente, organizador, campo):
    respuesta = crear(cliente, condiciones(organizador, **{campo: None}))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {campo: [MENSAJE_CAMPO_VACIO]}}


@pytest.mark.parametrize(
    ("campo", "valor", "mensaje"),
    [
        ("hora_inicio", "18:15", MENSAJE_HORA_INVALIDA),
        ("hora_inicio", "07:30", MENSAJE_HORA_INVALIDA),
        ("hora_inicio", "las seis", MENSAJE_HORA_INVALIDA),
        ("duracion_minutos", 45, MENSAJE_OPCION_INVALIDA),
        ("tipo_encuentro", "AMISTOSO", MENSAJE_OPCION_INVALIDA),
        ("localidad", 999_999, MENSAJE_OPCION_INVALIDA),
        ("localidad", "Río Ceballos", MENSAJE_OPCION_INVALIDA),
        ("ubicacion", "x" * 151, "Usá como máximo 150 caracteres."),
        ("fecha", "03/10/2026", "Elegí una fecha válida."),
    ],
)
def test_hu006_p1_rechaza_condiciones_invalidas(cliente, organizador, campo, valor, mensaje):
    respuesta = crear(cliente, condiciones(organizador, **{campo: valor}))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {campo: [mensaje]}}


def test_hu006_p6_termina_despues_de_las_23_30(cliente, organizador):
    respuesta = crear(cliente, condiciones(organizador, hora_inicio="22:30", duracion_minutos=120))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"duracion_minutos": [MENSAJE_FIN_TARDE]}}


def test_hu006_p6_acepta_el_ultimo_inicio_con_la_duracion_minima(cliente, organizador):
    respuesta = crear(cliente, condiciones(organizador, hora_inicio="22:30", duracion_minutos=60))

    assert respuesta.status_code == 201


def test_hu006_p4_rechaza_una_fecha_pasada(cliente, organizador):
    respuesta = crear(cliente, condiciones(organizador, fecha="2020-01-04"))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"fecha": [MENSAJE_EN_EL_PASADO]}}


def test_hu006_p4_acepta_una_fecha_a_60_dias(cliente, organizador):
    fecha = timezone.localdate() + timedelta(days=60)

    respuesta = crear(cliente, condiciones(organizador, fecha=fecha.isoformat()))

    assert respuesta.status_code == 201


def test_hu006_p4_rechaza_una_fecha_a_61_dias(cliente, organizador):
    fecha = timezone.localdate() + timedelta(days=61)

    respuesta = crear(cliente, condiciones(organizador, fecha=fecha.isoformat()))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"fecha": [MENSAJE_FECHA_LEJANA]}}
    assert not Encuentro.objects.exists()


def test_hu006_sin_sesion_responde_401(organizador):
    respuesta = crear(APIClient(), condiciones(organizador))

    assert respuesta.status_code == 401


@pytest.mark.parametrize(
    ("crear_usuario", "paso"),
    [
        (crear_usuario_con_perfil, "disponibilidad"),
        (lambda: crear_usuario_con_onboarding(nivel_estimado=None), "perfil"),
    ],
)
def test_hu006_c1_sin_onboarding_responde_403_con_el_paso(crear_usuario, paso):
    usuario = crear_usuario()
    cliente = APIClient()
    cliente.force_login(usuario)

    respuesta = crear(cliente, condiciones(usuario))

    assert respuesta.status_code == 403
    assert respuesta.json() == {"detalle": "Completá tu perfil para continuar.", "onboarding": paso}
    assert not Encuentro.objects.exists()


def test_hu006_get_de_un_encuentro_ajeno_responde_404(organizador):
    encuentro = crear_encuentro(organizador)
    otro = crear_usuario_con_onboarding(
        email="valentina.sosa@example.com", localidad=organizador.localidad
    )
    cliente = APIClient()
    cliente.force_login(otro)

    respuesta = cliente.get(f"{URL_ENCUENTROS}/{encuentro.pk}")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": "El encuentro no existe."}


def test_hu006_get_de_un_encuentro_inexistente_responde_404(cliente):
    respuesta = cliente.get(f"{URL_ENCUENTROS}/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": "El encuentro no existe."}


def test_hu006_get_sin_sesion_responde_401(organizador):
    encuentro = crear_encuentro(organizador)

    respuesta = APIClient().get(f"{URL_ENCUENTROS}/{encuentro.pk}")

    assert respuesta.status_code == 401
