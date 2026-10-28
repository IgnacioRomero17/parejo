"""Corre los experimentos de evaluación del motor y escribe un CSV por experimento.

Uso, desde `backend/`: `python -m evaluacion.experimentos`.
"""

import csv
import logging
from dataclasses import fields, replace
from pathlib import Path
from statistics import fmean

from evaluacion.escenarios import ESCENARIOS_DIRIGIDOS, EscenarioDirigido
from evaluacion.generador import SEMILLA, EscenarioAleatorio, generar_escenarios, generar_jugadores
from evaluacion.oraculo import precision_en_k, ranking_oraculo
from motor.parametros import PARAMETROS, Parametros
from motor.recomendar import recomendar
from motor.tipos import CandidatoEntrada, EncuentroEntrada

logger = logging.getLogger(__name__)

DIRECTORIO_RESULTADOS = Path(__file__).resolve().parent / "resultados"
K = 3
PROPIEDADES = (
    "ningun_excluido_recomendado",
    "orden_descendente",
    "puntajes_entre_0_y_1",
    "resultado_identico_al_repetir",
)

Fila = dict[str, str]


def formatear_parametros(p: Parametros) -> str:
    """Texto `campo=valor; …` con todos los campos de `p`, para guardar junto a los resultados."""
    return "; ".join(f"{campo.name}={getattr(p, campo.name)}" for campo in fields(p))


def _numero(valor: float) -> str:
    return f"{valor:.4f}"


def _porcentaje(parte: int, total: int) -> str:
    return _numero(100 * parte / total)


def _metadatos(semilla: int, p: Parametros) -> Fila:
    return {"semilla": str(semilla), "parametros": formatear_parametros(p)}


def _metricas(valores: dict[str, str], semilla: int, p: Parametros) -> list[Fila]:
    metadatos = _metadatos(semilla, p)
    return [{"metrica": nombre, "valor": valor, **metadatos} for nombre, valor in valores.items()]


def escribir_csv(directorio: Path, nombre: str, filas: list[Fila]) -> Path:
    """Escribe `filas` en `directorio/nombre` (UTF-8, fin de línea `\\n`) y devuelve la ruta.

    Las columnas son las claves de la primera fila. Crea el directorio si no existe.
    """
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / nombre
    # Fin de línea fijo para que el archivo sea idéntico en Windows y en Linux.
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta


def propiedades_de(
    encuentro: EncuentroEntrada,
    candidatos: tuple[CandidatoEntrada, ...],
    lugares_libres: int,
    p: Parametros = PARAMETROS,
) -> dict[str, bool]:
    """Verifica en un escenario las propiedades de la etapa 1.

    Ningún excluido recomendado, puntajes en orden descendente y entre 0 y 1, y el mismo
    resultado al repetir la llamada. Devuelve un booleano por propiedad de PROPIEDADES.
    """
    resultado = recomendar(encuentro, candidatos, lugares_libres, p)
    ids = {r.id for r in resultado.recomendados}
    puntajes = [r.puntaje for r in resultado.recomendados]
    return {
        "ningun_excluido_recomendado": not ids & encuentro.ids_excluidos,
        "orden_descendente": puntajes == sorted(puntajes, reverse=True),
        "puntajes_entre_0_y_1": all(0 <= puntaje <= 1 for puntaje in puntajes),
        "resultado_identico_al_repetir": (
            recomendar(encuentro, candidatos, lugares_libres, p) == resultado
        ),
    }


def cumple_lo_esperado(escenario: EscenarioDirigido, p: Parametros = PARAMETROS) -> bool:
    """Indica si `recomendar` da exactamente los ids (en orden) y el `suficientes` esperados."""
    resultado = recomendar(escenario.encuentro, escenario.candidatos, escenario.lugares_libres, p)
    ids = tuple(r.id for r in resultado.recomendados)
    return (
        ids == escenario.ids_esperados and resultado.suficientes == escenario.suficientes_esperado
    )


