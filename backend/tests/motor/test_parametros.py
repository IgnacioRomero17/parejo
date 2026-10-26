import pytest

from motor.parametros import PARAMETROS, Parametros


def test_parametros_valores_iniciales_de_la_regla():
    assert PARAMETROS.dif_max_nivel == 1.0
    assert PARAMETROS.dist_max_km == 40.0
    assert PARAMETROS.umbral_minimo == 0.55
    assert (PARAMETROS.peso_nivel, PARAMETROS.peso_geo, PARAMETROS.peso_tipo) == (0.6, 0.3, 0.1)
    assert PARAMETROS.valor_tipo_opuesto == 0.0
    assert PARAMETROS.d_max_equilibrio == 2.0
    assert (PARAMETROS.peso_equilibrio_nivel, PARAMETROS.peso_equilibrio_lado) == (0.8, 0.2)
    assert PARAMETROS.lugares_por_encuentro == 4
    assert PARAMETROS.radio_tierra_km == 6371.0


def test_parametros_acepta_otros_pesos_que_suman_1():
    parametros = Parametros(peso_nivel=0.5, peso_geo=0.4, peso_tipo=0.1)

    assert parametros.peso_nivel == 0.5


@pytest.mark.parametrize(
    "campos",
    [
        {"peso_nivel": 0.7},
        {"peso_equilibrio_lado": 0.3},
    ],
)
def test_parametros_rechaza_pesos_que_no_suman_1(campos):
    with pytest.raises(ValueError, match="sumar 1"):
        Parametros(**campos)


@pytest.mark.parametrize(
    "campo",
    [
        "dif_max_nivel",
        "dist_max_km",
        "d_max_equilibrio",
        "lugares_por_encuentro",
        "radio_tierra_km",
    ],
)
def test_parametros_rechaza_maximos_no_positivos(campo):
    with pytest.raises(ValueError, match=campo):
        Parametros(**{campo: 0})
