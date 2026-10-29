"""Corre los experimentos de evaluación del motor y escribe un CSV por experimento y un resumen.

Uso, desde `backend/`: `python -m evaluacion.experimentos`.
"""

import csv
import logging
import platform
import random
import time
from collections.abc import Callable
from dataclasses import fields, replace
from decimal import Decimal
from functools import partial
from pathlib import Path
from statistics import fmean, median

from evaluacion import lineas_base
from evaluacion.escenarios import ESCENARIOS_DIRIGIDOS, EscenarioDirigido
from evaluacion.generador import (
    SEMILLA,
    EscenarioAleatorio,
    Grupo,
    generar_escenarios,
    generar_grupos_aleatorios,
    generar_jugadores,
    grupos_de_recomendados,
)
from evaluacion.oraculo import precision_en_k, ranking_oraculo
from motor import filtros
from motor.equilibrio import elegir_mejor, evaluar_combinaciones
from motor.geo import haversine_km
from motor.parametros import PARAMETROS, Parametros
from motor.recomendar import nivel_promedio, recomendar
from motor.tipos import (
    CandidatoEntrada,
    CombinacionResultado,
    EncuentroEntrada,
    ResultadoRecomendacion,
)

logger = logging.getLogger(__name__)

DIRECTORIO_RESULTADOS = Path(__file__).resolve().parent / "resultados"
K = 3
PROPIEDADES = (
    "ningun_excluido_recomendado",
    "orden_descendente",
    "puntajes_entre_0_y_1",
    "resultado_identico_al_repetir",
)
# Las 7 etapas del medio son los filtros, en el orden en que los aplica el motor.
ETAPAS_EMBUDO = (
    "inicial",
    "activo",
    "disponible",
    "perfil_completo",
    "no_excluido",
    "disponibilidad",
    "distancia",
    "nivel",
    "umbral",
)
POBLACIONES = (200, 500, 1000)
METODOS = ("motor", "aleatoria", "orden_llegada", "mas_fuertes_juntos")
# Como máximo medio nivel de diferencia entre parejas con lados complementarios.
PUNTAJE_REFERENCIA = Decimal("0.80")
PESOS_ETAPA1 = ("peso_nivel", "peso_geo", "peso_tipo")
VARIACION_PESO = 0.10
VALORES_SENSIBILIDAD = {
    "umbral_minimo": (0.50, 0.55, 0.60),
    "dif_max_nivel": (0.5, 1.0, 1.5),
    "dist_max_km": (20.0, 40.0),
}
TAMANIOS_RENDIMIENTO = (100, 200, 1000, 5000)
REPETICIONES = 20
MILISEGUNDOS_POR_SEGUNDO = 1000

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


def _recomendar_todos(
    aleatorios: tuple[EscenarioAleatorio, ...],
    candidatos: tuple[CandidatoEntrada, ...],
    p: Parametros,
) -> list[ResultadoRecomendacion]:
    return [
        recomendar(escenario.encuentro, candidatos, escenario.lugares_libres, p)
        for escenario in aleatorios
    ]


def _valores_cobertura(
    aleatorios: tuple[EscenarioAleatorio, ...],
    candidatos: tuple[CandidatoEntrada, ...],
    p: Parametros,
) -> dict[str, str]:
    resultados = _recomendar_todos(aleatorios, candidatos, p)
    puntajes = [float(r.puntaje) for resultado in resultados for r in resultado.recomendados]
    return {
        "escenarios": str(len(resultados)),
        "porcentaje_suficientes": _porcentaje(
            sum(resultado.suficientes for resultado in resultados), len(resultados)
        ),
        "recomendados_media": _numero(fmean(len(r.recomendados) for r in resultados)),
        "puntaje_medio": _numero(fmean(puntajes)),
        "escenarios_sin_recomendados": str(sum(not r.recomendados for r in resultados)),
    }


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
    return _metricas(_valores_cobertura(aleatorios, candidatos, p), semilla, p)


