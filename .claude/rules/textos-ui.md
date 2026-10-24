---
paths:
  - "frontend/src/**"
---

# Textos de la interfaz

## Fuente de los textos
- Los textos de cada pantalla están en `docs/interfaces/` y los mensajes de error en `docs/historias-de-usuario.md`. **Se copian tal cual**, sin reformular.
- Si hace falta un texto que no está definido, escribirlo siguiendo esta regla y mencionarlo al terminar la tarea para que el autor lo revise.

## Voz y tono
- Español rioplatense con **voseo**: "Creá", "Elegí", "Completá", "Ingresá", "Revisá", "Tenés", "Podés". Nunca "tú" ni "usted".
- Cercano y directo, sin jerga técnica: "No se encontraron suficientes participantes compatibles", no "Error 404" ni "query vacía".
- Frases cortas. Lo importante primero.
- Sin emojis, signos de exclamación solo en logros ("¡Encuentro completo!").

## Formato
- Mayúscula solo al inicio y en nombres propios: "Crear encuentro", "Jugadores recomendados" (no "Crear Encuentro").
- Botones con verbo en infinitivo que dice lo que pasa: "Guardar y continuar", "Enviar invitación (1)", "Formar parejas equilibradas". Evitar "Aceptar"/"OK" genéricos.
- Mensajes de error: qué pasó y, si se puede, qué hacer, con punto final: "Este correo ya está registrado.", "Completá este campo para poder guardar."
- Avisos de confirmación en pasado, con punto: "Cambios guardados correctamente."
- Rótulos en mayúsculas solo con el estilo de rótulo (CSS `text-transform`); en el código se escriben normal.
- Números: coma decimal ("4,5", "1,00"); "N de 4"; minutos como "90 minutos" en títulos y "90 min" en datos compactos.
- Fechas: "Sábado 3 de octubre · 18:00" en títulos, "Sáb 3 oct 2026" en encabezados y listas; horas en 24 h ("18:00").
- Plurales correctos según la cantidad: "1 lugar libre" / "2 lugares libres", "1 invitación pendiente" / "3 invitaciones pendientes".
- Género: todo texto que se refiera a una persona concreta usa el género de su perfil ("la organizadora", "quedás registrada"). Con "Prefiero no decirlo", o en textos generales, se usa una forma neutra, reformulando la frase si hace falta ("Esperando que se inicie la formación de parejas").

## Glosario (usar siempre estos términos)
| Usar | No usar |
|---|---|
| encuentro | partido, match, juego (salvo en la bienvenida, que usa "partido") |
| organizador / organizadora | creador, admin, host |
| jugador / jugadores | usuario (en textos visibles) |
| invitación · aceptar · rechazar | solicitud, request, declinar |
| participante confirmado | inscripto, miembro |
| jugadores recomendados · compatibles | sugeridos, matches |
| pareja · combinación | equipo, team |
| propuesta de encuentro | resultado final, fixture |
| resultado de equilibrio | score, rating |
| nivel estimado | ranking, categoría |
| franja (horaria) | slot, turno |
| Drive · Revés · Indiferente | derecha, izquierda, revés sin tilde |
| Recreativo · Competitivo · Indiferente | amistoso, serio |
| localidad | ciudad, zona |
