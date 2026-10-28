"""Experimentos 1 a 3 y escritura de resultados."""

import csv

from evaluacion.escenarios import ESCENARIOS_DIRIGIDOS
from evaluacion.experimentos import (
    escribir_csv,
    experimento_cobertura,
    experimento_oraculo,
    experimento_propiedades,
    formatear_parametros,
)
from evaluacion.generador import SEMILLA, generar_escenarios, generar_jugadores
from motor.parametros import PARAMETROS

JUGADORES = generar_jugadores()
CANDIDATOS = tuple(jugador.candidato for jugador in JUGADORES)
ESCENARIOS = generar_escenarios(JUGADORES)


def test_experimentos_propiedades_dan_100_por_ciento():
    filas = experimento_propiedades(ESCENARIOS, CANDIDATOS, ESCENARIOS_DIRIGIDOS)

    assert [fila["propiedad"] for fila in filas] == [
        "ningun_excluido_recomendado",
        "orden_descendente",
        "puntajes_entre_0_y_1",
        "resultado_identico_al_repetir",
        "resultado_esperado_dirigidos",
    ]
    assert [fila["escenarios"] for fila in filas] == ["155"] * 4 + ["5"]
    assert all(fila["porcentaje"] == "100.0000" for fila in filas)


def test_experimentos_oraculo_informa_los_parametros_sin_umbral():
    filas = experimento_oraculo(ESCENARIOS, CANDIDATOS)
    valores = {fila["metrica"]: fila["valor"] for fila in filas}
    con_coincidencias = sum(int(valores[f"escenarios_con_{k}_de_3"]) for k in range(4))

    assert con_coincidencias == int(valores["escenarios_con_3_filtrados"])
    assert 0 <= float(valores["precision_at_3_media"]) <= 1
    assert all("umbral_minimo=0.0;" in fila["parametros"] for fila in filas)


def test_experimentos_cobertura_cuenta_los_150_escenarios():
    filas = experimento_cobertura(ESCENARIOS, CANDIDATOS)
    valores = {fila["metrica"]: fila["valor"] for fila in filas}

    assert valores["escenarios"] == "150"
    assert 0 <= float(valores["porcentaje_suficientes"]) <= 100
    assert all(fila["parametros"] == formatear_parametros(PARAMETROS) for fila in filas)


def test_experimentos_csv_con_semilla_parametros_y_fin_de_linea_lf(tmp_path):
    filas = experimento_cobertura(ESCENARIOS, CANDIDATOS)

    ruta = escribir_csv(tmp_path / "resultados", "cobertura.csv", filas)

    assert b"\r\n" not in ruta.read_bytes()
    with ruta.open(encoding="utf-8", newline="") as archivo:
        leidas = list(csv.DictReader(archivo))
    assert leidas == filas
    assert all(fila["semilla"] == str(SEMILLA) for fila in leidas)


def test_experimentos_dan_lo_mismo_al_repetir():
    assert experimento_oraculo(ESCENARIOS, CANDIDATOS) == experimento_oraculo(
        generar_escenarios(generar_jugadores()), CANDIDATOS
    )