def _filtros_superados(
    candidato: CandidatoEntrada, encuentro: EncuentroEntrada, promedio: float, p: Parametros
) -> int:
    # Funciones sin evaluar: la distancia y el nivel solo se calculan si el perfil está completo.
    filtros_en_orden = (
        lambda: filtros.esta_activo(candidato),
        lambda: filtros.esta_disponible(candidato),
        lambda: filtros.tiene_perfil_completo(candidato),
        lambda: filtros.no_esta_excluido(candidato, encuentro),
        lambda: filtros.tiene_disponibilidad(candidato, encuentro),
        lambda: filtros.dentro_de_distancia(
            haversine_km(encuentro.lat, encuentro.lon, candidato.lat, candidato.lon, p), p
        ),
        lambda: filtros.nivel_compatible(abs(candidato.nivel - promedio), p),
    )
    for superados, filtro in enumerate(filtros_en_orden):
        if not filtro():
            return superados
    return len(filtros_en_orden)


def embudo(
    encuentro: EncuentroEntrada,
    candidatos: tuple[CandidatoEntrada, ...],
    lugares_libres: int,
    p: Parametros = PARAMETROS,
) -> tuple[int, ...]:
    """Cuenta los candidatos que quedan en cada etapa de ETAPAS_EMBUDO.

    Primero cuenta todos los candidatos. Después aplica los 7 filtros de `motor.filtros` en
    el orden del motor, uno detrás del otro, y al final cuenta los que `recomendar` deja
    arriba del umbral. Devuelve un conteo por etapa.
    """
    promedio = nivel_promedio(encuentro.niveles_confirmados)
    superados = [_filtros_superados(candidato, encuentro, promedio, p) for candidato in candidatos]
    cantidad_filtros = len(ETAPAS_EMBUDO) - 2
    restantes = [
        sum(cantidad >= filtro for cantidad in superados) for filtro in range(cantidad_filtros + 1)
    ]
    restantes.append(len(recomendar(encuentro, candidatos, lugares_libres, p).recomendados))
    return tuple(restantes)


def experimento_embudo(
    aleatorios: tuple[EscenarioAleatorio, ...],
    candidatos: tuple[CandidatoEntrada, ...],
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
) -> list[Fila]:
    """Experimento 3b: cantidad media de candidatos por escenario que quedan en cada etapa
    del embudo (todos, después de cada filtro en el orden del motor y después del umbral).

    Devuelve una fila por etapa: paso, etapa, restantes_media, descartados_media (contra la
    etapa anterior), semilla y parámetros.
    """
    conteos = [
        embudo(escenario.encuentro, candidatos, escenario.lugares_libres, p)
        for escenario in aleatorios
    ]
    medias = [fmean(conteo[paso] for conteo in conteos) for paso in range(len(ETAPAS_EMBUDO))]
    metadatos = _metadatos(semilla, p)
    return [
        {
            "paso": str(paso),
            "etapa": etapa,
            "restantes_media": _numero(media),
            "descartados_media": _numero(medias[paso - 1] - media if paso else 0.0),
            **metadatos,
        }
        for paso, (etapa, media) in enumerate(zip(ETAPAS_EMBUDO, medias, strict=True))
    ]


def experimento_poblacion(
    aleatorios: tuple[EscenarioAleatorio, ...],
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
    poblaciones: tuple[int, ...] = POBLACIONES,
) -> list[Fila]:
    """Experimento 3c: el experimento 3 con 200, 500 y 1000 jugadores.

    Los escenarios son siempre `aleatorios` (los de la población base). Lo único que cambia
    es cuántos jugadores se generan con la misma semilla, y los primeros 200 son siempre
    los mismos. Devuelve una fila por población: jugadores, las métricas del experimento 3,
    semilla y parámetros.
    """
    metadatos = _metadatos(semilla, p)
    filas = []
    for cantidad in poblaciones:
        candidatos = tuple(jugador.candidato for jugador in generar_jugadores(semilla, cantidad))
        valores = _valores_cobertura(aleatorios, candidatos, p)
        filas.append({"jugadores": str(cantidad), **valores, **metadatos})
    return filas


def _diferencia(combinacion: CombinacionResultado) -> float:
    return abs(combinacion.promedio1 - combinacion.promedio2)


