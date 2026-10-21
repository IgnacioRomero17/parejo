# 12 · Seleccionar e invitar (seguimiento del encuentro)

Imagen: `12-seleccionar-invitar.png` (2 confirmados, 1 pendiente, 1 seleccionado) · Ruta: `/encuentros/:id` mientras está Buscando participantes · Acceso: solo el organizador · HU: HU-008

## Contenido
- Línea superior: "ENCUENTRO · Sáb 3 oct 2026 · 18:00 · Río Ceballos". Título "Seleccionar e invitar jugadores".

### Panel izquierdo · "Jugadores recomendados" ("Ordenados por compatibilidad")
- **Ya invitados** ("N invitaciones enviadas"): cada invitado con iniciales, nombre, localidad, nivel y etiqueta Aceptada / Rechazada / Pendiente, en orden de envío (datos de `GET encuentros/{id}`). Sin número de posición ni franja (en la imagen aparecen; no se implementan). No se pueden volver a invitar.
- **Disponibles para invitar** (etiqueta "N lugar(es) libre(s) · M seleccionado(s)"): candidatos del motor que todavía no fueron invitados, con casilla de selección.
  - Se pueden marcar hasta tantos como lugares libres. Al llegar al límite, las demás casillas quedan deshabilitadas y se muestra: "Como queda{n} N lugar(es) libre(s), podés seleccionar N jugador(es). Para elegir a otro, quitá la selección actual."
  - Seleccionado: fila resaltada en azul y texto "Seleccionado".
- Pie: "Vas a invitar a **{nombres}**" y botón "Enviar invitación (N)". Deshabilitado sin selección.

### Panel derecho · "Lugares del encuentro"
- "N de 4 · confirmados · M lugares restantes" (M = 4 − confirmados, incluye los que esperan respuesta) y etiqueta del estado.
- Lista: confirmados (verde, "Confirmado"), invitaciones pendientes (borde amarillo punteado, "Invitación enviada" / "Pendiente") y seleccionados sin enviar (borde azul punteado, "Seleccionado · sin enviar").
- Texto: "Con 4 participantes confirmados se habilita el inicio de la formación automática de parejas." y botón "Formar parejas equilibradas" **deshabilitado**.

## Acciones
| Elemento | Resultado |
|---|---|
| Casilla de un candidato | selecciona / deselecciona |
| Enviar invitación (N) | crea N invitaciones pendientes, aviso "Invitación enviada" / "N invitaciones enviadas" y actualiza ambos paneles |

## Estados
- Sin lugares libres por invitaciones pendientes: la sección "Disponibles para invitar" muestra "Esperá la respuesta de las invitaciones pendientes."
- Al llegar a 4 confirmados, esta ruta muestra la pantalla 14.
