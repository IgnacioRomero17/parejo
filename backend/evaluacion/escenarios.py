"""Escenarios dirigidos: casos armados a mano con resultado esperado conocido.

Todos son un sábado a las 18:00, de 90 min, competitivos, con el organizador (id 1, nivel 4,0)
como único confirmado y 3 lugares libres. Los puntajes de los comentarios son con los
parámetros base (pesos 0,60 / 0,30 / 0,10, umbral 0,55, 1 punto y 40 km como máximos).
"""

import math
from dataclasses import dataclass, replace
from datetime import date, time

from evaluacion.localidades import POR_NOMBRE, Localidad
from motor.parametros import PARAMETROS
from motor.tipos import COMPETITIVO, RECREATIVO, CandidatoEntrada, EncuentroEntrada, Franja

SABADO = date(2026, 11, 7)
FRANJA_SABADO = Franja(dia=6, inicio=time(17), fin=time(21))
FRANJA_DOMINGO = Franja(dia=7, inicio=time(17), fin=time(21))
ORGANIZADOR_ID = 1
NIVEL_ORGANIZADOR = 4.0
LUGARES_LIBRES = 3

RIO_CEBALLOS = POR_NOMBRE["Río Ceballos"]
VILLA_CARLOS_PAZ = POR_NOMBRE["Villa Carlos Paz"]


@dataclass(frozen=True)
class EscenarioDirigido:
    """Encuentro con sus candidatos y el resultado que se espera de `recomendar`."""

    nombre: str
    encuentro: EncuentroEntrada
    candidatos: tuple[CandidatoEntrada, ...]
    lugares_libres: int
    ids_esperados: tuple[int, ...]
    suficientes_esperado: bool


def _encuentro(localidad: Localidad) -> EncuentroEntrada:
    return EncuentroEntrada(
        fecha=SABADO,
        hora_inicio=time(18),
        duracion_minutos=90,
        lat=localidad.lat,
        lon=localidad.lon,
        tipo=COMPETITIVO,
        niveles_confirmados=(NIVEL_ORGANIZADOR,),
        ids_excluidos=frozenset({ORGANIZADOR_ID}),
    )


def _candidato(identificador: int, localidad: Localidad, **campos) -> CandidatoEntrada:
    """Candidato compatible por defecto: activo, disponible, nivel 4,0, competitivo y libre
    el sábado de 17 a 21; `campos` cambia lo que haga falta."""
    candidato = CandidatoEntrada(
        id=identificador,
        activo=True,
        disponible=True,
        nivel=NIVEL_ORGANIZADOR,
        lat=localidad.lat,
        lon=localidad.lon,
        tipo_preferido=COMPETITIVO,
        franjas=(FRANJA_SABADO,),
    )
    return replace(candidato, **campos)


def _al_sur(localidad: Localidad, distancia_km: float) -> tuple[float, float]:
    # Sobre el mismo meridiano, Haversine da R·Δlat: el punto queda a esa distancia exacta.
    delta_lat = math.degrees(distancia_km / PARAMETROS.radio_tierra_km)
    return localidad.lat - delta_lat, localidad.lon


def _nadie_compatible() -> EscenarioDirigido:
    jesus_maria = POR_NOMBRE["Jesús María"]
    vcp = VILLA_CARLOS_PAZ
    candidatos = (
        _candidato(1, vcp),  # el organizador: excluido
        _candidato(2, vcp, activo=False),
        _candidato(3, vcp, disponible=False),
        _candidato(4, vcp, lat=None, lon=None),  # perfil incompleto
        _candidato(5, vcp, franjas=(FRANJA_DOMINGO,)),
        _candidato(6, jesus_maria),  # 61,2 km
        _candidato(7, vcp, nivel=6.0),  # 2 puntos de diferencia
        _candidato(8, vcp, nivel=5.0),  # pasa los filtros, pero 0,4000 < 0,55
    )
    return EscenarioDirigido(
        nombre="nadie_compatible",
        encuentro=_encuentro(vcp),
        candidatos=candidatos,
        lugares_libres=LUGARES_LIBRES,
        ids_esperados=(),
        suficientes_esperado=False,
    )