def _elegidas(
    grupo: Grupo, generador: random.Random, p: Parametros
) -> tuple[dict[str, CombinacionResultado], float]:
    """Combinación elegida por cada método de METODOS y la menor diferencia de promedios."""
    combinaciones = evaluar_combinaciones(grupo, p)
    elegidas = {
        "motor": elegir_mejor(combinaciones),
        "aleatoria": lineas_base.aleatoria(combinaciones, generador),
        "orden_llegada": lineas_base.orden_de_llegada(combinaciones),
        "mas_fuertes_juntos": lineas_base.mas_fuertes_juntos(grupo, combinaciones),
    }
    return elegidas, min(_diferencia(combinacion) for combinacion in combinaciones)


def _fila_equilibrio(elegidas: list[CombinacionResultado], optimos: list[float]) -> dict[str, str]:
    diferencias = [_diferencia(combinacion) for combinacion in elegidas]
    coinciden = sum(d == optimo for d, optimo in zip(diferencias, optimos, strict=True))
    altos = sum(combinacion.puntaje >= PUNTAJE_REFERENCIA for combinacion in elegidas)
    return {
        "cantidad_grupos": str(len(elegidas)),
        "diferencia_media": _numero(fmean(diferencias)),
        "puntaje_medio": _numero(fmean(float(combinacion.puntaje) for combinacion in elegidas)),
        "porcentaje_puntaje_0_80": _porcentaje(altos, len(elegidas)),
        "coincide_optimo_nivel": str(coinciden),
        "porcentaje_optimo_nivel": _porcentaje(coinciden, len(elegidas)),
    }


def experimento_equilibrio(
    recomendados: tuple[Grupo, ...],
    aleatorios: tuple[Grupo, ...],
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
) -> list[Fila]:
    """Experimento 4: compara la propuesta del motor con las 3 líneas base en cada grupo.

    Para cada fuente (grupos de recomendados, grupos al azar y todos) y cada método informa
    la diferencia media de promedios entre parejas, el puntaje de equilibrio medio, el % de
    grupos con puntaje >= 0,80 y cuántas veces coincide con el óptimo por nivel (la menor
    diferencia de promedios de las 3 combinaciones). La línea base aleatoria usa un
    `random.Random(semilla)` para todos los grupos.
    """
    generador = random.Random(semilla)
    por_fuente = {
        "recomendados": [_elegidas(grupo, generador, p) for grupo in recomendados],
        "aleatorios": [_elegidas(grupo, generador, p) for grupo in aleatorios],
    }
    por_fuente["todos"] = por_fuente["recomendados"] + por_fuente["aleatorios"]
    metadatos = _metadatos(semilla, p)
    filas = []
    for fuente, evaluados in por_fuente.items():
        optimos = [optimo for _, optimo in evaluados]
        for metodo in METODOS:
            elegidas = [por_metodo[metodo] for por_metodo, _ in evaluados]
            valores = _fila_equilibrio(elegidas, optimos)
            filas.append({"grupos": fuente, "metodo": metodo, **valores, **metadatos})
    return filas


def _variar_peso(p: Parametros, campo: str, variacion: float) -> Parametros:
    # El peso variado queda fijo y los otros dos se reescalan para que la suma siga en 1.
    nuevo = round(getattr(p, campo) + variacion, 2)
    otros = [peso for peso in PESOS_ETAPA1 if peso != campo]
    escala = (1 - nuevo) / sum(getattr(p, peso) for peso in otros)
    return replace(p, **{campo: nuevo}, **{peso: getattr(p, peso) * escala for peso in otros})


def configuraciones_sensibilidad(
    p: Parametros = PARAMETROS,
) -> tuple[tuple[str, Parametros], ...]:
    """Configuraciones del experimento 5: la base y una variante por valor, cambiando de a un
    parámetro.

    Cada peso de la etapa 1 se mueve ±0,10 y los otros dos se reescalan para que sumen 1. El
    umbral, `dif_max_nivel` y `dist_max_km` toman los valores de VALORES_SENSIBILIDAD que no
    son el de `p`. Devuelve pares (nombre, parámetros), con la base primero.
    """
    configuraciones = [("base", p)]
    for campo in PESOS_ETAPA1:
        for variacion in (VARIACION_PESO, -VARIACION_PESO):
            nombre = f"{campo}{variacion:+.2f}"
            configuraciones.append((nombre, _variar_peso(p, campo, variacion)))
    for campo, valores in VALORES_SENSIBILIDAD.items():
        for valor in valores:
            if valor != getattr(p, campo):
                configuraciones.append((f"{campo}={valor}", replace(p, **{campo: valor})))
    return tuple(configuraciones)


