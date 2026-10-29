# Resumen de la evaluación del motor

Generado con `python -m evaluacion.experimentos`; los CSV de esta carpeta tienen el detalle de cada experimento.

Semilla: 2026. Parámetros base: `dif_max_nivel=1.0; dist_max_km=40.0; umbral_minimo=0.55; peso_nivel=0.6; peso_geo=0.3; peso_tipo=0.1; valor_tipo_opuesto=0.0; d_max_equilibrio=2.0; peso_equilibrio_nivel=0.8; peso_equilibrio_lado=0.2; lugares_por_encuentro=4; radio_tierra_km=6371.0`.

## 1. Propiedades de la etapa 1

| Propiedad | Escenarios | Cumplen | % |
|---|---|---|---|
| ningun_excluido_recomendado | 155 | 155 | 100,0000 |
| orden_descendente | 155 | 155 | 100,0000 |
| puntajes_entre_0_y_1 | 155 | 155 | 100,0000 |
| resultado_identico_al_repetir | 155 | 155 | 100,0000 |
| resultado_esperado_dirigidos | 5 | 5 | 100,0000 |

## 2. Consistencia con el oráculo

Con umbral 0, sobre los mismos candidatos filtrados. Es un chequeo de consistencia, no una validación de calidad.

| Métrica | Valor |
|---|---|
| escenarios | 150 |
| escenarios_con_3_filtrados | 94 |
| precision_at_3_media | 0,9823 |
| precision_at_3_minima | 0,6667 |
| escenarios_con_0_de_3 | 0 |
| escenarios_con_1_de_3 | 0 |
| escenarios_con_2_de_3 | 5 |
| escenarios_con_3_de_3 | 89 |

## 3. Cobertura de recomendaciones

150 escenarios aleatorios con 200 jugadores.

| Métrica | Valor |
|---|---|
| escenarios | 150 |
| porcentaje_suficientes | 28,6667 |
| recomendados_media | 1,7400 |
| puntaje_medio | 0,7384 |
| escenarios_sin_recomendados | 42 |

## 3b. Embudo de filtros

| Paso | Etapa | Restantes (media) | Descartados (media) |
|---|---|---|---|
| 0 | inicial | 200,0000 | 0,0000 |
| 1 | activo | 200,0000 | 0,0000 |
| 2 | disponible | 168,0000 | 32,0000 |
| 3 | perfil_completo | 168,0000 | 0,0000 |
| 4 | no_excluido | 167,1200 | 0,8800 |
| 5 | disponibilidad | 6,7133 | 160,4067 |
| 6 | distancia | 5,7667 | 0,9467 |
| 7 | nivel | 3,4067 | 2,3600 |
| 8 | umbral | 1,7400 | 1,6667 |

El filtro que más candidatos descarta es **disponibilidad**: 160,4067 de media por escenario.

## 3c. Cobertura según la población

Los mismos 150 escenarios; solo cambia la cantidad de jugadores generados.

| Jugadores | % suficientes | Recomendados (media) | Puntaje medio | Sin recom. |
|---|---|---|---|---|
| 200 | 28,6667 | 1,7400 | 0,7384 | 42 |
| 500 | 64,0000 | 3,9133 | 0,7377 | 18 |
| 1000 | 76,6667 | 7,6267 | 0,7264 | 11 |

## 4. Equilibrio de la etapa 2 contra las líneas base

| Grupos | Método | Cantidad | Diferencia media | Puntaje medio | % ≥ 0,80 | Óptimo por nivel | % óptimo |
|---|---|---|---|---|---|---|---|
| recomendados | motor | 43 | 0,1570 | 0,8860 | 90,6977 | 43 | 100,0000 |
| recomendados | aleatoria | 43 | 0,1802 | 0,8581 | 83,7209 | 41 | 95,3488 |
| recomendados | orden_llegada | 43 | 0,2151 | 0,8465 | 86,0465 | 38 | 88,3721 |
| recomendados | mas_fuertes_juntos | 43 | 0,3081 | 0,8093 | 72,0930 | 30 | 69,7674 |
| aleatorios | motor | 150 | 0,3400 | 0,8087 | 74,0000 | 150 | 100,0000 |
| aleatorios | aleatoria | 150 | 0,9000 | 0,5940 | 33,3333 | 68 | 45,3333 |
| aleatorios | orden_llegada | 150 | 0,8533 | 0,6113 | 34,6667 | 75 | 50,0000 |
| aleatorios | mas_fuertes_juntos | 150 | 1,5500 | 0,3680 | 2,6667 | 2 | 1,3333 |
| todos | motor | 193 | 0,2992 | 0,8259 | 77,7202 | 193 | 100,0000 |
| todos | aleatoria | 193 | 0,7396 | 0,6528 | 44,5596 | 109 | 56,4767 |
| todos | orden_llegada | 193 | 0,7111 | 0,6637 | 46,1140 | 113 | 58,5492 |
| todos | mas_fuertes_juntos | 193 | 1,2733 | 0,4663 | 18,1347 | 32 | 16,5803 |

## 5. Sensibilidad

Se varía un parámetro por vez; los parámetros completos de cada fila están en el CSV.

| Configuración | % suficientes | Cambio (puntos) | Con 3 en ambas | precision@3 | % top 3 idéntico |
|---|---|---|---|---|---|
| `base` | 28,6667 | 0,0000 | 43 | 1,0000 | 100,0000 |
| `peso_nivel+0.10` | 26,6667 | -2,0000 | 40 | 1,0000 | 95,3333 |
| `peso_nivel-0.10` | 31,3333 | 2,6667 | 43 | 0,9845 | 92,0000 |
| `peso_geo+0.10` | 30,0000 | 1,3333 | 42 | 0,9921 | 90,6667 |
| `peso_geo-0.10` | 26,6667 | -2,0000 | 39 | 0,9915 | 91,3333 |
| `peso_tipo+0.10` | 29,3333 | 0,6667 | 39 | 0,9658 | 82,6667 |
| `peso_tipo-0.10` | 25,3333 | -3,3333 | 34 | 0,9804 | 78,0000 |
| `umbral_minimo=0.5` | 34,6667 | 6,0000 | 43 | 1,0000 | 87,3333 |
| `umbral_minimo=0.6` | 19,3333 | -9,3333 | 29 | 1,0000 | 82,6667 |
| `dif_max_nivel=0.5` | 4,6667 | -24,0000 | 7 | 1,0000 | 48,0000 |
| `dif_max_nivel=1.5` | 42,0000 | 13,3333 | 43 | 0,9845 | 70,0000 |
| `dist_max_km=20.0` | 10,6667 | -18,0000 | 16 | 0,9792 | 58,0000 |

## 6. Rendimiento

Mediana de 20 repeticiones con `time.perf_counter`, en Python 3.13.17 sobre Windows-10-10.0.19045-SP0. Los tiempos dependen de la máquina y cambian en cada corrida.

| Prueba | Jugadores | Mediana (ms) |
|---|---|---|
| recomendar | 100 | 0,1026 |
| recomendar | 200 | 0,1913 |
| recomendar | 1000 | 0,8917 |
| recomendar | 5000 | 4,6116 |
| etapa_2 | 4 | 0,0165 |
