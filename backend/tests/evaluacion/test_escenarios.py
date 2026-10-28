"""Escenarios dirigidos: cada uno da el resultado esperado."""

import pytest

from evaluacion.escenarios import ESCENARIOS_DIRIGIDOS
from motor.geo import haversine_km
from motor.recomendar import evaluar_candidato, recomendar

POR_NOMBRE = {escenario.nombre: escenario for escenario in ESCENARIOS_DIRIGIDOS}


def test_escenarios_son_los_5_de_la_regla():
    assert list(POR_NOMBRE) == [
        "nadie_compatible",
        "justo_lugares_libres",
        "empates",
        "mismo_nivel",
        "limites",
    ]


@pytest.mark.parametrize("escenario", ESCENARIOS_DIRIGIDOS, ids=lambda e: e.nombre)
def test_escenarios_dan_el_resultado_esperado(escenario):
    resultado = recomendar(escenario.encuentro, escenario.candidatos, escenario.lugares_libres)

    assert tuple(r.id for r in resultado.recomendados) == escenario.ids_esperados
    assert resultado.suficientes == escenario.suficientes_esperado


def test_escenarios_justo_lugares_libres_recomienda_tantos_como_lugares():
    escenario = POR_NOMBRE["justo_lugares_libres"]

    assert len(escenario.ids_esperados) == escenario.lugares_libres


def test_escenarios_empates_se_resuelven_por_id_con_puntajes_iguales():
    escenario = POR_NOMBRE["empates"]
    resultado = recomendar(escenario.encuentro, escenario.candidatos, escenario.lugares_libres)
    puntajes = {r.id: r.puntaje for r in resultado.recomendados}

    assert puntajes[3] == puntajes[4] == puntajes[5]
    assert puntajes[6] == puntajes[7]


def test_escenarios_mismo_nivel_sin_diferencia_de_nivel():
    escenario = POR_NOMBRE["mismo_nivel"]
    resultado = recomendar(escenario.encuentro, escenario.candidatos, escenario.lugares_libres)

    assert {candidato.nivel for candidato in escenario.candidatos} == set(
        escenario.encuentro.niveles_confirmados
    )
    assert all(r.dif_nivel == 0 for r in resultado.recomendados)


def test_escenarios_limites_pasan_o_no_los_filtros_de_distancia_y_nivel():
    escenario = POR_NOMBRE["limites"]
    encuentro = escenario.encuentro
    evaluados = {
        candidato.id: evaluar_candidato(candidato, encuentro, 4.0)
        for candidato in escenario.candidatos
    }
    distancias = {
        candidato.id: haversine_km(encuentro.lat, encuentro.lon, candidato.lat, candidato.lon)
        for candidato in escenario.candidatos
    }

    assert evaluados[2].dif_nivel == 1.0 and evaluados[2].c_nivel == 0
    assert evaluados[6].dif_nivel == 1.0 and evaluados[6].c_nivel == 0
    assert evaluados[3] is None
    assert 39.8 < distancias[4] <= 40 and evaluados[4] is not None
    assert 40 < distancias[5] < 40.2 and evaluados[5] is None
