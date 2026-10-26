from datetime import date, time

import pytest

from motor import filtros
from motor.parametros import Parametros
from motor.tipos import Franja
from tests.motor.entradas import FRANJA_SABADO, candidato, encuentro


def test_filtro1_activo():
    assert filtros.esta_activo(candidato())
    assert not filtros.esta_activo(candidato(activo=False))


def test_filtro2_disponible():
    assert filtros.esta_disponible(candidato())
    assert not filtros.esta_disponible(candidato(disponible=False))


@pytest.mark.parametrize("campo", ["nivel", "lat", "lon"])
def test_filtro3_perfil_completo(campo):
    assert filtros.tiene_perfil_completo(candidato())
    assert not filtros.tiene_perfil_completo(candidato(**{campo: None}))


def test_filtro4_no_excluido():
    excluidos = encuentro(ids_excluidos=frozenset({1, 2}))

    assert filtros.no_esta_excluido(candidato(id=3), excluidos)
    assert not filtros.no_esta_excluido(candidato(id=2), excluidos)


@pytest.mark.parametrize(
    ("inicio", "fin"),
    [
        (time(17), time(21)),
        (time(18), time(21)),  # empieza justo a la hora del encuentro
        (time(17), time(19, 30)),  # termina justo al final
        (time(18), time(19, 30)),
    ],
)
def test_filtro5_franja_que_cubre_el_encuentro(inicio, fin):
    franja = Franja(dia=6, inicio=inicio, fin=fin)

    assert filtros.tiene_disponibilidad(candidato(franjas=(franja,)), encuentro())


@pytest.mark.parametrize(
    "franja",
    [
        Franja(dia=7, inicio=time(17), fin=time(21)),  # otro día, mismo horario
        Franja(dia=6, inicio=time(18, 30), fin=time(21)),  # empieza tarde
        Franja(dia=6, inicio=time(17), fin=time(19)),  # termina antes
    ],
)
def test_filtro5_franja_que_no_cubre(franja):
    assert not filtros.tiene_disponibilidad(candidato(franjas=(franja,)), encuentro())


def test_filtro5_sin_franjas_no_cubre():
    assert not filtros.tiene_disponibilidad(candidato(franjas=()), encuentro())


def test_filtro5_dos_franjas_que_juntas_cubren_no_alcanzan():
    franjas = (
        Franja(dia=6, inicio=time(17), fin=time(18, 30)),
        Franja(dia=6, inicio=time(18, 30), fin=time(21)),
    )

    assert not filtros.tiene_disponibilidad(candidato(franjas=franjas), encuentro())


def test_filtro5_usa_el_dia_iso_de_la_fecha():
    domingo = encuentro(fecha=date(2026, 10, 4))
    franja_domingo = Franja(dia=7, inicio=time(17), fin=time(21))

    assert filtros.tiene_disponibilidad(candidato(franjas=(franja_domingo,)), domingo)
    assert not filtros.tiene_disponibilidad(candidato(franjas=(FRANJA_SABADO,)), domingo)


def test_franja_que_cubre_devuelve_la_que_cubre():
    otra = Franja(dia=2, inicio=time(9), fin=time(12))

    assert filtros.franja_que_cubre((otra, FRANJA_SABADO), encuentro()) == FRANJA_SABADO
    assert filtros.franja_que_cubre((otra,), encuentro()) is None


@pytest.mark.parametrize(("distancia", "pasa"), [(0.0, True), (40.0, True), (40.0001, False)])
def test_filtro6_distancia(distancia, pasa):
    assert filtros.dentro_de_distancia(distancia) is pasa


def test_filtro6_usa_la_distancia_maxima_de_los_parametros():
    assert not filtros.dentro_de_distancia(25.0, Parametros(dist_max_km=20.0))


@pytest.mark.parametrize(("dif_nivel", "pasa"), [(0.0, True), (1.0, True), (1.5, False)])
def test_filtro7_nivel(dif_nivel, pasa):
    assert filtros.nivel_compatible(dif_nivel) is pasa


def test_filtro7_usa_la_diferencia_maxima_de_los_parametros():
    assert not filtros.nivel_compatible(1.0, Parametros(dif_max_nivel=0.5))
