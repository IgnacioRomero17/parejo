"""Entradas del motor con valores por defecto válidos, para los tests sin base de datos."""

from dataclasses import replace
from datetime import date, time

from motor.tipos import COMPETITIVO, CandidatoEntrada, EncuentroEntrada, Franja

RIO_CEBALLOS = (-31.1653, -64.3253)
SABADO = date(2026, 10, 3)
FRANJA_SABADO = Franja(dia=6, inicio=time(17), fin=time(21))

ENCUENTRO = EncuentroEntrada(
    fecha=SABADO,
    hora_inicio=time(18),
    duracion_minutos=90,
    lat=RIO_CEBALLOS[0],
    lon=RIO_CEBALLOS[1],
    tipo=COMPETITIVO,
    niveles_confirmados=(4.5,),
    ids_excluidos=frozenset({1}),
)

CANDIDATO = CandidatoEntrada(
    id=2,
    activo=True,
    disponible=True,
    nivel=4.5,
    lat=RIO_CEBALLOS[0],
    lon=RIO_CEBALLOS[1],
    tipo_preferido=COMPETITIVO,
    franjas=(FRANJA_SABADO,),
)


def encuentro(**campos) -> EncuentroEntrada:
    return replace(ENCUENTRO, **campos)


def candidato(**campos) -> CandidatoEntrada:
    return replace(CANDIDATO, **campos)
