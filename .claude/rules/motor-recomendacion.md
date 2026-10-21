---
paths:
  - "backend/motor/**"
  - "backend/tests/motor/**"
  - "backend/apps/encuentros/servicios*.py"
---

# Motor de recomendación y balanceo

Es el núcleo de la tesis. Esta regla es **completa**: para trabajar en el motor no hace falta leer `docs/`. Cualquier cambio de fórmula, filtro, parámetro o desempate se consulta con el autor antes de hacerlo.

## Principios
- **Python puro:** `backend/motor/` no importa Django, DRF ni nada de `apps/`. Solo biblioteca estándar.
- **Entradas y salidas inmutables:** `@dataclass(frozen=True)`. El motor no consulta la base ni modifica sus entradas.
- **Determinista:** misma entrada y mismos parámetros, mismo resultado y mismo orden. Prohibido usar azar, la hora actual o el orden de un `set`.
- **Parámetros inyectables:** cada función pública recibe `p: Parametros = PARAMETROS`. Así la evaluación puede probar otros valores sin tocar el código.

## Estructura
```
backend/motor/
  parametros.py   # Parametros + PARAMETROS (único lugar con números)
  tipos.py        # dataclasses de entrada y salida
  redondeo.py     # redondear4()
  geo.py          # haversine_km()
  filtros.py      # un filtro por función
  puntaje.py      # un criterio por función + puntaje final
  recomendar.py   # etapa 1: recomendar()
  equilibrio.py   # etapa 2: evaluar_combinaciones(), elegir_mejor()
```

## Parámetros (`parametros.py`)
Valores iniciales, provisionales hasta calibrarlos con el dataset sintético.

| Campo | Valor | Uso |
|---|---|---|
| `dif_max_nivel` | 1.0 | filtro y criterio de nivel (etapa 1) |
| `dist_max_km` | 40.0 | filtro y criterio geográfico |
| `umbral_minimo` | 0.55 | puntaje mínimo para recomendar |
| `peso_nivel`, `peso_geo`, `peso_tipo` | 0.60, 0.30, 0.10 | puntaje etapa 1 (suman 1) |
| `valor_tipo_opuesto` | 0.0 | criterio de tipo cuando no coinciden |
| `d_max_equilibrio` | 2.0 | equilibrio de nivel (etapa 2) |
| `peso_equilibrio_nivel`, `peso_equilibrio_lado` | 0.80, 0.20 | puntaje etapa 2 (suman 1) |
| `lugares_por_encuentro` | 4 | tamaño del encuentro |
| `radio_tierra_km` | 6371.0 | Haversine |

`Parametros` valida en `__post_init__` que cada grupo de pesos sume 1 (tolerancia 1e-9) y que los máximos sean positivos.

## Redondeo
`redondear4(x) -> Decimal`: `Decimal(repr(x)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)`.
Los puntajes finales de ambas etapas se redondean así **antes** de compararlos, ordenarlos o devolverlos. Los criterios intermedios se calculan en `float`.

## Distancia (`geo.py`)
`haversine_km(lat1, lon1, lat2, lon2, p)` en grados decimales:
```
a = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)
d = 2·R·atan2(√a, √(1−a))      # R = p.radio_tierra_km
```
Distancia en línea recta (limitación aceptada). Misma localidad → 0.

## Etapa 1 · Recomendar candidatos (`recomendar.py`)

### Entradas
- `EncuentroEntrada`: `fecha` (date), `hora_inicio` (time), `duracion_minutos`, `lat`, `lon` (de su localidad), `tipo` (`RECREATIVO` | `COMPETITIVO` | `INDIFERENTE`), `niveles_confirmados` (tupla, incluye al organizador; al menos 1), `ids_excluidos` (frozenset: organizador, participantes e invitados en **cualquier** estado).
- `CandidatoEntrada`: `id`, `activo`, `disponible`, `nivel` (float o None), `lat`, `lon` (None si no tiene localidad), `tipo_preferido` (None si no tiene preferencia), `franjas` (tupla de `Franja(dia, inicio, fin)`, `dia` 1 = lunes … 7 = domingo).
- `lugares_libres` (int, lo obtiene el servicio con `Encuentro.lugares_libres()`).

