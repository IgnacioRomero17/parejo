from datetime import time

MENSAJE_HORA_INVALIDA = "Elegí un horario entre las 08:00 y las 23:30, en pasos de 30 minutos."
# Horario en que se juegan los encuentros; las franjas de disponibilidad usan el mismo.
HORA_MINIMA = time(8)
HORA_MAXIMA = time(23, 30)


def hora_valida(hora: time) -> bool:
    """Indica si una hora va en pasos de 30 minutos y entre las 08:00 y las 23:30."""
    return (
        hora.minute in (0, 30)
        and hora.second == 0
        and hora.microsecond == 0
        and HORA_MINIMA <= hora <= HORA_MAXIMA
    )


def minutos(hora: time) -> int:
    """Devuelve los minutos transcurridos desde las 00:00 hasta esa hora."""
    return hora.hour * 60 + hora.minute
