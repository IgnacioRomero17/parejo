"""Ranking lexicográfico de referencia para comparar con el del motor."""

from motor.tipos import Recomendacion


def ranking_oraculo(filtrados: tuple[Recomendacion, ...]) -> tuple[int, ...]:
    """Ordena los candidatos filtrados por menor diferencia de nivel; a igualdad, menor
    distancia; y al final, menor id. Devuelve los ids en ese orden.
    """
    ordenados = sorted(filtrados, key=lambda r: (r.dif_nivel, r.distancia_km, r.id))
    return tuple(r.id for r in ordenados)


def precision_en_k(
    ranking_motor: tuple[int, ...], ranking_referencia: tuple[int, ...], k: int = 3
) -> float:
    """precision@k = |top k del motor ∩ top k de la referencia| / k.

    Lanza ValueError si alguno de los dos rankings tiene menos de k ids.
    """
    if len(ranking_motor) < k or len(ranking_referencia) < k:
        raise ValueError(f"Los dos rankings necesitan al menos {k} ids.")
    return len(set(ranking_motor[:k]) & set(ranking_referencia[:k])) / k