def experimento_propiedades(
    aleatorios: tuple[EscenarioAleatorio, ...],
    candidatos: tuple[CandidatoEntrada, ...],
    dirigidos: tuple[EscenarioDirigido, ...],
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
) -> list[Fila]:
    """Experimento 1: cuántos escenarios (aleatorios y dirigidos) cumplen cada propiedad, más
    cuántos dirigidos dan el resultado esperado. Debe dar 100 % en todo.

    Devuelve una fila por propiedad: propiedad, escenarios, cumplen, porcentaje, semilla y
    parámetros.
    """
    verificados = [
        propiedades_de(escenario.encuentro, candidatos, escenario.lugares_libres, p)
        for escenario in aleatorios
    ] + [
        propiedades_de(escenario.encuentro, escenario.candidatos, escenario.lugares_libres, p)
        for escenario in dirigidos
    ]
    conteos = [
        (propiedad, sum(v[propiedad] for v in verificados), len(verificados))
        for propiedad in PROPIEDADES
    ]
    esperados = sum(cumple_lo_esperado(escenario, p) for escenario in dirigidos)
    conteos.append(("resultado_esperado_dirigidos", esperados, len(dirigidos)))
    metadatos = _metadatos(semilla, p)
    return [
        {
            "propiedad": propiedad,
            "escenarios": str(total),
            "cumplen": str(cumplen),
            "porcentaje": _porcentaje(cumplen, total),
            **metadatos,
        }
        for propiedad, cumplen, total in conteos
    ]


def experimento_oraculo(
    aleatorios: tuple[EscenarioAleatorio, ...],
    candidatos: tuple[CandidatoEntrada, ...],
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
) -> list[Fila]:
    """Experimento 2: precision@3 entre el ranking del motor y el del oráculo lexicográfico.

    Con `umbral_minimo = 0` el motor devuelve, en su orden, todos los candidatos que pasan los
    7 filtros; el oráculo ordena ese mismo conjunto. Solo cuentan los escenarios con al menos
    3 filtrados. Es un chequeo de consistencia, no una validación de calidad.
    Devuelve filas metrica, valor, semilla y parámetros (los de umbral 0).
    """
    sin_umbral = replace(p, umbral_minimo=0.0)
    precisiones = []
    for escenario in aleatorios:
        filtrados = recomendar(
            escenario.encuentro, candidatos, escenario.lugares_libres, sin_umbral
        ).recomendados
        if len(filtrados) >= K:
            ranking_motor = tuple(r.id for r in filtrados)
            precisiones.append(precision_en_k(ranking_motor, ranking_oraculo(filtrados), K))
    aciertos = [round(precision * K) for precision in precisiones]
    valores = {
        "escenarios": str(len(aleatorios)),
        "escenarios_con_3_filtrados": str(len(precisiones)),
        "precision_at_3_media": _numero(fmean(precisiones)),
        "precision_at_3_minima": _numero(min(precisiones)),
    }
    for coincidencias in range(K + 1):
        valores[f"escenarios_con_{coincidencias}_de_3"] = str(aciertos.count(coincidencias))
    return _metricas(valores, semilla, sin_umbral)


def experimento_cobertura(
    aleatorios: tuple[EscenarioAleatorio, ...],
    candidatos: tuple[CandidatoEntrada, ...],
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
) -> list[Fila]:
    """Experimento 3: % de escenarios con candidatos suficientes, cantidad media de
    recomendados por escenario y puntaje medio de todos los recomendados.

    Devuelve filas metrica, valor, semilla y parámetros.
    """
    resultados = [
        recomendar(escenario.encuentro, candidatos, escenario.lugares_libres, p)
        for escenario in aleatorios
    ]
    puntajes = [float(r.puntaje) for resultado in resultados for r in resultado.recomendados]
    valores = {
        "escenarios": str(len(resultados)),
        "porcentaje_suficientes": _porcentaje(
            sum(resultado.suficientes for resultado in resultados), len(resultados)
        ),
        "recomendados_media": _numero(fmean(len(r.recomendados) for r in resultados)),
        "puntaje_medio": _numero(fmean(puntajes)),
        "escenarios_sin_recomendados": str(sum(not r.recomendados for r in resultados)),
    }
    return _metricas(valores, semilla, p)


def main() -> None:
    """Genera los datos con SEMILLA y escribe los CSV de los experimentos 1 a 3."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    jugadores = generar_jugadores()
    candidatos = tuple(jugador.candidato for jugador in jugadores)
    aleatorios = generar_escenarios(jugadores)
    archivos = {
        "01_propiedades.csv": experimento_propiedades(aleatorios, candidatos, ESCENARIOS_DIRIGIDOS),
        "02_oraculo.csv": experimento_oraculo(aleatorios, candidatos),
        "03_cobertura.csv": experimento_cobertura(aleatorios, candidatos),
    }
    for nombre, filas in archivos.items():
        ruta = escribir_csv(DIRECTORIO_RESULTADOS, nombre, filas)
        logger.info("Escrito %s", ruta.name)


if __name__ == "__main__":
    main()