def _comparar_con_base(
    resultados: list[ResultadoRecomendacion], base: list[ResultadoRecomendacion]
) -> dict[str, str]:
    rankings = [tuple(r.id for r in resultado.recomendados) for resultado in resultados]
    rankings_base = [tuple(r.id for r in resultado.recomendados) for resultado in base]
    pares = list(zip(rankings, rankings_base, strict=True))
    precisiones = [
        precision_en_k(ranking, ranking_base, K)
        for ranking, ranking_base in pares
        if len(ranking) >= K and len(ranking_base) >= K
    ]
    identicos = sum(ranking[:K] == ranking_base[:K] for ranking, ranking_base in pares)
    return {
        "escenarios_con_3_en_ambas": str(len(precisiones)),
        "precision_at_3_media": _numero(fmean(precisiones)) if precisiones else "",
        "porcentaje_top3_identico": _porcentaje(identicos, len(pares)),
    }


def experimento_sensibilidad(
    aleatorios: tuple[EscenarioAleatorio, ...],
    candidatos: tuple[CandidatoEntrada, ...],
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
) -> list[Fila]:
    """Experimento 5: cómo cambia la etapa 1 al variar de a un parámetro.

    Por configuración informa el % de escenarios suficientes y su cambio en puntos contra la
    base. También informa la coincidencia del top 3 con la base de dos formas: precision@3
    media en los escenarios con al menos 3 recomendados en ambas, y % de escenarios con el
    mismo top 3 en el mismo orden (aunque tenga menos de 3). Cada fila lleva los parámetros
    de su configuración.
    """
    base = _recomendar_todos(aleatorios, candidatos, p)
    porcentaje_base = 100 * fmean(resultado.suficientes for resultado in base)
    filas = []
    for nombre, parametros in configuraciones_sensibilidad(p):
        resultados = _recomendar_todos(aleatorios, candidatos, parametros)
        porcentaje = 100 * fmean(resultado.suficientes for resultado in resultados)
        filas.append(
            {
                "configuracion": nombre,
                "porcentaje_suficientes": _numero(porcentaje),
                "cambio_puntos": _numero(porcentaje - porcentaje_base),
                **_comparar_con_base(resultados, base),
                **_metadatos(semilla, parametros),
            }
        )
    return filas


def _mediana_ms(funcion: Callable[[], object], repeticiones: int) -> float:
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        funcion()
        tiempos.append(time.perf_counter() - inicio)
    return median(tiempos) * MILISEGUNDOS_POR_SEGUNDO


def experimento_rendimiento(
    escenario: EscenarioAleatorio,
    grupo: Grupo,
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
    tamanios: tuple[int, ...] = TAMANIOS_RENDIMIENTO,
    repeticiones: int = REPETICIONES,
) -> list[Fila]:
    """Experimento 6: mediana del tiempo de `recomendar` y de la etapa 2, con `perf_counter`.

    `recomendar` se mide sobre `escenario` con cada cantidad de jugadores de `tamanios`,
    generados con la semilla. La etapa 2 (`evaluar_combinaciones` y `elegir_mejor`) se mide
    sobre `grupo`. Es el único experimento que cambia entre corridas: los tiempos dependen
    de la máquina, que se informa en las columnas python y sistema.
    """
    pruebas = []
    for cantidad in tamanios:
        candidatos = tuple(jugador.candidato for jugador in generar_jugadores(semilla, cantidad))
        llamada = partial(recomendar, escenario.encuentro, candidatos, escenario.lugares_libres, p)
        pruebas.append(("recomendar", cantidad, llamada))
    pruebas.append(("etapa_2", len(grupo), lambda: elegir_mejor(evaluar_combinaciones(grupo, p))))
    entorno = {"python": platform.python_version(), "sistema": platform.platform()}
    metadatos = _metadatos(semilla, p)
    return [
        {
            "prueba": prueba,
            "jugadores": str(cantidad),
            "repeticiones": str(repeticiones),
            "mediana_ms": _numero(_mediana_ms(llamada, repeticiones)),
            **entorno,
            **metadatos,
        }
        for prueba, cantidad, llamada in pruebas
    ]


