"""`GET encuentros`: encuentros activos del panel principal (pantalla 08, HU-012)."""

from datetime import time

import pytest
from rest_framework.test import APIClient

from apps.encuentros.models import EstadoEncuentro, EstadoInvitacion, Participante
from apps.usuarios.models import Genero
from tests.fabricas import (
    crear_encuentro,
    crear_invitacion,
    crear_localidad,
    crear_usuario_con_onboarding,
    crear_usuario_con_perfil,
)

pytestmark = pytest.mark.django_db

URL_ENCUENTROS = "/api/encuentros"


@pytest.fixture
def rio_ceballos():
    return crear_localidad()


@pytest.fixture
def tomas(rio_ceballos):
    return crear_usuario_con_onboarding(
        localidad=rio_ceballos,
        email="tomas@example.com",
        nombre="Tomás",
        apellido="Ríos",
        genero=Genero.MASCULINO,
    )


@pytest.fixture
def lucia(rio_ceballos):
    return crear_usuario_con_onboarding(
        localidad=rio_ceballos,
        email="lucia@example.com",
        nombre="Lucía",
        apellido="Bravo",
        genero=Genero.FEMENINO,
    )


def consultar(usuario):
    cliente = APIClient()
    cliente.force_login(usuario)
    return cliente.get(URL_ENCUENTROS)


def test_hu012_devuelve_los_encuentros_activos_con_el_rol(tomas, lucia, rio_ceballos):
    organizado = crear_encuentro(tomas)
    invitado = crear_usuario_con_onboarding(localidad=rio_ceballos, email="diego@example.com")
    crear_invitacion(organizado, invitado)
    aceptado = crear_encuentro(lucia, hora_inicio=time(20), estado=EstadoEncuentro.COMPLETO)
    Participante.objects.create(encuentro=aceptado, usuario=tomas)

    respuesta = consultar(tomas)

    assert respuesta.status_code == 200
    primero, segundo = respuesta.json()
    assert primero == {
        "id": organizado.pk,
        "fecha": organizado.fecha.isoformat(),
        "hora_inicio": "18:00",
        "duracion_minutos": 90,
        "localidad": {"id": rio_ceballos.pk, "nombre": "Río Ceballos"},
        "ubicacion": "Av. San Martín 4500",
        "tipo_encuentro": "COMPETITIVO",
        "estado": EstadoEncuentro.BUSCANDO_PARTICIPANTES,
        "confirmados": 1,
        "organizador": {
            "id": tomas.pk,
            "nombre": "Tomás",
            "apellido": "Ríos",
            "genero": "MASCULINO",
        },
        "organizas": True,
        "invitaciones_pendientes": 1,
    }
    assert segundo["id"] == aceptado.pk
    assert segundo["organizas"] is False
    assert segundo["confirmados"] == 2
    assert segundo["organizador"] == {
        "id": lucia.pk,
        "nombre": "Lucía",
        "apellido": "Bravo",
        "genero": "FEMENINO",
    }


def test_hu012_las_invitaciones_pendientes_se_informan_solo_al_organizador(tomas, lucia):
    encuentro = crear_encuentro(lucia)
    Participante.objects.create(encuentro=encuentro, usuario=tomas)
    crear_invitacion(encuentro, tomas, estado=EstadoInvitacion.ACEPTADA)

    [datos] = consultar(tomas).json()

    assert "invitaciones_pendientes" not in datos


def test_hu012_sin_encuentros_devuelve_una_lista_vacia(tomas):
    respuesta = consultar(tomas)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_hu012_no_expone_la_edad_del_organizador(tomas):
    crear_encuentro(tomas)

    [datos] = consultar(tomas).json()

    assert "edad" not in datos["organizador"]


def test_hu012_sin_sesion_responde_401():
    assert APIClient().get(URL_ENCUENTROS).status_code == 401


def test_hu012_sin_onboarding_responde_403_con_el_paso():
    usuario = crear_usuario_con_perfil()

    respuesta = consultar(usuario)

    assert respuesta.status_code == 403
    assert respuesta.json() == {
        "detalle": "Completá tu perfil para continuar.",
        "onboarding": "disponibilidad",
    }
