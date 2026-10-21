# 10 · Jugadores recomendados

Imagen: `10-recomendados.png` · Ruta: `/encuentros/:id/recomendados` · Acceso: solo el organizador del encuentro · HU: HU-007

## Contenido
- **Encabezado del encuentro** (barra): etiqueta de estado, fecha, hora, duración, localidad · dirección, tipo, y a la derecha casilleros + "N de 4 · faltan M" (N = confirmados, M = 4 − confirmados).
- Título "Jugadores recomendados para este encuentro".
- Texto: "Ordenados según los criterios de compatibilidad del sistema. Solo aparecen jugadores disponibles para recibir invitaciones."
- Grilla de tarjetas, en el orden que devuelve el motor. Cada tarjeta:
  - Posición (1, 2, 3…), iniciales, nombre y localidad.
  - "NIVEL 4,5".
  - "Disponible {día abreviado} {franja que cubre el encuentro}", por ejemplo "Disponible sáb 17:00–21:00".
- No se muestra el puntaje de compatibilidad.
- Barra inferior: "Podés invitar hasta **N jugadores** para completar el encuentro." (N = lugares libres) y botón "Seleccionar e invitar" → `/encuentros/:id`.

## Datos
- La lista se pide al backend cada vez que se entra (el ranking no se guarda).
- Solo incluye candidatos que pasan los filtros y superan el umbral (ver `motor-recomendacion.md`).

## Estados
| Situación (se evalúa en este orden) | Qué se muestra |
|---|---|
| Lugares libres = 0 | sin grilla ni barra inferior; texto "No quedan lugares libres. Esperá la respuesta de las invitaciones pendientes." |
| Candidatos ≥ lugares libres | la grilla, como en la imagen |
| 0 < candidatos < lugares libres (no dibujado) | aviso amarillo arriba de la grilla: "No se encontraron suficientes participantes compatibles. Hay N jugador(es) para M lugar(es) libre(s)." y la grilla con los que haya |
| 0 candidatos | pantalla 11 |