### Referencia de nivel
`promedio = media de niveles_confirmados` (float, sin redondear).

### Filtros eliminatorios (en este orden; si uno falla, el candidato se descarta)
1. `activo` es verdadero.
2. `disponible` es verdadero.
3. Perfil completo: `nivel`, `lat` y `lon` no son None.
4. `id` no está en `ids_excluidos`.
5. Disponibilidad: alguna franja con `dia == fecha.isoweekday()`, `inicio <= hora_inicio` y `fin >= hora_inicio + duracion`. Una sola franja tiene que cubrir el encuentro completo.
6. Distancia: `haversine_km(...) <= dist_max_km`.
7. Nivel: `abs(nivel - promedio) <= dif_max_nivel`.

### Criterios (cada uno entre 0 y 1)
- `c_nivel = 1 - abs(nivel - promedio) / dif_max_nivel`
- `c_geo = 1 - distancia_km / dist_max_km`
- `c_tipo = 1` si los tipos coinciden o alguno es `INDIFERENTE` o None; si no, `valor_tipo_opuesto`.

### Puntaje
`puntaje = redondear4(peso_nivel·c_nivel + peso_geo·c_geo + peso_tipo·c_tipo)`
Se recomiendan solo los candidatos con `puntaje >= umbral_minimo`.

### Orden y desempate
1. `puntaje` descendente.
2. `dif_nivel` ascendente.
3. `distancia_km` ascendente.
4. `id` ascendente.

### Salida
`ResultadoRecomendacion(recomendados, suficientes)`:
- `recomendados`: tupla ordenada de `Recomendacion(id, puntaje, c_nivel, c_geo, c_tipo, distancia_km, dif_nivel)`. Incluye **todos** los que superan el umbral, no se recorta a los lugares libres.
- `suficientes = len(recomendados) >= lugares_libres`.

## Etapa 2 · Formar parejas equilibradas (`equilibrio.py`)

### Entrada
Exactamente 4 `JugadorEntrada(id, nivel, lado)` con ids distintos y nivel no nulo; `lado` es `DRIVE` | `REVES` | `INDIFERENTE` | None. Si no, `ValueError`.

### Combinaciones
Ordenar por `id`: a < b < c < d. Las 3 combinaciones, siempre en este orden:
1. (a, b) vs (c, d)
2. (a, c) vs (b, d)
3. (a, d) vs (b, c)

La pareja que contiene a `a` es la Pareja 1.

### Cálculo por combinación
- `promedio1`, `promedio2`: media de nivel de cada pareja.
- `eq_nivel = max(0, 1 - abs(promedio1 - promedio2) / d_max_equilibrio)`
- `lado_pareja = 1` si son DRIVE + REVES, o si alguno es `INDIFERENTE` o None; `0` si repiten lado.
- `eq_lado = (lado_pareja1 + lado_pareja2) / 2`
- `puntaje = redondear4(peso_equilibrio_nivel·eq_nivel + peso_equilibrio_lado·eq_lado)`

Salida: `CombinacionResultado(numero, pareja1, pareja2, promedio1, promedio2, eq_nivel, eq_lado, puntaje)` para las 3.

### Elección (`elegir_mejor`)
1. Mayor `puntaje`.
2. Menor `abs(promedio1 - promedio2)`.
3. Mayor `eq_lado`.
4. Menor `numero`.

Se evalúa una sola vez por encuentro; el motor no conoce estados.

