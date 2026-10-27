from decimal import Decimal
from statistics import fmean

from motor.parametros import PARAMETROS, Parametros
from motor.redondeo import redondear4
from motor.tipos import DRIVE, REVES, CombinacionResultado, JugadorEntrada

Pareja = tuple[JugadorEntrada, JugadorEntrada]


def equilibrio_nivel(promedio1: float, promedio2: float, p: Parametros = PARAMETROS) -> float:
    """eq_nivel = max(0, 1 - abs(promedio1 - promedio2) / d_max_equilibrio)."""
    return max(0.0, 1 - abs(promedio1 - promedio2) / p.d_max_equilibrio)


def lado_pareja(lado1: str | None, lado2: str | None) -> float:
    """1 si la pareja es DRIVE + REVES o si alguno es INDIFERENTE o None; 0 si repiten lado."""
    if lado1 in (DRIVE, REVES) and lado1 == lado2:
        return 0.0
    return 1.0


def equilibrio_lado(pareja1: Pareja, pareja2: Pareja) -> float:
    """eq_lado = (lado_pareja1 + lado_pareja2) / 2."""
    lado1 = lado_pareja(pareja1[0].lado, pareja1[1].lado)
    lado2 = lado_pareja(pareja2[0].lado, pareja2[1].lado)
    return (lado1 + lado2) / 2


def puntaje_equilibrio(eq_nivel: float, eq_lado: float, p: Parametros = PARAMETROS) -> Decimal:
    """puntaje = redondear4(peso_equilibrio_nivel·eq_nivel + peso_equilibrio_lado·eq_lado)."""
    return redondear4(p.peso_equilibrio_nivel * eq_nivel + p.peso_equilibrio_lado * eq_lado)


def _validar_jugadores(jugadores: tuple[JugadorEntrada, ...], p: Parametros) -> None:
    if len(jugadores) != p.lugares_por_encuentro:
        raise ValueError(f"Se necesitan exactamente {p.lugares_por_encuentro} jugadores.")
    if len({jugador.id for jugador in jugadores}) != len(jugadores):
        raise ValueError("Los jugadores deben tener ids distintos.")
    if any(jugador.nivel is None for jugador in jugadores):
        raise ValueError("Todos los jugadores deben tener nivel.")


def _evaluar(numero: int, pareja1: Pareja, pareja2: Pareja, p: Parametros) -> CombinacionResultado:
    promedio1 = fmean(jugador.nivel for jugador in pareja1)
    promedio2 = fmean(jugador.nivel for jugador in pareja2)
    eq_nivel = equilibrio_nivel(promedio1, promedio2, p)
    eq_lado = equilibrio_lado(pareja1, pareja2)
    return CombinacionResultado(
        numero=numero,
        pareja1=(pareja1[0].id, pareja1[1].id),
        pareja2=(pareja2[0].id, pareja2[1].id),
        promedio1=promedio1,
        promedio2=promedio2,
        eq_nivel=eq_nivel,
        eq_lado=eq_lado,
        puntaje=puntaje_equilibrio(eq_nivel, eq_lado, p),
    )


def evaluar_combinaciones(
    jugadores: tuple[JugadorEntrada, ...], p: Parametros = PARAMETROS
) -> tuple[CombinacionResultado, ...]:
    """Etapa 2: evalúa las 3 combinaciones de 2 parejas con los 4 confirmados (HU-009).

    Ordena los jugadores por id (a < b < c < d) y devuelve, siempre en este orden:
    1. (a, b) vs (c, d) · 2. (a, c) vs (b, d) · 3. (a, d) vs (b, c).
    La pareja que contiene a `a` es la Pareja 1. Por combinación:
    eq_nivel = max(0, 1 - abs(promedio1 - promedio2) / d_max_equilibrio),
    eq_lado = (lado_pareja1 + lado_pareja2) / 2 y
    puntaje = redondear4(peso_equilibrio_nivel·eq_nivel + peso_equilibrio_lado·eq_lado).
    Lanza ValueError si no son exactamente 4 jugadores con ids distintos y nivel no nulo.
    """
    _validar_jugadores(jugadores, p)
    a, b, c, d = sorted(jugadores, key=lambda jugador: jugador.id)
    parejas = (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c)))
    return tuple(
        _evaluar(numero, pareja1, pareja2, p)
        for numero, (pareja1, pareja2) in enumerate(parejas, start=1)
    )


def _orden(combinacion: CombinacionResultado) -> tuple:
    return (
        -combinacion.puntaje,
        abs(combinacion.promedio1 - combinacion.promedio2),
        -combinacion.eq_lado,
        combinacion.numero,
    )


def elegir_mejor(combinaciones: tuple[CombinacionResultado, ...]) -> CombinacionResultado:
    """Elige la combinación con mejor resultado de equilibrio (HU-010).

    Orden: mayor puntaje, menor abs(promedio1 - promedio2), mayor eq_lado y menor número.
    Lanza ValueError si no recibe ninguna combinación.
    """
    if not combinaciones:
        raise ValueError("No hay combinaciones para elegir.")
    return min(combinaciones, key=_orden)
