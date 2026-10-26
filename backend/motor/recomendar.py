from statistics import fmean

from motor import filtros
from motor.geo import haversine_km
from motor.parametros import PARAMETROS, Parametros
from motor.puntaje import criterio_geo, criterio_nivel, criterio_tipo, puntaje_recomendacion
from motor.redondeo import redondear4
from motor.tipos import CandidatoEntrada, EncuentroEntrada, Recomendacion, ResultadoRecomendacion


def nivel_promedio(niveles_confirmados: tuple[float, ...]) -> float:
    """Nivel de referencia: la media de los niveles confirmados (float, sin redondear).

    Lanza ValueError si no hay ningún nivel (el organizador siempre está confirmado).
    """
    if not niveles_confirmados:
        raise ValueError("El encuentro necesita al menos un nivel confirmado.")
    return fmean(niveles_confirmados)


def evaluar_candidato(
    candidato: CandidatoEntrada,
    encuentro: EncuentroEntrada,
    promedio: float,
    p: Parametros = PARAMETROS,
) -> Recomendacion | None:
    """Aplica los 7 filtros en orden y, si los pasa, calcula criterios y puntaje.

    Filtros: activo, disponible, perfil completo, no excluido, disponibilidad, distancia
    (`<= dist_max_km`) y nivel (`abs(nivel - promedio) <= dif_max_nivel`).
    puntaje = redondear4(peso_nivel·c_nivel + peso_geo·c_geo + peso_tipo·c_tipo).
    Devuelve la Recomendacion, o None si un filtro lo descarta. No aplica el umbral.
    """
    if not (
        filtros.esta_activo(candidato)
        and filtros.esta_disponible(candidato)
        and filtros.tiene_perfil_completo(candidato)
        and filtros.no_esta_excluido(candidato, encuentro)
        and filtros.tiene_disponibilidad(candidato, encuentro)
    ):
        return None
    distancia_km = haversine_km(encuentro.lat, encuentro.lon, candidato.lat, candidato.lon, p)
    if not filtros.dentro_de_distancia(distancia_km, p):
        return None
    dif_nivel = abs(candidato.nivel - promedio)
    if not filtros.nivel_compatible(dif_nivel, p):
        return None
    c_nivel = criterio_nivel(dif_nivel, p)
    c_geo = criterio_geo(distancia_km, p)
    c_tipo = criterio_tipo(encuentro.tipo, candidato.tipo_preferido, p)
    return Recomendacion(
        id=candidato.id,
        puntaje=puntaje_recomendacion(c_nivel, c_geo, c_tipo, p),
        c_nivel=c_nivel,
        c_geo=c_geo,
        c_tipo=c_tipo,
        distancia_km=distancia_km,
        dif_nivel=dif_nivel,
    )


def _orden(recomendacion: Recomendacion) -> tuple:
    return (
        -recomendacion.puntaje,
        recomendacion.dif_nivel,
        recomendacion.distancia_km,
        recomendacion.id,
    )


def recomendar(
    encuentro: EncuentroEntrada,
    candidatos: tuple[CandidatoEntrada, ...],
    lugares_libres: int,
    p: Parametros = PARAMETROS,
) -> ResultadoRecomendacion:
    """Etapa 1: recomienda candidatos compatibles con el encuentro (HU-007).

    Recibe el encuentro, los candidatos y los lugares libres (de `Encuentro.lugares_libres()`).
    El nivel de referencia es la media de `niveles_confirmados`. Cada candidato pasa los 7
    filtros de `evaluar_candidato` y se recomienda si `puntaje >= umbral_minimo`.
    Orden: puntaje descendente, dif_nivel ascendente, distancia_km ascendente e id ascendente.
    Devuelve todos los recomendados (no se recortan a los lugares libres) y
    `suficientes = len(recomendados) >= lugares_libres`.
    Lanza ValueError si no hay niveles confirmados o si `lugares_libres` es negativo.
    """
    if lugares_libres < 0:
        raise ValueError("Los lugares libres no pueden ser negativos.")
    promedio = nivel_promedio(encuentro.niveles_confirmados)
    # El puntaje es Decimal: comparado con el float 0.55 (0.5500000000000000444…), un puntaje
    # de 0.5500 quedaría abajo del umbral. Se compara contra el umbral redondeado igual.
    umbral = redondear4(p.umbral_minimo)
    evaluados = (evaluar_candidato(candidato, encuentro, promedio, p) for candidato in candidatos)
    recomendados = tuple(
        sorted((r for r in evaluados if r is not None and r.puntaje >= umbral), key=_orden)
    )
    return ResultadoRecomendacion(
        recomendados=recomendados, suficientes=len(recomendados) >= lugares_libres
    )
