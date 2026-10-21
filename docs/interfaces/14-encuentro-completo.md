# 14 · Encuentro completo

Imagen: `14-encuentro-completo.png` (con aviso de la última aceptación) · Ruta: `/encuentros/:id` cuando el estado es Completo · Acceso: solo el organizador · HU: HU-008, HU-009

## Contenido
- "SEGUIMIENTO DEL ENCUENTRO" y título "¡Encuentro completo!".
- Bloque oscuro: etiqueta Completo, "4 de 4 jugadores confirmados", cuatro casilleros lima; tarjetas de los 4 jugadores (iniciales, nombre, "Nivel 4,5"; el organizador dice "Vos · Nivel 4,5"); fila con fecha, hora, duración, localidad · dirección y tipo.
- Tarjeta "Formar parejas equilibradas" con el texto: "Al presionar el botón, el sistema evalúa las 3 combinaciones posibles de 2 parejas con los 4 jugadores y selecciona automáticamente la de mejor resultado de equilibrio. Vos no armás las parejas." y botón **habilitado** "Formar parejas equilibradas".
- Panel derecho "Invitaciones enviadas": cada invitado con su estado, y la nota "Los demás participantes ven el encuentro como “Completo” hasta que inicies la formación de parejas."

## Acciones
| Elemento | Resultado |
|---|---|
| Formar parejas equilibradas | lleva a `/encuentros/:id/formando` (pantalla 15), que dispara la evaluación |

## Notas
- El aviso "{nombre} aceptó tu invitación." que aparece en la imagen no se implementa (no hay notificaciones).
- Si el encuentro ya tiene propuesta, esta ruta redirige a `/encuentros/:id/propuesta`.
