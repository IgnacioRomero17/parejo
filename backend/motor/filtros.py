from datetime import time

from motor.parametros import PARAMETROS, Parametros
from motor.tipos import CandidatoEntrada, EncuentroEntrada, Franja

MINUTOS_POR_HORA = 60


def _minutos(hora: time) -> int:
    return hora.hour * MINUTOS_POR_HORA + hora.minute


def esta_activo(candidato: CandidatoEntrada) -> bool:
    """Filtro 1: la cuenta del candidato está activa."""
    return candidato.activo


def esta_disponible(candidato: CandidatoEntrada) -> bool:
    """Filtro 2: el candidato está disponible para recibir invitaciones."""
    return candidato.disponible


def tiene_perfil_completo(candidato: CandidatoEntrada) -> bool:
    """Filtro 3: el candidato tiene nivel y localidad (lat y lon)."""
    return candidato.nivel is not None and candidato.lat is not None and candidato.lon is not None


def no_esta_excluido(candidato: CandidatoEntrada, encuentro: EncuentroEntrada) -> bool:
    """Filtro 4: el candidato no es el organizador, ni participante ni invitado del encuentro."""
    return candidato.id not in encuentro.ids_excluidos


def cubre_horario(franja: Franja, encuentro: EncuentroEntrada) -> bool:
    """Indica si una sola franja cubre el encuentro completo.

    Cubre si `dia == fecha.isoweekday()`, `inicio <= hora_inicio` y
    `fin >= hora_inicio + duracion`. Empezar justo a la hora o terminar justo al final cubre.
    """
    inicio_encuentro = _minutos(encuentro.hora_inicio)
    fin_encuentro = inicio_encuentro + encuentro.duracion_minutos
    return (
        franja.dia == encuentro.fecha.isoweekday()
        and _minutos(franja.inicio) <= inicio_encuentro
        and _minutos(franja.fin) >= fin_encuentro
    )


def franja_que_cubre(franjas: tuple[Franja, ...], encuentro: EncuentroEntrada) -> Franja | None:
    """Devuelve la primera franja, en el orden recibido, que cubre el encuentro; si no, None."""
    return next((franja for franja in franjas if cubre_horario(franja, encuentro)), None)


def tiene_disponibilidad(candidato: CandidatoEntrada, encuentro: EncuentroEntrada) -> bool:
    """Filtro 5: alguna franja del candidato cubre el encuentro completo."""
    return franja_que_cubre(candidato.franjas, encuentro) is not None


def dentro_de_distancia(distancia_km: float, p: Parametros = PARAMETROS) -> bool:
    """Filtro 6: `distancia_km <= dist_max_km`."""
    return distancia_km <= p.dist_max_km


def nivel_compatible(dif_nivel: float, p: Parametros = PARAMETROS) -> bool:
    """Filtro 7: `abs(nivel - promedio) <= dif_max_nivel` (recibe ya la diferencia)."""
    return dif_nivel <= p.dif_max_nivel
