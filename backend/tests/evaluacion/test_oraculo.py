"""Oráculo lexicográfico y precision@k."""

from decimal import Decimal

import pytest

from evaluacion.oraculo import precision_en_k, ranking_oraculo
from motor.tipos import Recomendacion


def _recomendacion(identificador: int, dif_nivel: float, distancia_km: float) -> Recomendacion:
    # El puntaje no interviene en el oráculo: se pone al revés para comprobarlo.
    return Recomendacion(
        id=identificador,
        puntaje=Decimal(identificador),
        c_nivel=0.0,
        c_geo=0.0,
        c_tipo=0.0,
        distancia_km=distancia_km,
        dif_nivel=dif_nivel,
    )


def test_oraculo_ordena_por_nivel_despues_distancia_y_al_final_id():
    filtrados = (
        _recomendacion(1, 0.5, 2.0),
        _recomendacion(2, 0.0, 9.0),
        _recomendacion(3, 0.5, 1.0),
        _recomendacion(5, 0.0, 3.0),
        _recomendacion(4, 0.0, 3.0),
    )

    assert ranking_oraculo(filtrados) == (4, 5, 2, 3, 1)


def test_oraculo_sin_filtrados_da_ranking_vacio():
    assert ranking_oraculo(()) == ()


@pytest.mark.parametrize(
    ("motor", "referencia", "esperada"),
    [
        ((1, 2, 3), (4, 5, 6), 0),
        ((1, 2, 3, 4), (3, 5, 6), 1 / 3),
        ((1, 2, 3), (3, 1, 2, 7), 1),
    ],
)
def test_oraculo_precision_en_3(motor, referencia, esperada):
    assert precision_en_k(motor, referencia) == pytest.approx(esperada)


def test_oraculo_precision_con_menos_de_k_ids_lanza_error():
    with pytest.raises(ValueError):
        precision_en_k((1, 2), (1, 2, 3))
