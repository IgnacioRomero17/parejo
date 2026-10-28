"""`GET encuentros/{id}/propuesta` (HU-011 y HU-012) con el caso de ejemplo de la regla del
motor: Tomás (4,5, Drive), Valentina (4,5, Revés), Camila (5,0, Revés) y Federico (5,0, Drive)."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.encuentros import servicios
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
MENSAJE_SIN_PROPUESTA = "Este encuentro todavía no tiene una propuesta."


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
    encuentro = crear_encuentro_completo(*jugadores)
    servicios.formar_parejas(encuentro)
    return encuentro


def consultar(usuario, id_encuentro):
    cliente = APIClient()
    cliente.force_login(usuario)
    return cliente.get(f"/api/encuentros/{id_encuentro}/propuesta")


def integrantes_de(pareja) -> list[str]:
    return [persona["nombre"] for persona in pareja["integrantes"]]


@pytest.mark.parametrize("posicion", range(4))
def test_hu012_c1_cada_participante_puede_ver_la_propuesta(encuentro, jugadores, posicion):
    respuesta = consultar(jugadores[posicion], encuentro.pk)

    assert respuesta.status_code == 200
    assert respuesta.json()["encuentro"]["id"] == encuentro.pk


def test_hu011_c2_hu012_c2_incluye_fecha_horario_localidad_y_direccion(encuentro, rio_ceballos):
    datos = consultar(encuentro.organizador, encuentro.pk).json()["encuentro"]

    assert datos["fecha"] == encuentro.fecha.isoformat()
    assert (datos["hora_inicio"], datos["duracion_minutos"]) == ("18:00", 90)
    assert datos["localidad"] == {"id": rio_ceballos.pk, "nombre": "Río Ceballos"}
    assert datos["ubicacion"] == "Av. San Martín 4500"
    assert datos["tipo_encuentro"] == "COMPETITIVO"
    assert datos["estado"] == "PROPUESTA_GENERADA"


def test_hu011_c3_hu012_c2_muestra_las_dos_parejas_y_el_resultado(encuentro, jugadores):
    datos = consultar(jugadores[1], encuentro.pk).json()

    assert datos["combinacion_elegida"] == 2
    assert datos["puntaje_equilibrio"] == 1.0
    elegida = datos["combinaciones"][1]
    assert [(p["numero"], p["promedio"], integrantes_de(p)) for p in elegida["parejas"]] == [
        (1, 4.75, ["Tomás", "Camila"]),
        (2, 4.75, ["Valentina", "Federico"]),
    ]
    tomas = elegida["parejas"][0]["integrantes"][0]
    assert tomas["localidad"]["nombre"] == "Río Ceballos"
    assert (tomas["nivel"], tomas["lado"]) == (4.5, "DRIVE")


def test_hu012_p3_trae_las_3_combinaciones_con_sus_puntajes(encuentro, jugadores):
    datos = consultar(jugadores[2], encuentro.pk).json()

    assert [
        (
            c["numero"],
            c["puntaje_equilibrio"],
            [p["promedio"] for p in c["parejas"]],
            c["equilibrio_nivel"],
            c["equilibrio_lado"],
        )
        for c in datos["combinaciones"]
    ] == [
        (1, 0.8, [4.5, 5.0], 0.75, 1.0),
        (2, 1.0, [4.75, 4.75], 1.0, 1.0),
        (3, 0.8, [4.75, 4.75], 1.0, 0.0),
    ]


def test_hu012_p4_el_puntaje_es_el_guardado_y_los_promedios_se_recalculan(encuentro, jugadores):
    camila = jugadores[2]
    camila.nivel_estimado = Decimal("6.0")
    camila.save(update_fields=["nivel_estimado"])

    datos = consultar(jugadores[0], encuentro.pk).json()

    elegida = datos["combinaciones"][1]
    assert datos["puntaje_equilibrio"] == elegida["puntaje_equilibrio"] == 1.0
    assert [p["promedio"] for p in elegida["parejas"]] == [5.25, 4.75]
    assert elegida["equilibrio_nivel"] == 0.75


def test_hu012_no_expone_edad_ni_genero(encuentro, jugadores):
    datos = consultar(jugadores[3], encuentro.pk).json()

    for combinacion in datos["combinaciones"]:
        for pareja in combinacion["parejas"]:
            for persona in pareja["integrantes"]:
                assert "edad" not in persona
                assert "genero" not in persona


def test_hu012_p1_un_usuario_ajeno_recibe_404(encuentro, rio_ceballos):
    ajeno = crear_usuario_con_onboarding(localidad=rio_ceballos, email="ajeno@example.com")

    respuesta = consultar(ajeno, encuentro.pk)

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_ENCUENTRO_INEXISTENTE}


@pytest.mark.parametrize("id_encuentro", [999_999, 2_147_483_648])
def test_hu012_un_encuentro_inexistente_responde_404(jugadores, id_encuentro):
    respuesta = consultar(jugadores[0], id_encuentro)

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_ENCUENTRO_INEXISTENTE}


def test_hu012_sin_sesion_responde_401(encuentro):
    respuesta = APIClient().get(f"/api/encuentros/{encuentro.pk}/propuesta")

    assert respuesta.status_code == 401


def test_hu012_sin_propuesta_generada_responde_409(jugadores):
    encuentro = crear_encuentro(jugadores[0])

    respuesta = consultar(jugadores[0], encuentro.pk)

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detalle": MENSAJE_SIN_PROPUESTA}
