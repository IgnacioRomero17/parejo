"""Generadores sintéticos: reproducibles con la semilla y fieles a las distribuciones."""

import random
from collections import Counter
from datetime import time, timedelta
from statistics import fmean, stdev

import pytest

from evaluacion.generador import (
    FECHA_BASE,
    SEMILLA,
    generar_escenarios,
    generar_jugadores,
)
from evaluacion.localidades import LOCALIDADES
from motor.tipos import COMPETITIVO, DRIVE, INDIFERENTE, RECREATIVO, REVES

JUGADORES = generar_jugadores()
CANDIDATOS = [jugador.candidato for jugador in JUGADORES]
FRANJAS = [franja for candidato in CANDIDATOS for franja in candidato.franjas]
ESCENARIOS = generar_escenarios(JUGADORES)
TOLERANCIA_PROPORCION = 0.08
# Valor crítico de χ² con 15 grados de libertad (16 localidades) y α = 0,001.
CHI2_CRITICO_15_GL = 37.697


def _minutos(hora: time) -> int:
    return hora.hour * 60 + hora.minute


def _proporciones(valores) -> dict:
    conteo = Counter(valores)
    return {clave: cantidad / len(valores) for clave, cantidad in conteo.items()}


def test_generador_misma_semilla_mismos_jugadores():
    assert generar_jugadores(SEMILLA) == JUGADORES


def test_generador_otra_semilla_otros_jugadores():
    assert generar_jugadores(SEMILLA + 1) != JUGADORES


def test_generador_misma_semilla_mismos_escenarios():
    assert generar_escenarios(JUGADORES, SEMILLA) == ESCENARIOS
    assert generar_escenarios(JUGADORES, SEMILLA + 1) != ESCENARIOS


def test_generador_no_usa_el_random_global():
    random.seed(1)
    antes = random.random()
    random.seed(1)
    generar_jugadores()
    generar_escenarios(JUGADORES)

    assert random.random() == antes


def test_generador_200_jugadores_con_ids_del_1_al_200():
    assert [candidato.id for candidato in CANDIDATOS] == list(range(1, 201))


def test_generador_nivel_en_medios_puntos_entre_1_y_7():
    niveles = [candidato.nivel for candidato in CANDIDATOS]

    assert all(1 <= nivel <= 7 and (nivel * 2).is_integer() for nivel in niveles)


def test_generador_nivel_con_media_4_y_desvio_1_2():
    niveles = [candidato.nivel for candidato in CANDIDATOS]

    assert fmean(niveles) == pytest.approx(4, abs=0.3)
    assert stdev(niveles) == pytest.approx(1.2, abs=0.25)


def test_generador_localidad_uniforme_sobre_el_catalogo():
    conteo = Counter(jugador.localidad for jugador in JUGADORES)
    esperado = len(JUGADORES) / len(LOCALIDADES)
    chi2 = sum((conteo[localidad] - esperado) ** 2 / esperado for localidad in LOCALIDADES)

    assert set(conteo) <= set(LOCALIDADES)
    assert chi2 < CHI2_CRITICO_15_GL
    assert all(
        (candidato.lat, candidato.lon) == (jugador.localidad.lat, jugador.localidad.lon)
        for jugador, candidato in zip(JUGADORES, CANDIDATOS, strict=True)
    )


@pytest.mark.parametrize(
    ("atributo", "esperadas"),
    [
        ("tipo", {RECREATIVO: 0.35, COMPETITIVO: 0.35, INDIFERENTE: 0.30}),
        ("lado", {DRIVE: 0.40, REVES: 0.40, INDIFERENTE: 0.20}),
        ("disponible", {True: 0.85, False: 0.15}),
    ],
)
def test_generador_proporciones_de_tipo_lado_y_disponible(atributo, esperadas):
    valores = {
        "tipo": [candidato.tipo_preferido for candidato in CANDIDATOS],
        "lado": [jugador.lado for jugador in JUGADORES],
        "disponible": [candidato.disponible for candidato in CANDIDATOS],
    }[atributo]
    proporciones = _proporciones(valores)

    assert set(proporciones) == set(esperadas)
    for clave, esperada in esperadas.items():
        assert proporciones[clave] == pytest.approx(esperada, abs=TOLERANCIA_PROPORCION)


def test_generador_todos_activos():
    assert all(candidato.activo for candidato in CANDIDATOS)


def test_generador_de_1_a_3_franjas_en_dias_distintos():
    for candidato in CANDIDATOS:
        dias = [franja.dia for franja in candidato.franjas]

        assert 1 <= len(dias) <= 3
        assert len(set(dias)) == len(dias)


def test_generador_franjas_de_2_a_4_horas_entre_las_8_y_las_23():
    for franja in FRANJAS:
        duracion = _minutos(franja.fin) - _minutos(franja.inicio)

        assert 120 <= duracion <= 240
        assert franja.inicio.minute in (0, 30) and franja.fin.minute in (0, 30)
        assert time(8) <= franja.inicio and franja.fin <= time(23)


def test_generador_el_fin_de_semana_tiene_mas_franjas():
    por_dia = Counter(franja.dia for franja in FRANJAS)
    habiles = [por_dia[dia] for dia in range(1, 6)]

    assert min(por_dia[6], por_dia[7]) > max(habiles)


def test_generador_150_escenarios_con_solo_el_organizador():
    ids = {candidato.id for candidato in CANDIDATOS}
    niveles = {candidato.id: candidato.nivel for candidato in CANDIDATOS}

    assert [escenario.numero for escenario in ESCENARIOS] == list(range(1, 151))
    for escenario in ESCENARIOS:
        assert escenario.organizador_id in ids
        assert escenario.encuentro.ids_excluidos == {escenario.organizador_id}
        assert escenario.encuentro.niveles_confirmados == (niveles[escenario.organizador_id],)
        assert escenario.lugares_libres == 3


def test_generador_escenarios_dentro_de_los_rangos():
    coordenadas = {(localidad.lat, localidad.lon) for localidad in LOCALIDADES}

    for escenario in ESCENARIOS:
        encuentro = escenario.encuentro

        assert FECHA_BASE < encuentro.fecha <= FECHA_BASE + timedelta(days=14)
        assert time(8) <= encuentro.hora_inicio <= time(21, 30)
        assert encuentro.hora_inicio.minute in (0, 30)
        assert encuentro.duracion_minutos in (60, 90, 120)
        assert (encuentro.lat, encuentro.lon) in coordenadas
        assert encuentro.tipo in (RECREATIVO, COMPETITIVO, INDIFERENTE)
