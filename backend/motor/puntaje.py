from decimal import Decimal

from motor.parametros import PARAMETROS, Parametros
from motor.redondeo import redondear4
from motor.tipos import INDIFERENTE


def criterio_nivel(dif_nivel: float, p: Parametros = PARAMETROS) -> float:
    """c_nivel = 1 - abs(nivel - promedio) / dif_max_nivel (recibe ya la diferencia)."""
    return 1 - dif_nivel / p.dif_max_nivel


def criterio_geo(distancia_km: float, p: Parametros = PARAMETROS) -> float:
    """c_geo = 1 - distancia_km / dist_max_km."""
    return 1 - distancia_km / p.dist_max_km


def criterio_tipo(
    tipo_encuentro: str, tipo_preferido: str | None, p: Parametros = PARAMETROS
) -> float:
    """c_tipo = 1 si los tipos coinciden o alguno es INDIFERENTE o None; si no,
    valor_tipo_opuesto."""
    if (
        tipo_preferido is None
        or INDIFERENTE in (tipo_encuentro, tipo_preferido)
        or tipo_encuentro == tipo_preferido
    ):
        return 1.0
    return p.valor_tipo_opuesto


def puntaje_recomendacion(
    c_nivel: float, c_geo: float, c_tipo: float, p: Parametros = PARAMETROS
) -> Decimal:
    """puntaje = redondear4(peso_nivel·c_nivel + peso_geo·c_geo + peso_tipo·c_tipo)."""
    return redondear4(p.peso_nivel * c_nivel + p.peso_geo * c_geo + p.peso_tipo * c_tipo)
