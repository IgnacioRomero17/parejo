"""Propiedades de la etapa 1 sobre datos generados con semilla fija."""

import random
from datetime import date, time, timedelta

import pytest

from motor.recomendar import recomendar
from motor.redondeo import redondear4
from motor.tipos import (
    COMPETITIVO,
    INDIFERENTE,
    RECREATIVO,
    CandidatoEntrada,
    EncuentroEntrada,
    Franja,
)

SEMILLA = 2026
TIPOS = (RECREATIVO, COMPETITIVO, INDIFERENTE)
NIVELES = tuple(x / 2 for x in range(2, 15))  # 1,0 a 7,0 en pasos de 0,5
DURACIONES = (60, 90, 120)


def _coordenadas(generador: random.Random) -> tuple[float, float]:
    # Un recuadro alrededor de las localidades del catálogo, con algunas a más de 40 km.
    return generador.uniform(-31.5, -31.0), generador.uniform(-64.5, -64.1)


def _franja(generador: random.Random) -> Franja:
    inicio = generador.randrange(16, 44)  # medias horas desde las 08:00 hasta las 21:30
    largo = generador.randrange(4, 13)
    fin = min(inicio + largo, 47)
    return Franja(
        dia=generador.randint(1, 7),
        inicio=time(inicio // 2, 30 * (inicio % 2)),
        fin=time(fin // 2, 30 * (fin % 2)),
    )


def _candidato(generador: random.Random, identificador: int) -> CandidatoEntrada:
    lat, lon = _coordenadas(generador)
    sin_localidad = generador.random() < 0.05
    return CandidatoEntrada(
        id=identificador,
        activo=generador.random() < 0.95,
        disponible=generador.random() < 0.85,
        nivel=None if generador.random() < 0.05 else generador.choice(NIVELES),
        lat=None if sin_localidad else lat,
        lon=None if sin_localidad else lon,
        tipo_preferido=None if generador.random() < 0.05 else generador.choice(TIPOS),
        franjas=tuple(_franja(generador) for _ in range(generador.randint(0, 4))),
    )


def _encuentro(generador: random.Random, ids: list[int]) -> EncuentroEntrada:
    lat, lon = _coordenadas(generador)
    confirmados = generador.sample(ids, generador.randint(1, 3))
    invitados = generador.sample(ids, generador.randint(0, 3))
    hora = generador.randrange(16, 41)
    return EncuentroEntrada(
        fecha=date(2026, 10, 1) + timedelta(days=generador.randrange(14)),
        hora_inicio=time(hora // 2, 30 * (hora % 2)),
        duracion_minutos=generador.choice(DURACIONES),
        lat=lat,
        lon=lon,
        tipo=generador.choice(TIPOS),
        niveles_confirmados=tuple(generador.choice(NIVELES) for _ in confirmados),
        ids_excluidos=frozenset(confirmados + invitados),
    )


def _escenarios():
    generador = random.Random(SEMILLA)
    candidatos = tuple(_candidato(generador, identificador) for identificador in range(1, 201))
    ids = [c.id for c in candidatos]
    return [(_encuentro(generador, ids), candidatos) for _ in range(60)]


ESCENARIOS = _escenarios()


@pytest.mark.parametrize(("encuentro", "candidatos"), ESCENARIOS)
def test_propiedades_de_la_etapa1(encuentro, candidatos):
    resultado = recomendar(encuentro, candidatos, 3)
    puntajes = [r.puntaje for r in resultado.recomendados]
    umbral = redondear4(0.55)

    assert not {r.id for r in resultado.recomendados} & encuentro.ids_excluidos
    assert puntajes == sorted(puntajes, reverse=True)
    assert all(umbral <= puntaje <= 1 for puntaje in puntajes)
    assert recomendar(encuentro, candidatos, 3) == resultado


@pytest.mark.parametrize(("encuentro", "candidatos"), ESCENARIOS[:10])
def test_el_orden_de_entrada_no_cambia_el_resultado(encuentro, candidatos):
    mezclados = list(candidatos)
    random.Random(SEMILLA).shuffle(mezclados)

    assert recomendar(encuentro, tuple(mezclados), 3) == recomendar(encuentro, candidatos, 3)


def test_los_escenarios_generados_recomiendan_a_alguien():
    # Evita que las propiedades pasen sin probar nada porque nunca hay recomendados.
    con_recomendados = sum(1 for e, c in ESCENARIOS if recomendar(e, c, 3).recomendados)

    assert con_recomendados >= len(ESCENARIOS) // 2
