from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.encuentros.models import Combinacion, EstadoEncuentro
from apps.usuarios.models import LadoPreferido
from tests.fabricas import (
    crear_encuentro,
    crear_encuentro_completo,
    crear_localidad,
    crear_preferencia,
    crear_usuario_con_onboarding,
    crear_usuario_con_perfil,
)

pytestmark = pytest.mark.django_db

MENSAJE_ENCUENTRO_INEXISTENTE = "El encuentro no existe."
MENSAJE_YA_COMENZO = "Este encuentro ya comenzó."
MENSAJE_YA_TIENE_PROPUESTA = "Este encuentro ya tiene una propuesta."
MENSAJE_SIN_CUATRO = "El encuentro todavía no tiene 4 jugadores confirmados."


@pytest.fixture
def rio_ceballos():
    return crear_localidad()


def jugador(localidad, nombre, apellido, nivel, lado):
    usuario = crear_usuario_con_perfil(
        localidad=localidad,
        email=f"{apellido.lower()}@example.com",
        nombre=nombre,
        apellido=apellido,
        nivel_estimado=Decimal(nivel),
    )
    crear_preferencia(usuario, lado_preferido=lado)
    return usuario


@pytest.fixture
def jugadores(rio_ceballos):
    return (
        jugador(rio_ceballos, "Tomás", "Ríos", "4.5", LadoPreferido.DRIVE),
        jugador(rio_ceballos, "Valentina", "Sosa", "4.5", LadoPreferido.REVES),
        jugador(rio_ceballos, "Camila", "Paz", "5.0", LadoPreferido.REVES),
        jugador(rio_ceballos, "Federico", "Luna", "5.0", LadoPreferido.DRIVE),
    )


@pytest.fixture
def encuentro(jugadores):
    return crear_encuentro_completo(*jugadores)


def formar(usuario, id_encuentro):
    cliente = APIClient()
    cliente.force_login(usuario)
    return cliente.post(f"/api/encuentros/{id_encuentro}/formar-parejas")


def integrante(usuario, lado):
    return {
        "id": usuario.pk,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "localidad": {"id": usuario.localidad_id, "nombre": usuario.localidad.nombre},
        "nivel": float(usuario.nivel_estimado),
        "lado": lado,
    }


def test_hu009_c1_formar_parejas_responde_201_con_la_propuesta(encuentro, jugadores):
    tomas, valentina, camila, federico = jugadores

    respuesta = formar(tomas, encuentro.pk)

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["encuentro"]["id"] == encuentro.pk
    assert datos["encuentro"]["estado"] == EstadoEncuentro.PROPUESTA_GENERADA
    assert datos["combinacion_elegida"] == 2
    assert datos["puntaje_equilibrio"] == 1.0
    assert [
        (c["numero"], c["puntaje_equilibrio"], c["equilibrio_nivel"], c["equilibrio_lado"])
        for c in datos["combinaciones"]
    ] == [(1, 0.8, 0.75, 1.0), (2, 1.0, 1.0, 1.0), (3, 0.8, 1.0, 0.0)]
    assert datos["combinaciones"][1]["parejas"] == [
        {
            "numero": 1,
            "promedio": 4.75,
            "integrantes": [integrante(tomas, "DRIVE"), integrante(camila, "REVES")],
        },
        {
            "numero": 2,
            "promedio": 4.75,
            "integrantes": [integrante(valentina, "REVES"), integrante(federico, "DRIVE")],
        },
    ]


def test_hu009_la_respuesta_no_expone_edad_ni_genero(encuentro, jugadores):
    datos = formar(jugadores[0], encuentro.pk).json()

    for combinacion in datos["combinaciones"]:
        for pareja in combinacion["parejas"]:
            for persona in pareja["integrantes"]:
                assert "edad" not in persona
                assert "genero" not in persona


def test_hu009_p1_un_participante_que_no_organiza_recibe_404(encuentro, jugadores):
    respuesta = formar(jugadores[1], encuentro.pk)

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_ENCUENTRO_INEXISTENTE}
    assert not Combinacion.objects.exists()


def test_hu009_un_usuario_ajeno_recibe_404(encuentro, rio_ceballos):
    ajeno = crear_usuario_con_onboarding(localidad=rio_ceballos, email="ajeno@example.com")

    assert formar(ajeno, encuentro.pk).status_code == 404


@pytest.mark.parametrize("id_encuentro", [999_999, 2_147_483_648])
def test_hu009_un_encuentro_inexistente_responde_404(jugadores, id_encuentro):
    respuesta = formar(jugadores[0], id_encuentro)

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_ENCUENTRO_INEXISTENTE}


def test_hu009_sin_sesion_responde_401(encuentro):
    respuesta = APIClient().post(f"/api/encuentros/{encuentro.pk}/formar-parejas")

    assert respuesta.status_code == 401


def test_hu009_p1_sin_cuatro_confirmados_responde_409(jugadores):
    encuentro = crear_encuentro(jugadores[0])

    respuesta = formar(jugadores[0], encuentro.pk)

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detalle": MENSAJE_SIN_CUATRO}


def test_hu009_con_propuesta_ya_generada_responde_409(encuentro, jugadores):
    formar(jugadores[0], encuentro.pk)

    respuesta = formar(jugadores[0], encuentro.pk)

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detalle": MENSAJE_YA_TIENE_PROPUESTA}


def test_hu009_un_encuentro_comenzado_responde_409(jugadores):
    ayer = timezone.localdate() - timedelta(days=1)
    encuentro = crear_encuentro_completo(*jugadores, fecha=ayer)

    respuesta = formar(jugadores[0], encuentro.pk)

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detalle": MENSAJE_YA_COMENZO}
