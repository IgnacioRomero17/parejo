# Interfaces — prototipo parejo

Cada pantalla tiene una imagen (`.png`) y una descripción (`.md`) con el mismo nombre. **La descripción manda**: la imagen muestra cómo se ve; el `.md` define campos, validaciones, acciones y estados, incluidos los que no están dibujados.

- Los nombres, fechas y lugares de las imágenes (Tomás Ríos, Valentina Sosa, sábado 3 de octubre, etc.) son **datos de ejemplo**. Nada de eso se escribe fijo en el código.
- Colores, tipografías y componentes: ver `.claude/rules/estilo-visual.md`. Tono de los textos: `.claude/rules/textos-ui.md`.
- Las reglas de negocio están en `docs/historias-de-usuario.md`; las descripciones solo las referencian.

## Índice

| # | Pantalla | Ruta sugerida | HU | Acceso |
|---|---|---|---|---|
| 05 | [Bienvenida](05-bienvenida.md) | `/` | — | pública |
| 06a | [Registro](06a-registro.md) | `/registro` | HU-001 | pública |
| 06b | [Inicio de sesión](06b-inicio-sesion.md) | `/ingresar` | HU-002 | pública |
| 06c | [Recuperación · correo](06c-recuperacion-correo.md) | `/recuperar` | HU-003 | con o sin sesión |
| 06d | [Recuperación · enviado](06d-recuperacion-enviado.md) | `/recuperar/enviado` | HU-003 | con o sin sesión |
| 06e | [Recuperación · nueva contraseña](06e-recuperacion-nueva.md) | `/recuperar/:uid/:token` | HU-003 | con o sin sesión (enlace del correo) |
| 07a | [Onboarding · perfil deportivo](07a-onboarding-perfil.md) | `/onboarding/perfil` | HU-004 | sesión |
| 07b | [Onboarding · disponibilidad](07b-onboarding-disponibilidad.md) | `/onboarding/disponibilidad` | HU-005 | sesión |
| 08 | [Panel principal](08-panel-principal.md) | `/inicio` | HU-008, HU-012 | sesión + onboarding |
| 09 | [Crear encuentro](09-crear-encuentro.md) | `/encuentros/nuevo` | HU-006 | sesión + onboarding |
| 10 | [Jugadores recomendados](10-recomendados.md) | `/encuentros/:id/recomendados` | HU-007 | organizador |
| 11 | [Sin participantes compatibles](11-sin-compatibles.md) | (estado de la 10) | HU-007 | organizador |
| 12 | [Seleccionar e invitar](12-seleccionar-invitar.md) | `/encuentros/:id` | HU-008 | organizador |
| 13 | [Bandeja de invitaciones](13-bandeja-invitaciones.md) | `/invitaciones` | HU-008 | sesión + onboarding |
| 14 | [Encuentro completo](14-encuentro-completo.md) | `/encuentros/:id` (estado completo) | HU-008, HU-009 | organizador |
| 15 | [Pantalla de carga](15-carga.md) | `/encuentros/:id/formando` | HU-009, HU-010 | organizador |
| 16 | [Propuesta de encuentro](16-propuesta.md) | `/encuentros/:id/propuesta` | HU-011, HU-012 | participantes |
| 17 | [Perfil del usuario](17-perfil.md) | `/perfil` | HU-004, HU-005 | sesión + onboarding |

"Sesión + onboarding": requiere sesión iniciada y onboarding completo; si falta, se redirige al paso pendiente.

## Elementos comunes

**Barra superior (pantallas con sesión y onboarding completo)**
- Logo "parejo" a la izquierda: lleva a `/inicio`.
- Enlaces: Inicio, Crear encuentro, Invitaciones, Perfil. El activo se marca con una línea lima debajo.
- "Invitaciones" muestra un indicador con la cantidad de invitaciones pendientes; si es 0, no se muestra.
- En el onboarding la barra muestra solo el logo, sin enlaces.

**Pantallas de acceso (05 a 06e)**
- Bienvenida: fondo oscuro de página completa.
- Registro, inicio de sesión y recuperación: panel oscuro a la izquierda (logo, ilustración de cancha, título y texto) y formulario a la derecha.

**Desplegables**
- Todos los desplegables (localidad, género, frecuencia, duración, día) son `<select>` nativos con estilo propio. Las imágenes muestran una lupa en el campo de localidad: no se implementa búsqueda.

**Mensajes**
- Error de campo: borde rojo en el campo y mensaje debajo con ícono de alerta.
- Error general del formulario: recuadro rojo claro arriba del formulario.
- Confirmación: aviso flotante oscuro arriba a la derecha, con ícono de check lima; desaparece solo a los pocos segundos.
- Campo obligatorio vacío: "Completá este campo para poder guardar."

**Estados de encuentro (etiquetas)**: Buscando participantes (azul), Completo (lima), Propuesta generada (lima).
**Estados de invitación (etiquetas)**: Pendiente (amarillo), Aceptada (verde), Rechazada (rojo).
**Formato de fechas**: "Sábado 3 de octubre · 18:00" en títulos; "Sáb 3 oct 2026" en encabezados compactos. Niveles con coma decimal ("4,5").
