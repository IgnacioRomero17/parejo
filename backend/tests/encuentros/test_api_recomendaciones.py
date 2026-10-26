from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.encuentros.models import Participante
from tests.fabricas import (
    crear_encuentro,
    crear_jugador_disponible,
    crear_localidad,
    crear_usuario_con_onboarding,
)

pytestmark = pytest.mark.django_db

MENSAJE_INEXISTENTE = "El encuentro no existe."


@pytest.fixture
def rio_ceballos():
    return crear_localidad()


@pytest.fixture
def organizador(rio_ceballos):
    return crear_usuario_con_onboarding(
        localidad=rio_ceballos, email="tomas@example.com", nivel_estimado=Decimal("4.5")
    )


@pytest.fixture
def encuentro(organizador):
    return crear_encuentro(organizador)


def cliente_de(usuario) -> APIClient:
    cliente = APIClient()
    cliente.force_login(usuario)
    return cliente


def url(id_encuentro) -> str:
    return f"/api/encuentros/{id_encuentro}/recomendados"


def test_hu007_responde_los_recomendados_en_orden(encuentro, organizador, rio_ceballos):
    valentina = crear_jugador_disponible(
        rio_ceballos,
        "valentina@example.com",
        nombre="Valentina",
        apellido="Sosa",
        nivel_estimado=Decimal("4.5"),
    )
    camila = crear_jugador_disponible(
        rio_ceballos,
        "camila@example.com",
        nombre="Camila",
        apellido="Paz",
        nivel_estimado=Decimal("5.0"),
    )

    respuesta = cliente_de(organizador).get(url(encuentro.pk))

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "lugares_libres": 3,
        "suficientes": False,
        "recomendados": [
            {
                "id": valentina.pk,
                "nombre": "Valentina",
                "apellido": "Sosa",
                "localidad": {"id": rio_ceballos.pk, "nombre": "Río Ceballos"},
                "nivel": 4.5,
                "franja": {"dia_semana": 6, "hora_inicio": "17:00", "hora_fin": "21:00"},
            },
            {
                "id": camila.pk,
                "nombre": "Camila",
                "apellido": "Paz",
                "localidad": {"id": rio_ceballos.pk, "nombre": "Río Ceballos"},
                "nivel": 5.0,
                "franja": {"dia_semana": 6, "hora_inicio": "17:00", "hora_fin": "21:00"},
            },
        ],
    }


def test_hu007_sin_candidatos_responde_la_lista_vacia(encuentro, organizador):
    respuesta = cliente_de(organizador).get(url(encuentro.pk))

    assert respuesta.status_code == 200
    assert respuesta.json() == {"lugares_libres": 3, "suficientes": False, "recomendados": []}


def test_hu007_sin_sesion_responde_401(encuentro):
    assert APIClient().get(url(encuentro.pk)).status_code == 401


def test_hu007_p6_un_participante_que_no_organiza_recibe_404(encuentro, rio_ceballos):
    participante = crear_usuario_con_onboarding(localidad=rio_ceballos, email="p@example.com")
    Participante.objects.create(encuentro=encuentro, usuario=participante)

    respuesta = cliente_de(participante).get(url(encuentro.pk))

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_INEXISTENTE}


def test_hu007_p6_un_jugador_ajeno_recibe_404(encuentro, rio_ceballos):
    ajeno = crear_usuario_con_onboarding(localidad=rio_ceballos, email="ajeno@example.com")

    assert cliente_de(ajeno).get(url(encuentro.pk)).status_code == 404


@pytest.mark.parametrize("id_encuentro", [999_999, 2_147_483_648])
def test_hu007_encuentro_inexistente_responde_404(organizador, id_encuentro):
    respuesta = cliente_de(organizador).get(url(id_encuentro))

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_INEXISTENTE}
