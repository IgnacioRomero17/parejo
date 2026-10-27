"""Etapa 2: evaluación de las 3 combinaciones y elección de la mejor."""

import random
from dataclasses import replace
from decimal import Decimal

import pytest

from motor.equilibrio import (
    elegir_mejor,
    equilibrio_lado,
    equilibrio_nivel,
    evaluar_combinaciones,
    lado_pareja,
    puntaje_equilibrio,
)
from motor.parametros import Parametros
from motor.tipos import DRIVE, INDIFERENTE, REVES, CombinacionResultado, JugadorEntrada

SEMILLA = 2026
NIVELES = tuple(x / 2 for x in range(2, 15))  # 1,0 a 7,0 en pasos de 0,5
LADOS = (DRIVE, REVES, INDIFERENTE, None)


def jugadores(*niveles_y_lados, ids=(1, 2, 3, 4)) -> tuple[JugadorEntrada, ...]:
    return tuple(
        JugadorEntrada(id=identificador, nivel=nivel, lado=lado)
        for identificador, (nivel, lado) in zip(ids, niveles_y_lados, strict=True)
    )


CUATRO = jugadores((4.0, DRIVE), (4.5, REVES), (5.0, DRIVE), (3.5, REVES))


def combinacion(numero, puntaje, promedio1=4.5, promedio2=4.5, eq_lado=1.0):
    return CombinacionResultado(
        numero=numero,
        pareja1=(1, 2),
        pareja2=(3, 4),
        promedio1=promedio1,
        promedio2=promedio2,
        eq_nivel=1.0,
        eq_lado=eq_lado,
        puntaje=Decimal(puntaje),
    )


# Combinaciones


def test_equilibrio_siempre_3_combinaciones_en_orden_por_id():
    desordenados = tuple(replace(j, id=i) for j, i in zip(CUATRO, (40, 10, 30, 20), strict=True))

    resultado = evaluar_combinaciones(desordenados[::-1])

    assert [c.numero for c in resultado] == [1, 2, 3]
    assert [(c.pareja1, c.pareja2) for c in resultado] == [
        ((10, 20), (30, 40)),
        ((10, 30), (20, 40)),
        ((10, 40), (20, 30)),
    ]


def test_equilibrio_cada_jugador_en_una_sola_pareja_y_nadie_excluido():
    for c in evaluar_combinaciones(CUATRO):
        integrantes = [*c.pareja1, *c.pareja2]
        assert sorted(integrantes) == [1, 2, 3, 4]
        assert 1 in c.pareja1


def test_equilibrio_las_3_combinaciones_son_distintas():
    resultado = evaluar_combinaciones(CUATRO)

    conformaciones = {frozenset({frozenset(c.pareja1), frozenset(c.pareja2)}) for c in resultado}
    assert len(conformaciones) == 3


def test_equilibrio_calcula_promedios_por_pareja():
    primera = evaluar_combinaciones(CUATRO)[0]  # (4,0 + 4,5) vs (5,0 + 3,5)

    assert (primera.promedio1, primera.promedio2) == (pytest.approx(4.25), pytest.approx(4.25))


@pytest.mark.parametrize(
    "jugadores_invalidos",
    [
        CUATRO[:3],
        (*CUATRO, JugadorEntrada(id=5, nivel=4.0, lado=DRIVE)),
        (*CUATRO[:3], replace(CUATRO[3], id=1)),
        (*CUATRO[:3], replace(CUATRO[3], nivel=None)),
    ],
    ids=["tres", "cinco", "id_repetido", "nivel_nulo"],
)
def test_equilibrio_rechaza_entradas_invalidas(jugadores_invalidos):
    with pytest.raises(ValueError):
        evaluar_combinaciones(jugadores_invalidos)


# Criterios y puntaje


@pytest.mark.parametrize(
    ("promedio1", "promedio2", "esperado"),
    [(4.75, 4.75, 1.0), (4.5, 5.0, 0.75), (3.0, 5.0, 0.0), (1.0, 7.0, 0.0)],
)
def test_equilibrio_nivel(promedio1, promedio2, esperado):
    assert equilibrio_nivel(promedio1, promedio2) == pytest.approx(esperado)


