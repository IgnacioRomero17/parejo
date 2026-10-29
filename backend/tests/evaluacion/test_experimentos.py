"""Experimentos 1 a 6, escritura de resultados y resumen."""

import csv
from decimal import Decimal

import pytest

from evaluacion.escenarios import ESCENARIOS_DIRIGIDOS
from evaluacion.experimentos import (
    ETAPAS_EMBUDO,
    METODOS,
    PESOS_ETAPA1,
    configuraciones_sensibilidad,
    embudo,
    escribir_csv,
    escribir_resumen,
    experimento_cobertura,
    experimento_embudo,
    experimento_equilibrio,
    experimento_oraculo,
    experimento_poblacion,
    experimento_propiedades,
    experimento_rendimiento,
    experimento_sensibilidad,
    formatear_parametros,
)
from evaluacion.generador import (
    SEMILLA,
    generar_escenarios,
    generar_grupos_aleatorios,
    generar_jugadores,
    grupos_de_recomendados,
)
from motor.parametros import PARAMETROS
from motor.recomendar import evaluar_candidato, nivel_promedio

JUGADORES = generar_jugadores()
CANDIDATOS = tuple(jugador.candidato for jugador in JUGADORES)
ESCENARIOS = generar_escenarios(JUGADORES)
GRUPOS_RECOMENDADOS = grupos_de_recomendados(JUGADORES, ESCENARIOS)
GRUPOS_ALEATORIOS = generar_grupos_aleatorios(JUGADORES)


def _valores(filas):
    return {fila["metrica"]: fila["valor"] for fila in filas}


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
    valores = _valores(filas)
    con_coincidencias = sum(int(valores[f"escenarios_con_{k}_de_3"]) for k in range(4))

    assert con_coincidencias == int(valores["escenarios_con_3_filtrados"])
    assert 0 <= float(valores["precision_at_3_media"]) <= 1
    assert all("umbral_minimo=0.0;" in fila["parametros"] for fila in filas)


def test_experimentos_cobertura_cuenta_los_150_escenarios():
    filas = experimento_cobertura(ESCENARIOS, CANDIDATOS)
    valores = _valores(filas)

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


def test_experimentos_embudo_coincide_con_los_filtros_y_el_umbral_del_motor():
    for escenario in ESCENARIOS[:20]:
        conteos = embudo(escenario.encuentro, CANDIDATOS, escenario.lugares_libres)
        promedio = nivel_promedio(escenario.encuentro.niveles_confirmados)
        pasan_filtros = [
            evaluar_candidato(candidato, escenario.encuentro, promedio) for candidato in CANDIDATOS
        ]

        assert len(conteos) == len(ETAPAS_EMBUDO)
        assert conteos[0] == len(CANDIDATOS)
        assert list(conteos) == sorted(conteos, reverse=True)
        assert conteos[-2] == sum(r is not None for r in pasan_filtros)


def test_experimentos_embudo_termina_en_los_recomendados_del_experimento_3():
    filas = experimento_embudo(ESCENARIOS, CANDIDATOS)
    cobertura = _valores(experimento_cobertura(ESCENARIOS, CANDIDATOS))

    assert [fila["etapa"] for fila in filas] == list(ETAPAS_EMBUDO)
    assert filas[0]["restantes_media"] == "200.0000"
    assert filas[-1]["restantes_media"] == cobertura["recomendados_media"]
    assert all(float(fila["descartados_media"]) >= 0 for fila in filas)


def test_experimentos_embudo_descarta_al_organizador_en_no_excluido():
    filas = {fila["etapa"]: fila for fila in experimento_embudo(ESCENARIOS, CANDIDATOS)}

    # Solo el organizador está excluido, y se descarta ahí solo si estaba disponible.
    assert 0 < float(filas["no_excluido"]["descartados_media"]) <= 1


def test_experimentos_poblacion_con_200_repite_el_experimento_3():
    filas = experimento_poblacion(ESCENARIOS, poblaciones=(200, 500))
    cobertura = _valores(experimento_cobertura(ESCENARIOS, CANDIDATOS))

    assert [fila["jugadores"] for fila in filas] == ["200", "500"]
    assert {clave: filas[0][clave] for clave in cobertura} == cobertura
    assert float(filas[1]["porcentaje_suficientes"]) >= float(filas[0]["porcentaje_suficientes"])


