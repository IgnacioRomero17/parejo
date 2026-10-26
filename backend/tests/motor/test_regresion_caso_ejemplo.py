"""Regresión con el caso de ejemplo de la regla del motor (coordenadas propias, no del fixture).

Encuentro: sábado 3/10/2026, 18:00, 90 min, Río Ceballos, COMPETITIVO. Confirmado: Tomás
(id 1, nivel 4,5). Todos los candidatos activos, disponibles y con franja de sábado que cubre
18:00–19:30.
"""

from datetime import date, time
from decimal import Decimal

from motor.recomendar import recomendar
from motor.tipos import (
    COMPETITIVO,
    INDIFERENTE,
    RECREATIVO,
    CandidatoEntrada,
    EncuentroEntrada,
    Franja,
)

RIO_CEBALLOS = (-31.1653, -64.3253)
SABADO_18_A_1930 = (Franja(dia=6, inicio=time(18), fin=time(19, 30)),)

ENCUENTRO = EncuentroEntrada(
    fecha=date(2026, 10, 3),
    hora_inicio=time(18),
    duracion_minutos=90,
    lat=RIO_CEBALLOS[0],
    lon=RIO_CEBALLOS[1],
    tipo=COMPETITIVO,
    niveles_confirmados=(4.5,),
    ids_excluidos=frozenset({1}),
)

# id, nivel, (lat, lon), tipo preferido
JUGADORES = (
    (2, 4.5, (-31.1653, -64.3253), COMPETITIVO),  # Valentina · Río Ceballos
    (3, 4.5, (-31.2306, -64.3175), COMPETITIVO),  # Joaquín · Unquillo
    (4, 5.0, (-31.2606, -64.2961), COMPETITIVO),  # Camila · Mendiolaza
    (5, 5.0, (-31.2933, -64.2956), INDIFERENTE),  # Federico · Villa Allende
    (6, 4.0, (-31.1478, -64.2958), RECREATIVO),  # Bruno · Salsipuedes
    (7, 5.0, (-31.3400, -64.3350), COMPETITIVO),  # Agustina · La Calera
)

CANDIDATOS = tuple(
    CandidatoEntrada(
        id=identificador,
        activo=True,
        disponible=True,
        nivel=nivel,
        lat=lat,
        lon=lon,
        tipo_preferido=tipo,
        franjas=SABADO_18_A_1930,
    )
    for identificador, nivel, (lat, lon), tipo in JUGADORES
)

ESPERADO = [
    (2, 0.000, Decimal("1.0000")),
    (3, 7.299, Decimal("0.9453")),
    (4, 10.955, Decimal("0.6178")),
    (5, 14.510, Decimal("0.5912")),
    (6, 3.416, Decimal("0.5744")),
    (7, 19.448, Decimal("0.5541")),
]


def test_regresion_caso_ejemplo_orden_distancias_y_puntajes():
    # Se pasan en orden inverso para que el orden lo decida el motor.
    resultado = recomendar(ENCUENTRO, CANDIDATOS[::-1], lugares_libres=3)

    obtenido = [(r.id, round(r.distancia_km, 3), r.puntaje) for r in resultado.recomendados]
    assert obtenido == ESPERADO
    assert resultado.suficientes
