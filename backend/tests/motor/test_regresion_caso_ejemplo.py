"""Regresión con el caso de ejemplo de la regla del motor (coordenadas propias, no del fixture).

Encuentro: sábado 3/10/2026, 18:00, 90 min, Río Ceballos, COMPETITIVO. Confirmado: Tomás
(id 1, nivel 4,5). Todos los candidatos activos, disponibles y con franja de sábado que cubre
18:00–19:30.
"""

from datetime import date, time
from decimal import Decimal

from motor.equilibrio import elegir_mejor, evaluar_combinaciones
from motor.recomendar import recomendar
from motor.tipos import (
    COMPETITIVO,
    DRIVE,
    INDIFERENTE,
    RECREATIVO,
    REVES,
    CandidatoEntrada,
    EncuentroEntrada,
    Franja,
    JugadorEntrada,
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


# Etapa 2 con Tomás (1), Valentina (2), Camila (4) y Federico (5).
CONFIRMADOS = (
    JugadorEntrada(id=5, nivel=5.0, lado=DRIVE),  # Federico
    JugadorEntrada(id=2, nivel=4.5, lado=REVES),  # Valentina
    JugadorEntrada(id=4, nivel=5.0, lado=REVES),  # Camila
    JugadorEntrada(id=1, nivel=4.5, lado=DRIVE),  # Tomás
)

# numero, pareja 1, pareja 2, promedios, puntaje
ESPERADO_ETAPA2 = [
    (1, (1, 2), (4, 5), (4.50, 5.00), Decimal("0.8000")),
    (2, (1, 4), (2, 5), (4.75, 4.75), Decimal("1.0000")),
    (3, (1, 5), (2, 4), (4.75, 4.75), Decimal("0.8000")),  # ambas parejas repiten lado
]


def test_regresion_caso_ejemplo_etapa2_elige_la_combinacion_2():
    # Desordenados para que el orden de las combinaciones lo decida el motor.
    combinaciones = evaluar_combinaciones(CONFIRMADOS)

    obtenido = [
        (c.numero, c.pareja1, c.pareja2, (c.promedio1, c.promedio2), c.puntaje)
        for c in combinaciones
    ]
    assert obtenido == ESPERADO_ETAPA2
    elegida = elegir_mejor(combinaciones)
    assert (elegida.numero, elegida.puntaje) == (2, Decimal("1.0000"))
    # Tomás + Camila vs Valentina + Federico.
    assert (elegida.pareja1, elegida.pareja2) == ((1, 4), (2, 5))
