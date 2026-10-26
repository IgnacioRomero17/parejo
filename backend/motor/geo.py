from math import atan2, cos, radians, sin, sqrt

from motor.parametros import PARAMETROS, Parametros


def haversine_km(
    lat1: float, lon1: float, lat2: float, lon2: float, p: Parametros = PARAMETROS
) -> float:
    """Distancia en línea recta, en km, entre dos puntos en grados decimales (Haversine).

    a = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)
    d = 2·R·atan2(√a, √(1−a)), con R = p.radio_tierra_km
    El mismo punto da 0.
    """
    lat1_rad, lat2_rad = radians(lat1), radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    return 2 * p.radio_tierra_km * atan2(sqrt(a), sqrt(1 - a))
