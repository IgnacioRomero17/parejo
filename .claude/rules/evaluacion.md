---
paths:
  - "backend/evaluacion/**"
  - "backend/tests/evaluacion/**"
  - "backend/apps/comun/management/**"
---

# Evaluación del motor (Objetivo 4 de la tesis)

Mide la calidad de las recomendaciones y el equilibrio de los encuentros. Todo debe ser **reproducible**: mismos datos y misma semilla, mismos resultados.

## Principios
- Los scripts usan el motor **directamente** (`motor.recomendar`, `motor.equilibrio`), sin base de datos ni Django. Solo la carga del dataset de demostración toca la base.
- Solo biblioteca estándar de Python (`random`, `statistics`, `csv`, `time`). Sin pandas, numpy ni librerías de gráficos.
- Semilla global `SEMILLA = 2026`. Cada generador usa su propio `random.Random(semilla)`, nunca el `random` global.
- Para variar parámetros se pasa otro `Parametros` al motor; **nunca se modifica `motor/` desde acá**.
- Cada archivo de resultados incluye la semilla y los parámetros usados.

## Estructura
```
backend/evaluacion/
  localidades.py      # copia del catálogo (independiente del fixture)
  generador.py        # jugadores y escenarios sintéticos
  escenarios.py       # escenarios dirigidos
  oraculo.py          # ranking lexicográfico de referencia
  lineas_base.py      # métodos alternativos de armar parejas
  experimentos.py     # corre todo y escribe resultados
  datasets/demo.json  # dataset de demostración
  resultados/         # CSV + resumen.md generados
```
Comando `python manage.py cargar_datos` (en `apps/comun/management/commands/`): carga `demo.json` en la base. Si ya hay datos, pide `--reemplazar`.

## Dataset de demostración (`demo.json`)
- Entre 15 y 30 jugadores con nombre y apellido inventados, perfil completo, preferencias y franjas, distribuidos en las localidades del catálogo.
- Incluye a los 7 jugadores del caso de ejemplo de la regla del motor, con esos mismos datos.
- Contraseña común documentada en el archivo, solo para la demostración.
- Se puede editar después desde el admin.

## Jugadores sintéticos (`generador.py`) · supuestos confirmados por el autor
| Dato | Distribución |
|---|---|
| Cantidad | 200 jugadores |
| Nivel | normal (media 4, desvío 1,2), redondeada a 0,5 y acotada a 1–7 |
| Localidad | uniforme sobre el catálogo |
| Tipo preferido | Recreativo 35 %, Competitivo 35 %, Indiferente 30 % |
| Lado | Drive 40 %, Revés 40 %, Indiferente 20 % |
| Franjas | 1 a 3, días con más peso en fin de semana, 2 a 4 horas, pasos de 30 min, entre 08:00 y 23:00 |
| Disponible / activo | 85 % / 100 % |

## Escenarios
- **Aleatorios:** 150 encuentros (organizador al azar, fecha en los próximos 14 días, hora entre 08:00 y 21:30, duración 60/90/120, localidad y tipo al azar).
- **Dirigidos** (`escenarios.py`), con resultado esperado conocido:
  1. Nadie compatible.
  2. Exactamente tantos candidatos como lugares libres.
  3. Empates de puntaje que se resuelven por desempate.
  4. Los cuatro jugadores con el mismo nivel.
  5. Candidatos en el límite de distancia y de diferencia de nivel.
- **Grupos de 4 para la etapa 2:** organizador + los 3 primeros recomendados de cada escenario aleatorio con al menos 3 candidatos, más 150 grupos de 4 jugadores al azar.

## Experimentos y métricas
1. **Propiedades (etapa 1):** en todos los escenarios, ningún excluido recomendado, orden descendente, puntajes entre 0 y 1, resultado idéntico al repetir. Debe dar 100 %.
2. **Consistencia con el oráculo:** precision@3 entre el ranking del motor y el oráculo lexicográfico (menor diferencia de nivel; a igualdad, menor distancia), sobre los mismos candidatos filtrados. Se informa como chequeo de consistencia, no como validación de calidad.
3. **Cobertura de recomendaciones:** % de escenarios con candidatos suficientes, cantidad media de recomendados y puntaje medio.
  - 3b. **Embudo de filtros:** en los 150 escenarios, cantidad media de candidatos que quedan después de cada filtro, en el orden del motor, y después del umbral. Identifica qué filtro reduce más los candidatos.
  - 3c. **Cobertura según la población:** repetir el experimento 3 con 200, 500 y 1000 jugadores generados con las mismas distribuciones (la semilla fija, y la cantidad como único cambio).
4. **Equilibrio (etapa 2):** para cada grupo, comparar la propuesta del motor con las líneas base: aleatoria (con semilla), orden de llegada (combinación 1) y "los dos más fuertes juntos". Métricas: diferencia media de promedios entre parejas, puntaje de equilibrio medio y % de grupos con puntaje mayor o igual a **0,80** (valor de referencia: como máximo medio nivel de diferencia entre parejas con lados complementarios). Informar también cuántas veces el motor coincide con el óptimo por nivel (menor diferencia de promedios).
5. **Sensibilidad:** variar de a un parámetro: pesos de la etapa 1 ±0,10 (renormalizando a 1), umbral 0,50 / 0,55 / 0,60, `dif_max_nivel` 0,5 / 1 / 1,5, `dist_max_km` 20 / 40. Medir el cambio en el % de escenarios suficientes y la coincidencia del top 3 con la configuración base.
6. **Rendimiento:** tiempo de `recomendar` con 100, 200, 1000 y 5000 candidatos, y de la etapa 2; mediana de 20 repeticiones con `time.perf_counter`.

## Resultados
- Un CSV por experimento en `evaluacion/resultados/` y un `resumen.md` con las tablas principales, listos para pasar a la tesis.
- `python -m evaluacion.experimentos` regenera todo. Los resultados se versionan para poder citarlos.