def _coma(numero: str) -> str:
    return numero.replace(".", ",")


def _tabla(encabezados: tuple[str, ...], filas: list[tuple[str, ...]]) -> list[str]:
    return [
        f"| {' | '.join(encabezados)} |",
        f"|{'---|' * len(encabezados)}",
        *(f"| {' | '.join(fila)} |" for fila in filas),
    ]


def _seccion_propiedades(filas: list[Fila]) -> list[str]:
    return [
        "## 1. Propiedades de la etapa 1",
        "",
        *_tabla(
            ("Propiedad", "Escenarios", "Cumplen", "%"),
            [
                (fila["propiedad"], fila["escenarios"], fila["cumplen"], _coma(fila["porcentaje"]))
                for fila in filas
            ],
        ),
    ]


def _seccion_metricas(titulo: str, filas: list[Fila], nota: str) -> list[str]:
    return [
        titulo,
        "",
        nota,
        "",
        *_tabla(("Métrica", "Valor"), [(fila["metrica"], _coma(fila["valor"])) for fila in filas]),
    ]


def _seccion_embudo(filas: list[Fila]) -> list[str]:
    mayor = max(filas[1:-1], key=lambda fila: float(fila["descartados_media"]))
    return [
        "## 3b. Embudo de filtros",
        "",
        *_tabla(
            ("Paso", "Etapa", "Restantes (media)", "Descartados (media)"),
            [
                (
                    fila["paso"],
                    fila["etapa"],
                    _coma(fila["restantes_media"]),
                    _coma(fila["descartados_media"]),
                )
                for fila in filas
            ],
        ),
        "",
        f"El filtro que más candidatos descarta es **{mayor['etapa']}**: "
        f"{_coma(mayor['descartados_media'])} de media por escenario.",
    ]


def _seccion_poblacion(filas: list[Fila]) -> list[str]:
    columnas = (
        "porcentaje_suficientes",
        "recomendados_media",
        "puntaje_medio",
        "escenarios_sin_recomendados",
    )
    return [
        "## 3c. Cobertura según la población",
        "",
        "Los mismos 150 escenarios; solo cambia la cantidad de jugadores generados.",
        "",
        *_tabla(
            ("Jugadores", "% suficientes", "Recomendados (media)", "Puntaje medio", "Sin recom."),
            [
                (fila["jugadores"], *(_coma(fila[columna]) for columna in columnas))
                for fila in filas
            ],
        ),
    ]


def _seccion_equilibrio(filas: list[Fila]) -> list[str]:
    columnas = (
        "cantidad_grupos",
        "diferencia_media",
        "puntaje_medio",
        "porcentaje_puntaje_0_80",
        "coincide_optimo_nivel",
        "porcentaje_optimo_nivel",
    )
    return [
        "## 4. Equilibrio de la etapa 2 contra las líneas base",
        "",
        *_tabla(
            (
                "Grupos",
                "Método",
                "Cantidad",
                "Diferencia media",
                "Puntaje medio",
                "% ≥ 0,80",
                "Óptimo por nivel",
                "% óptimo",
            ),
            [
                (fila["grupos"], fila["metodo"], *(_coma(fila[columna]) for columna in columnas))
                for fila in filas
            ],
        ),
    ]


def _seccion_sensibilidad(filas: list[Fila]) -> list[str]:
    columnas = (
        "porcentaje_suficientes",
        "cambio_puntos",
        "escenarios_con_3_en_ambas",
        "precision_at_3_media",
        "porcentaje_top3_identico",
    )
    return [
        "## 5. Sensibilidad",
        "",
        "Se varía un parámetro por vez; los parámetros completos de cada fila están en el CSV.",
        "",
        *_tabla(
            (
                "Configuración",
                "% suficientes",
                "Cambio (puntos)",
                "Con 3 en ambas",
                "precision@3",
                "% top 3 idéntico",
            ),
            [
                (f"`{fila['configuracion']}`", *(_coma(fila[columna]) for columna in columnas))
                for fila in filas
            ],
        ),
    ]


