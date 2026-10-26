from decimal import Decimal

import pytest

from motor.geo import haversine_km
from motor.parametros import Parametros
from motor.redondeo import redondear4


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (0.55, "0.5500"),
        (0.12345, "0.1235"),
        (0.12344999, "0.1234"),
        (1.0, "1.0000"),
        (0.0, "0.0000"),
    ],
)
def test_redondear4_a_cuatro_decimales_con_la_mitad_hacia_arriba(valor, esperado):
    assert redondear4(valor) == Decimal(esperado)


def test_haversine_mismo_punto_da_cero():
    assert haversine_km(-31.1653, -64.3253, -31.1653, -64.3253) == 0.0


def test_haversine_rio_ceballos_unquillo():
    assert haversine_km(-31.1653, -64.3253, -31.2306, -64.3175) == pytest.approx(7.299, abs=5e-4)


def test_haversine_es_simetrica():
    ida = haversine_km(-31.1653, -64.3253, -31.34, -64.335)
    vuelta = haversine_km(-31.34, -64.335, -31.1653, -64.3253)

    assert ida == pytest.approx(vuelta)


def test_haversine_usa_el_radio_de_los_parametros():
    normal = haversine_km(-31.1653, -64.3253, -31.2306, -64.3175)
    doble = haversine_km(
        -31.1653, -64.3253, -31.2306, -64.3175, Parametros(radio_tierra_km=12742.0)
    )

    assert doble == pytest.approx(2 * normal)
