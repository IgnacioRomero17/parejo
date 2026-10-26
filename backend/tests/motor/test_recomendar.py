from decimal import Decimal

import pytest

from motor.parametros import Parametros
from motor.recomendar import nivel_promedio, recomendar
from motor.tipos import RECREATIVO
from tests.motor.entradas import CANDIDATO, ENCUENTRO, candidato, encuentro

UNQUILLO = (-31.2306, -64.3175)


def ids(resultado):
    return [r.id for r in resultado.recomendados]


def test_promedio_con_solo_el_organizador_es_su_nivel():
    resultado = recomendar(encuentro(niveles_confirmados=(4.5,)), (candidato(nivel=5.0),), 3)

    assert nivel_promedio((4.5,)) == 4.5
    assert resultado.recomendados[0].dif_nivel == 0.5


def test_promedio_no_entero_con_tres_confirmados():
    tres = encuentro(niveles_confirmados=(4.5, 5.0, 4.5))
    resultado = recomendar(tres, (candidato(id=2, nivel=4.5), candidato(id=3, nivel=5.0)), 1)

    assert round(nivel_promedio((4.5, 5.0, 4.5)), 4) == 4.6667
    assert [(r.id, r.puntaje) for r in resultado.recomendados] == [
        (2, Decimal("0.9000")),
        (3, Decimal("0.8000")),
    ]


def test_sin_niveles_confirmados_lanza_error():
    with pytest.raises(ValueError, match="nivel confirmado"):
        recomendar(encuentro(niveles_confirmados=()), (CANDIDATO,), 3)


def test_lugares_libres_negativos_lanza_error():
    with pytest.raises(ValueError, match="negativos"):
        recomendar(ENCUENTRO, (CANDIDATO,), -1)


def test_puntaje_igual_al_umbral_se_recomienda():
    # Promedio 4,25 y nivel 5,0: c_nivel = 0,25 → 0,6·0,25 + 0,3·1 + 0,1·1 = 0,55.
    resultado = recomendar(encuentro(niveles_confirmados=(4.5, 4.0)), (candidato(nivel=5.0),), 2)

    assert [r.puntaje for r in resultado.recomendados] == [Decimal("0.5500")]


def test_puntaje_debajo_del_umbral_no_se_recomienda():
    # Mismo caso con tipo opuesto: 0,15 + 0,3 = 0,45.
    lejano = candidato(nivel=5.0, tipo_preferido=RECREATIVO)
    resultado = recomendar(encuentro(niveles_confirmados=(4.5, 4.0)), (lejano,), 2)

    assert resultado.recomendados == ()


def test_diferencia_de_nivel_en_el_limite_pasa_el_filtro_pero_no_el_umbral():
    resultado = recomendar(ENCUENTRO, (candidato(nivel=5.5),), 3)

    assert resultado.recomendados == ()


def test_el_umbral_sale_de_los_parametros():
    lejano = candidato(nivel=5.0, tipo_preferido=RECREATIVO)
    parametros = Parametros(umbral_minimo=0.45)
    resultado = recomendar(encuentro(niveles_confirmados=(4.5, 4.0)), (lejano,), 2, parametros)

    assert ids(resultado) == [2]


@pytest.mark.parametrize(("lugares_libres", "suficientes"), [(3, False), (0, True)])
def test_cero_candidatos(lugares_libres, suficientes):
    resultado = recomendar(ENCUENTRO, (), lugares_libres)

    assert resultado.recomendados == ()
    assert resultado.suficientes is suficientes


def test_descarta_a_quien_no_pasa_un_filtro():
    candidatos = (
        candidato(id=1),  # el organizador, excluido
        candidato(id=2),
        candidato(id=3, activo=False),
        candidato(id=4, disponible=False),
        candidato(id=5, nivel=None),
        candidato(id=6, lat=None, lon=None),
        candidato(id=7, franjas=()),
        candidato(id=8, lat=-31.75, lon=-64.3253),  # a unos 65 km
        candidato(id=9, nivel=6.0),
    )

    assert ids(recomendar(ENCUENTRO, candidatos, 3)) == [2]


def test_candidato_sin_preferencia_cuenta_el_tipo_como_coincidente():
    resultado = recomendar(ENCUENTRO, (candidato(tipo_preferido=None),), 3)

    assert resultado.recomendados[0].c_tipo == 1.0


def test_no_recorta_a_los_lugares_libres():
    candidatos = tuple(candidato(id=identificador) for identificador in range(2, 8))
    resultado = recomendar(ENCUENTRO, candidatos, 3)

    assert len(resultado.recomendados) == 6
    assert resultado.suficientes


def test_menos_candidatos_que_lugares_libres_no_son_suficientes():
    resultado = recomendar(ENCUENTRO, (candidato(id=2), candidato(id=3)), 3)

    assert len(resultado.recomendados) == 2
    assert not resultado.suficientes


def test_ordena_por_puntaje_descendente():
    candidatos = (
        candidato(id=2, nivel=5.0),
        candidato(id=3, lat=UNQUILLO[0], lon=UNQUILLO[1]),
        candidato(id=4),
    )

    assert ids(recomendar(ENCUENTRO, candidatos, 3)) == [4, 3, 2]


def test_desempata_por_diferencia_de_nivel_distancia_e_id():
    # Con todo el peso en el tipo, todos tienen puntaje 1 y deciden los desempates.
    solo_tipo = Parametros(peso_nivel=0.0, peso_geo=0.0, peso_tipo=1.0)
    candidatos = (
        candidato(id=2, nivel=5.0),
        candidato(id=3, lat=UNQUILLO[0], lon=UNQUILLO[1]),
        candidato(id=5),
        candidato(id=4),
    )
    resultado = recomendar(ENCUENTRO, candidatos, 3, solo_tipo)

    assert {r.puntaje for r in resultado.recomendados} == {Decimal("1.0000")}
    assert ids(resultado) == [4, 5, 3, 2]


def test_empate_total_se_resuelve_por_id():
    candidatos = (candidato(id=9), candidato(id=3), candidato(id=6))

    assert ids(recomendar(ENCUENTRO, candidatos, 3)) == [3, 6, 9]


def test_devuelve_los_criterios_y_valores_de_cada_recomendado():
    recomendacion = recomendar(ENCUENTRO, (candidato(nivel=5.0),), 3).recomendados[0]

    assert recomendacion.c_nivel == 0.5
    assert recomendacion.c_geo == 1.0
    assert recomendacion.c_tipo == 1.0
    assert recomendacion.distancia_km == 0.0
    assert recomendacion.puntaje == Decimal("0.7000")