def test_experimentos_equilibrio_el_motor_no_pierde_contra_ninguna_linea_base():
    filas = experimento_equilibrio(GRUPOS_RECOMENDADOS, GRUPOS_ALEATORIOS)
    por_clave = {(fila["grupos"], fila["metodo"]): fila for fila in filas}
    cantidades = {
        "recomendados": len(GRUPOS_RECOMENDADOS),
        "aleatorios": len(GRUPOS_ALEATORIOS),
        "todos": len(GRUPOS_RECOMENDADOS) + len(GRUPOS_ALEATORIOS),
    }

    assert len(filas) == 3 * len(METODOS)
    for fuente, cantidad in cantidades.items():
        motor = por_clave[(fuente, "motor")]
        assert motor["cantidad_grupos"] == str(cantidad)
        for metodo in METODOS:
            linea = por_clave[(fuente, metodo)]
            assert Decimal(motor["puntaje_medio"]) >= Decimal(linea["puntaje_medio"])
            assert int(linea["coincide_optimo_nivel"]) <= cantidad


def test_experimentos_equilibrio_da_lo_mismo_al_repetir():
    assert experimento_equilibrio(GRUPOS_RECOMENDADOS, GRUPOS_ALEATORIOS) == experimento_equilibrio(
        GRUPOS_RECOMENDADOS, generar_grupos_aleatorios(JUGADORES)
    )


def test_experimentos_sensibilidad_pesos_variados_fijos_y_suman_1():
    configuraciones = dict(configuraciones_sensibilidad())
    peso_tipo_mas = configuraciones["peso_tipo+0.10"]

    assert len(configuraciones) == 12
    assert configuraciones["base"] == PARAMETROS
    assert peso_tipo_mas.peso_tipo == 0.20
    assert peso_tipo_mas.peso_nivel == pytest.approx(0.60 * 0.80 / 0.90)
    assert configuraciones["peso_nivel-0.10"].peso_nivel == 0.50
    for parametros in configuraciones.values():
        suma = sum(getattr(parametros, peso) for peso in PESOS_ETAPA1)
        assert suma == pytest.approx(1)


def test_experimentos_sensibilidad_la_base_no_cambia():
    filas = experimento_sensibilidad(ESCENARIOS, CANDIDATOS)
    base = filas[0]
    cobertura = _valores(experimento_cobertura(ESCENARIOS, CANDIDATOS))

    assert base["configuracion"] == "base"
    assert base["porcentaje_suficientes"] == cobertura["porcentaje_suficientes"]
    assert base["cambio_puntos"] == "0.0000"
    assert base["precision_at_3_media"] == "1.0000"
    assert base["porcentaje_top3_identico"] == "100.0000"
    umbral = next(fila for fila in filas if fila["configuracion"] == "umbral_minimo=0.6")
    assert "umbral_minimo=0.6;" in umbral["parametros"]


def test_experimentos_rendimiento_mide_cada_tamanio_y_la_etapa_2():
    filas = experimento_rendimiento(
        ESCENARIOS[0], GRUPOS_RECOMENDADOS[0], tamanios=(10, 20), repeticiones=2
    )

    assert [(fila["prueba"], fila["jugadores"]) for fila in filas] == [
        ("recomendar", "10"),
        ("recomendar", "20"),
        ("etapa_2", "4"),
    ]
    assert all(float(fila["mediana_ms"]) > 0 for fila in filas)
    assert all(fila["python"] and fila["sistema"] for fila in filas)


def test_experimentos_resumen_con_una_seccion_por_experimento(tmp_path):
    resultados = {
        "01_propiedades.csv": experimento_propiedades(ESCENARIOS, CANDIDATOS, ESCENARIOS_DIRIGIDOS),
        "02_oraculo.csv": experimento_oraculo(ESCENARIOS, CANDIDATOS),
        "03_cobertura.csv": experimento_cobertura(ESCENARIOS, CANDIDATOS),
        "03b_embudo.csv": experimento_embudo(ESCENARIOS, CANDIDATOS),
        "03c_poblacion.csv": experimento_poblacion(ESCENARIOS, poblaciones=(200,)),
        "04_equilibrio.csv": experimento_equilibrio(GRUPOS_RECOMENDADOS, GRUPOS_ALEATORIOS),
        "05_sensibilidad.csv": experimento_sensibilidad(ESCENARIOS, CANDIDATOS),
        "06_rendimiento.csv": experimento_rendimiento(
            ESCENARIOS[0], GRUPOS_RECOMENDADOS[0], tamanios=(10,), repeticiones=1
        ),
    }

    ruta = escribir_resumen(tmp_path, resultados)

    contenido = ruta.read_bytes()
    texto = contenido.decode("utf-8")
    assert b"\r\n" not in contenido
    for numero in ("1", "2", "3", "3b", "3c", "4", "5", "6"):
        assert f"\n## {numero}. " in texto
    assert f"Semilla: {SEMILLA}." in texto
    assert "El filtro que más candidatos descarta es **" in texto