def _seccion_rendimiento(filas: list[Fila]) -> list[str]:
    return [
        "## 6. Rendimiento",
        "",
        f"Mediana de {filas[0]['repeticiones']} repeticiones con `time.perf_counter`, en "
        f"Python {filas[0]['python']} sobre {filas[0]['sistema']}. Los tiempos dependen de la "
        "máquina y cambian en cada corrida.",
        "",
        *_tabla(
            ("Prueba", "Jugadores", "Mediana (ms)"),
            [(fila["prueba"], fila["jugadores"], _coma(fila["mediana_ms"])) for fila in filas],
        ),
    ]


def escribir_resumen(
    directorio: Path,
    resultados: dict[str, list[Fila]],
    semilla: int = SEMILLA,
    p: Parametros = PARAMETROS,
) -> Path:
    """Escribe `directorio/resumen.md` con una tabla por experimento, del 1 al 6.

    `resultados` tiene las filas de cada experimento, con el nombre de su CSV como clave.
    Los números van con coma decimal, listos para la tesis. Devuelve la ruta.
    """
    secciones = [
        _seccion_propiedades(resultados["01_propiedades.csv"]),
        _seccion_metricas(
            "## 2. Consistencia con el oráculo",
            resultados["02_oraculo.csv"],
            "Con umbral 0, sobre los mismos candidatos filtrados. Es un chequeo de "
            "consistencia, no una validación de calidad.",
        ),
        _seccion_metricas(
            "## 3. Cobertura de recomendaciones",
            resultados["03_cobertura.csv"],
            "150 escenarios aleatorios con 200 jugadores.",
        ),
        _seccion_embudo(resultados["03b_embudo.csv"]),
        _seccion_poblacion(resultados["03c_poblacion.csv"]),
        _seccion_equilibrio(resultados["04_equilibrio.csv"]),
        _seccion_sensibilidad(resultados["05_sensibilidad.csv"]),
        _seccion_rendimiento(resultados["06_rendimiento.csv"]),
    ]
    lineas = [
        "# Resumen de la evaluación del motor",
        "",
        "Generado con `python -m evaluacion.experimentos`; los CSV de esta carpeta tienen el "
        "detalle de cada experimento.",
        "",
        f"Semilla: {semilla}. Parámetros base: `{formatear_parametros(p)}`.",
    ]
    for seccion in secciones:
        lineas += ["", *seccion]
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / "resumen.md"
    with ruta.open("w", encoding="utf-8", newline="\n") as archivo:
        archivo.write("\n".join(lineas) + "\n")
    return ruta


def main() -> None:
    """Genera los datos con SEMILLA y escribe los CSV de los experimentos 1 a 6 y el resumen."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    jugadores = generar_jugadores()
    candidatos = tuple(jugador.candidato for jugador in jugadores)
    aleatorios = generar_escenarios(jugadores)
    grupos_recomendados = grupos_de_recomendados(jugadores, aleatorios)
    grupos_aleatorios = generar_grupos_aleatorios(jugadores)
    resultados = {
        "01_propiedades.csv": experimento_propiedades(aleatorios, candidatos, ESCENARIOS_DIRIGIDOS),
        "02_oraculo.csv": experimento_oraculo(aleatorios, candidatos),
        "03_cobertura.csv": experimento_cobertura(aleatorios, candidatos),
        "03b_embudo.csv": experimento_embudo(aleatorios, candidatos),
        "03c_poblacion.csv": experimento_poblacion(aleatorios),
        "04_equilibrio.csv": experimento_equilibrio(grupos_recomendados, grupos_aleatorios),
        "05_sensibilidad.csv": experimento_sensibilidad(aleatorios, candidatos),
        "06_rendimiento.csv": experimento_rendimiento(aleatorios[0], grupos_recomendados[0]),
    }
    for nombre, filas in resultados.items():
        ruta = escribir_csv(DIRECTORIO_RESULTADOS, nombre, filas)
        logger.info("Escrito %s", ruta.name)
    ruta = escribir_resumen(DIRECTORIO_RESULTADOS, resultados)
    logger.info("Escrito %s", ruta.name)


if __name__ == "__main__":
    main()
