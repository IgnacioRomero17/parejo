from decimal import Decimal

import pytest

from motor.parametros import Parametros
from motor.puntaje import criterio_geo, criterio_nivel, criterio_tipo, puntaje_recomendacion
from motor.tipos import COMPETITIVO, INDIFERENTE, RECREATIVO


@pytest.mark.parametrize(("dif_nivel", "esperado"), [(0.0, 1.0), (0.5, 0.5), (1.0, 0.0)])
def test_criterio_nivel(dif_nivel, esperado):
    assert criterio_nivel(dif_nivel) == pytest.approx(esperado)


@pytest.mark.parametrize(("distancia", "esperado"), [(0.0, 1.0), (10.0, 0.75), (40.0, 0.0)])
def test_criterio_geo(distancia, esperado):
    assert criterio_geo(distancia) == pytest.approx(esperado)


@pytest.mark.parametrize(
    ("tipo_encuentro", "tipo_preferido", "esperado"),
    [
        (COMPETITIVO, COMPETITIVO, 1.0),
        (COMPETITIVO, INDIFERENTE, 1.0),
        (INDIFERENTE, RECREATIVO, 1.0),
        (COMPETITIVO, None, 1.0),
        (COMPETITIVO, RECREATIVO, 0.0),
        (RECREATIVO, COMPETITIVO, 0.0),
    ],
)
def test_criterio_tipo(tipo_encuentro, tipo_preferido, esperado):
    assert criterio_tipo(tipo_encuentro, tipo_preferido) == esperado


def test_criterio_tipo_opuesto_usa_el_valor_de_los_parametros():
    parametros = Parametros(valor_tipo_opuesto=0.25)

    assert criterio_tipo(COMPETITIVO, RECREATIVO, parametros) == 0.25


def test_puntaje_es_la_suma_ponderada_redondeada():
    assert puntaje_recomendacion(1.0, 1.0, 1.0) == Decimal("1.0000")
    assert puntaje_recomendacion(0.5, 0.5, 0.0) == Decimal("0.4500")
    assert puntaje_recomendacion(1.0, 0.0, 0.0) == Decimal("0.6000")


def test_puntaje_usa_los_pesos_de_los_parametros():
    parametros = Parametros(peso_nivel=0.2, peso_geo=0.3, peso_tipo=0.5)

    assert puntaje_recomendacion(1.0, 0.0, 0.0, parametros) == Decimal("0.2000")