def _justo_lugares_libres() -> EscenarioDirigido:
    candidatos = (
        _candidato(2, RIO_CEBALLOS),  # 1,0000
        _candidato(3, POR_NOMBRE["Unquillo"]),  # 7,4 km: 0,9445
        _candidato(4, POR_NOMBRE["Salsipuedes"], nivel=4.5, tipo_preferido=RECREATIVO),  # 0,5713
        _candidato(5, POR_NOMBRE["La Calera"], nivel=4.5, tipo_preferido=RECREATIVO),  # 0,4516
        _candidato(6, RIO_CEBALLOS, disponible=False),
    )
    return EscenarioDirigido(
        nombre="justo_lugares_libres",
        encuentro=_encuentro(RIO_CEBALLOS),
        candidatos=candidatos,
        lugares_libres=LUGARES_LIBRES,
        ids_esperados=(2, 3, 4),
        suficientes_esperado=True,
    )


def _empates() -> EscenarioDirigido:
    unquillo = POR_NOMBRE["Unquillo"]
    # 3, 4 y 5 son idénticos (0,9445) y 6 y 7 empatan en puntaje, diferencia y distancia
    # (0,7000): todo se resuelve por id. Se pasan desordenados a propósito.
    candidatos = (
        _candidato(5, unquillo),
        _candidato(7, RIO_CEBALLOS, nivel=3.5),
        _candidato(3, unquillo),
        _candidato(6, RIO_CEBALLOS, nivel=4.5),
        _candidato(4, unquillo),
    )
    return EscenarioDirigido(
        nombre="empates",
        encuentro=_encuentro(RIO_CEBALLOS),
        candidatos=candidatos,
        lugares_libres=LUGARES_LIBRES,
        ids_esperados=(3, 4, 5, 6, 7),
        suficientes_esperado=True,
    )


def _mismo_nivel() -> EscenarioDirigido:
    candidatos = (
        _candidato(4, POR_NOMBRE["Unquillo"]),  # 0,9445
        _candidato(3, POR_NOMBRE["Salsipuedes"]),  # 0,9713
        _candidato(2, RIO_CEBALLOS),  # 1,0000
    )
    return EscenarioDirigido(
        nombre="mismo_nivel",
        encuentro=_encuentro(RIO_CEBALLOS),
        candidatos=candidatos,
        lugares_libres=LUGARES_LIBRES,
        ids_esperados=(2, 3, 4),
        suficientes_esperado=True,
    )


def _limites() -> EscenarioDirigido:
    lat_adentro, lon_adentro = _al_sur(RIO_CEBALLOS, 39.9)
    lat_afuera, lon_afuera = _al_sur(RIO_CEBALLOS, 40.1)
    candidatos = (
        _candidato(2, RIO_CEBALLOS, nivel=5.0),  # diferencia 1,0: pasa con c_nivel 0 (0,4000)
        _candidato(3, RIO_CEBALLOS, nivel=5.5),  # diferencia 1,5: filtrado
        _candidato(4, RIO_CEBALLOS, lat=lat_adentro, lon=lon_adentro),  # 39,9 km: 0,7008
        _candidato(5, RIO_CEBALLOS, lat=lat_afuera, lon=lon_afuera),  # 40,1 km: filtrado
        _candidato(6, RIO_CEBALLOS, nivel=3.0),  # diferencia 1,0 hacia abajo (0,4000)
    )
    return EscenarioDirigido(
        nombre="limites",
        encuentro=_encuentro(RIO_CEBALLOS),
        candidatos=candidatos,
        lugares_libres=LUGARES_LIBRES,
        ids_esperados=(4,),
        suficientes_esperado=False,
    )


ESCENARIOS_DIRIGIDOS = (
    _nadie_compatible(),
    _justo_lugares_libres(),
    _empates(),
    _mismo_nivel(),
    _limites(),
)