@pytest.mark.parametrize(
    ("lado1", "lado2", "esperado"),
    [
        (DRIVE, REVES, 1.0),
        (REVES, DRIVE, 1.0),
        (DRIVE, DRIVE, 0.0),
        (REVES, REVES, 0.0),
        (INDIFERENTE, DRIVE, 1.0),
        (INDIFERENTE, INDIFERENTE, 1.0),
        (None, REVES, 1.0),
        (None, None, 1.0),
    ],
)
def test_equilibrio_lado_de_una_pareja(lado1, lado2, esperado):
    assert lado_pareja(lado1, lado2) == esperado


def test_equilibrio_lado_es_el_promedio_de_las_dos_parejas():
    drive, reves, otro_drive = jugadores((4.0, DRIVE), (4.0, REVES), (4.0, DRIVE), (4.0, DRIVE))[:3]

    assert equilibrio_lado((drive, reves), (drive, otro_drive)) == 0.5


def test_equilibrio_puntaje_redondeado_a_4_decimales():
    assert puntaje_equilibrio(1 / 3, 1.0) == Decimal("0.4667")


def test_equilibrio_usa_los_parametros_recibidos():
    parametros = Parametros(
        d_max_equilibrio=1.0, peso_equilibrio_nivel=0.5, peso_equilibrio_lado=0.5
    )
    iguales = jugadores((4.0, DRIVE), (4.0, DRIVE), (5.0, DRIVE), (5.0, DRIVE))

    primera = evaluar_combinaciones(iguales, parametros)[0]  # 4,0 vs 5,0; repiten lado

    assert primera.eq_nivel == 0.0
    assert primera.puntaje == Decimal("0.0000")


# Elección


def test_elegir_mejor_por_mayor_puntaje():
    elegida = elegir_mejor((combinacion(1, "0.8"), combinacion(2, "0.9"), combinacion(3, "0.7")))

    assert elegida.numero == 2


def test_elegir_mejor_con_empate_de_puntaje_menor_diferencia_de_promedios():
    elegida = elegir_mejor(
        (
            combinacion(1, "0.8", promedio1=4.0, promedio2=5.0),
            combinacion(2, "0.8", promedio1=4.5, promedio2=4.75),
            combinacion(3, "0.8", promedio1=5.0, promedio2=4.5),
        )
    )

    assert elegida.numero == 2


def test_elegir_mejor_con_empate_de_diferencia_mayor_equilibrio_de_lado():
    elegida = elegir_mejor(
        (
            combinacion(1, "0.8", eq_lado=0.5),
            combinacion(2, "0.8", eq_lado=0.5),
            combinacion(3, "0.8", eq_lado=1.0),
        )
    )

    assert elegida.numero == 3


def test_elegir_mejor_con_empate_total_menor_numero():
    elegida = elegir_mejor((combinacion(3, "0.8"), combinacion(2, "0.8"), combinacion(1, "0.8")))

    assert elegida.numero == 1


def test_elegir_mejor_con_empate_total_real_elige_la_1():
    iguales = jugadores((4.0, INDIFERENTE), (4.0, INDIFERENTE), (4.0, None), (4.0, None))

    assert elegir_mejor(evaluar_combinaciones(iguales)).numero == 1


def test_elegir_mejor_sin_combinaciones():
    with pytest.raises(ValueError):
        elegir_mejor(())


# Propiedades sobre datos generados


def _cuatro_al_azar(generador: random.Random) -> tuple[JugadorEntrada, ...]:
    ids = generador.sample(range(1, 500), 4)
    return tuple(
        JugadorEntrada(id=i, nivel=generador.choice(NIVELES), lado=generador.choice(LADOS))
        for i in ids
    )


CASOS = [_cuatro_al_azar(random.Random(SEMILLA + n)) for n in range(200)]


@pytest.mark.parametrize("cuatro", CASOS[:50])
def test_equilibrio_propiedades(cuatro):
    resultado = evaluar_combinaciones(cuatro)

    ids = sorted(j.id for j in cuatro)
    assert len(resultado) == 3
    for c in resultado:
        assert sorted([*c.pareja1, *c.pareja2]) == ids
        assert Decimal(0) <= c.puntaje <= Decimal(1)
    assert evaluar_combinaciones(cuatro) == resultado
    assert evaluar_combinaciones(tuple(reversed(cuatro))) == resultado


def test_equilibrio_la_elegida_tiene_el_mayor_puntaje():
    for cuatro in CASOS:
        resultado = evaluar_combinaciones(cuatro)
        assert elegir_mejor(resultado).puntaje == max(c.puntaje for c in resultado)