## Integración con la app (servicio de encuentros)
- `Encuentro.lugares_libres()` = 4 − confirmados − invitaciones pendientes (método del modelo; es la única implementación).
- Arma las entradas desde la base y llama al motor; puede prefiltrar en la consulta por eficiencia, pero el motor aplica igual los 7 filtros.
- El ranking no se guarda: se recalcula en cada consulta.
- Etapa 2 solo con 4 confirmados y estado `COMPLETO`. Guarda las 3 combinaciones en el orden 1, 2, 3 (la tabla no tiene número: se deduce del orden por id), sus parejas e integrantes y la propuesta en **una transacción**, y pasa el encuentro a `PROPUESTA_GENERADA`.
- Al mostrar la propuesta, promedios y equilibrios se recalculan con el motor; el puntaje mostrado es el guardado.

## Casos borde que deben cubrirse
- Solo el organizador confirmado: el promedio es su nivel.
- Promedio no entero (por ejemplo 4,6667 con tres confirmados).
- Candidato sin preferencia, sin localidad, sin franjas o con nivel None.
- Franja que empieza justo a la hora del encuentro o termina justo al final: **cubre**.
- Franja de otro día con el mismo horario: no cubre.
- Distancia exactamente igual a `dist_max_km` o diferencia de nivel exactamente igual a `dif_max_nivel`: **pasa** el filtro (criterio en 0). Con los parámetros actuales igual queda bajo el umbral; testear el filtro por separado.
- Puntaje exactamente igual al umbral: **se recomienda**.
- Cero candidatos: lista vacía y `suficientes = (lugares_libres == 0)`.
- Empates totales en etapa 1 (se resuelven por id) y en etapa 2 (por número de combinación).

## Tests obligatorios (`backend/tests/motor/`, sin base de datos)
- Un test por filtro (pasa / no pasa) y por criterio.
- Propiedades sobre datos generados con semilla fija: nunca se recomienda un excluido, el orden es descendente, los puntajes están entre 0 y 1, y dos ejecuciones dan el mismo resultado.
- Etapa 2: siempre 3 combinaciones, cada jugador en una sola pareja, nadie excluido, elección según los desempates.
- **Regresión con el caso de ejemplo** (coordenadas dentro del test, no del fixture):

  Encuentro: sábado 3/10/2026, 18:00, 90 min, Río Ceballos (-31.1653, -64.3253), COMPETITIVO. Confirmado: Tomás (id 1, nivel 4,5, DRIVE). Todos los candidatos activos, disponibles y con franja de sábado que cubre 18:00–19:30.

  | id | Jugador | Nivel | Localidad (lat, lon) | Tipo | Lado | Distancia | Puntaje |
  |---|---|---|---|---|---|---|---|
  | 2 | Valentina | 4,5 | Río Ceballos (-31.1653, -64.3253) | COMPETITIVO | REVES | 0,000 | 1.0000 |
  | 3 | Joaquín | 4,5 | Unquillo (-31.2306, -64.3175) | COMPETITIVO | DRIVE | 7,299 | 0.9453 |
  | 4 | Camila | 5,0 | Mendiolaza (-31.2606, -64.2961) | COMPETITIVO | REVES | 10,955 | 0.6178 |
  | 5 | Federico | 5,0 | Villa Allende (-31.2933, -64.2956) | INDIFERENTE | DRIVE | 14,510 | 0.5912 |
  | 6 | Bruno | 4,0 | Salsipuedes (-31.1478, -64.2958) | RECREATIVO | REVES | 3,416 | 0.5744 |
  | 7 | Agustina | 5,0 | La Calera (-31.3400, -64.3350) | COMPETITIVO | INDIFERENTE | 19,448 | 0.5541 |

  Orden esperado: 2, 3, 4, 5, 6, 7.

  Etapa 2 con Tomás (1), Valentina (2), Camila (4) y Federico (5): combinación 1 = 0.8000 (4,50 vs 5,00), combinación 2 = 1.0000 (4,75 vs 4,75), combinación 3 = 0.8000 (4,75 vs 4,75, ambas parejas repiten lado). Se elige la 2: Tomás + Camila vs Valentina + Federico.
