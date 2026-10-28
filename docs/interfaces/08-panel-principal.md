# 08 · Panel principal

Imagen: `08-panel-principal.png` (con aviso de confirmación del onboarding) · Ruta: `/inicio` · Acceso: sesión + onboarding · HU: HU-008, HU-012

## Contenido
- Título "Hola, {nombre}" y texto "Organizá un encuentro o respondé las invitaciones que recibiste."
- Botón "+ Crear encuentro" arriba a la derecha.

## Columna izquierda · "Tus encuentros activos"
Subtítulo: "Los que organizás y aquellos a los que te invitaron y aceptaste."
Una tarjeta por encuentro **cuya fecha y hora todavía no pasaron**, ordenadas por fecha ascendente. Cada tarjeta:
- Etiquetas: estado del encuentro; "Organizás vos" o "Te invitaron"; tipo de encuentro.
- Título: "Sábado 3 de octubre · 18:00". Debajo: duración, localidad · dirección y, si no lo organiza, "Organiza {nombre}".
- Cuatro casilleros de lugares (azul = confirmado si está buscando; lima = confirmado si está completo) y "N de 4".
- Texto y acción según estado y rol:

| Estado | Rol | Texto | Acción |
|---|---|---|---|
| Buscando participantes | organizador | "confirmados · N invitación(es) pendiente(s)" | Ver seguimiento → `/encuentros/:id` |
| Buscando participantes | invitado | "confirmados" | — |
| Completo | organizador | "Listo para formar parejas." | Formar parejas → `/encuentros/:id` |
| Completo | invitado | "Esperando que {el organizador / la organizadora} inicie la formación automática de parejas." | — |
| Propuesta generada | cualquiera | "Parejas formadas." | Ver propuesta → `/encuentros/:id/propuesta` |

## Columna derecha
- **Invitaciones**: etiqueta "N pendiente(s)", la invitación pendiente más reciente ("{nombre} te invitó", fecha · hora · duración · localidad) y botón "Ver invitaciones" → `/invitaciones`. Sin pendientes: "No tenés invitaciones pendientes."
- **Tu perfil**: nivel estimado, localidad, cantidad de franjas cargadas, "Recibir invitaciones" (Disponible en verde / No disponible en gris) y enlace "Editar perfil" → `/perfil`.

## Estado vacío (no dibujado)
Sin encuentros activos: en lugar de las tarjetas, un recuadro con "Todavía no tenés encuentros" y el botón "Crear tu primer encuentro" → `/encuentros/nuevo`.
Texto debajo del título: "Creá un encuentro o aceptá una invitación para verlo acá." Ícono de calendario en círculo azul.

## Notas
- Para "el organizador / la organizadora" se usa el género del organizador; con "Prefiero no decirlo", "Esperando que se inicie la formación automática de parejas."
