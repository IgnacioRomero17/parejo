"""Métodos alternativos de armar parejas, para comparar con la etapa 2 del motor.

Cada línea base elige una de las 3 combinaciones que devuelve `evaluar_combinaciones`, así
su puntaje y sus promedios se calculan con las mismas fórmulas que la propuesta del motor.
"""

import random

from motor.tipos import CombinacionResultado, JugadorEntrada


def aleatoria(
    combinaciones: tuple[CombinacionResultado, ...], generador: random.Random
) -> CombinacionResultado:
    """Elige una combinación al azar con `generador` (un `random.Random` con semilla)."""
    return generador.choice(combinaciones)


def orden_de_llegada(combinaciones: tuple[CombinacionResultado, ...]) -> CombinacionResultado:
    """Elige la combinación 1, (a, b) vs (c, d) por id: las parejas en el orden de llegada.

    Lanza ValueError si no está la combinación 1.
    """
    for combinacion in combinaciones:
        if combinacion.numero == 1:
            return combinacion
    raise ValueError("Falta la combinación 1.")


def mas_fuertes_juntos(
    jugadores: tuple[JugadorEntrada, ...], combinaciones: tuple[CombinacionResultado, ...]
) -> CombinacionResultado:
    """Elige la combinación en la que los 2 jugadores de mayor nivel forman pareja.

    Los 2 más fuertes salen de ordenar por nivel descendente y, a igualdad, por id
    ascendente. Lanza ValueError si ninguna combinación los pone juntos.
    """
    fuertes = sorted(jugadores, key=lambda jugador: (-jugador.nivel, jugador.id))[:2]
    pareja = tuple(sorted(jugador.id for jugador in fuertes))
    for combinacion in combinaciones:
        if pareja in (combinacion.pareja1, combinacion.pareja2):
            return combinacion
    raise ValueError("Ninguna combinación pone juntos a los 2 más fuertes.")
