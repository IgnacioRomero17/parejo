"""Líneas base de la etapa 2: cada una elige la combinación que dice su regla."""

import random

import pytest

from evaluacion.lineas_base import aleatoria, mas_fuertes_juntos, orden_de_llegada
from motor.equilibrio import evaluar_combinaciones
from motor.tipos import DRIVE, REVES, JugadorEntrada


def _grupo(*niveles: float) -> tuple[JugadorEntrada, ...]:
    return tuple(
        JugadorEntrada(id=identificador, nivel=nivel, lado=DRIVE if identificador % 2 else REVES)
        for identificador, nivel in enumerate(niveles, start=1)
    )


def test_lineas_base_orden_de_llegada_es_la_combinacion_1():
    combinaciones = evaluar_combinaciones(_grupo(3.0, 4.0, 5.0, 6.0))

    elegida = orden_de_llegada(tuple(reversed(combinaciones)))

    assert elegida.numero == 1
    assert (elegida.pareja1, elegida.pareja2) == ((1, 2), (3, 4))


@pytest.mark.parametrize(
    ("niveles", "pareja_esperada"),
    [
        ((5.0, 5.0, 3.0, 3.0), (1, 2)),
        ((3.0, 5.0, 3.0, 5.0), (2, 4)),
        ((6.0, 3.0, 4.0, 2.0), (1, 3)),
    ],
)
def test_lineas_base_mas_fuertes_juntos_forman_pareja(niveles, pareja_esperada):
    grupo = _grupo(*niveles)

    elegida = mas_fuertes_juntos(grupo, evaluar_combinaciones(grupo))

    assert pareja_esperada in (elegida.pareja1, elegida.pareja2)


def test_lineas_base_mas_fuertes_juntos_desempata_por_id():
    # 2, 3 y 4 empatan en el nivel más alto: los más fuertes son 2 y 3, por id.
    grupo = _grupo(3.0, 5.0, 5.0, 5.0)

    elegida = mas_fuertes_juntos(grupo, evaluar_combinaciones(grupo))

    assert elegida.numero == 3
    assert elegida.pareja2 == (2, 3)


def test_lineas_base_aleatoria_reproducible_con_la_semilla():
    combinaciones = evaluar_combinaciones(_grupo(3.0, 4.0, 5.0, 6.0))

    primera = [aleatoria(combinaciones, random.Random(7)) for _ in range(3)]
    generador = random.Random(7)
    serie = [aleatoria(combinaciones, generador).numero for _ in range(30)]
    repetida = random.Random(7)

    assert primera[0] == primera[1] == primera[2]
    assert serie == [aleatoria(combinaciones, repetida).numero for _ in range(30)]
    assert set(serie) == {1, 2, 3}
