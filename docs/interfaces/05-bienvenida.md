# 05 · Bienvenida

Imagen: `05-bienvenida.png` · Ruta: `/` · Acceso: pública · HU: —

## Propósito
Primera pantalla. Presenta la app y lleva a crear cuenta o iniciar sesión.

## Contenido
- Encabezado: logo "parejo" y enlace "Iniciar sesión" a la derecha.
- Etiqueta "Pádel amateur · 2 contra 2".
- Título: "Partidos parejos, con parejas equilibradas."
- Texto: "Creá un encuentro, recibí recomendaciones de jugadores compatibles y dejá que el sistema forme las parejas."
- Ilustración del logo a la derecha.
- Tres tarjetas de pasos:
  1. "Creá tu encuentro" — "Definí fecha, hora, duración y ubicación del partido que querés jugar."
  2. "Invitá jugadores recomendados" — "El sistema sugiere jugadores compatibles por nivel, horario y preferencias."
  3. "Recibí parejas equilibradas" — "Con 4 confirmados, el sistema evalúa las combinaciones y arma las parejas."

## Acciones
| Elemento | Resultado |
|---|---|
| Crear cuenta | `/registro` |
| Ya tengo cuenta · Iniciar sesión | `/ingresar` |

## Notas
- Si el usuario ya tiene sesión iniciada, se redirige a `/inicio` (o al paso de onboarding pendiente).
