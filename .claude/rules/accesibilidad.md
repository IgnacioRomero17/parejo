---
paths:
  - "frontend/src/**"
---

# Accesibilidad básica

Objetivo: **buenas prácticas básicas**, no una certificación. Se cumplen escribiendo HTML correcto y usando controles nativos; no requieren librerías ni componentes especiales. Si alguna de estas prácticas complica una tarea, avisar en lugar de saltearla o de construir algo complejo.

## HTML
- `<html lang="es-AR">`. Cada ruta cambia el título de la pestaña: "Crear encuentro · parejo".
- Etiquetas semánticas: `header`, `nav`, `main`; un `h1` por pantalla; listas con `ul`/`li`; la tabla de combinaciones con `table` y `th`.
- Botones con `<button>` y navegación con `<a>` / `Link`. Nunca un `div` con `onClick`.

## Controles: siempre nativos, con estilo propio
| Control | Elemento |
|---|---|
| Campos de texto, email, contraseña, número, fecha | `<input>` del tipo correspondiente |
| Desplegables (localidad, género, frecuencia, duración, día, hora en pasos de 30 minutos, de 08:00 a 23:30) | `<select>` |
| Selector de nivel | `<input type="range" min="1" max="7" step="0.5">` |
| Selectores segmentados (tipo de encuentro, lado) | grupo de `<input type="radio">` dentro de `fieldset` con `legend` |
| Interruptor "Disponible para recibir invitaciones" | `<input type="checkbox">` |
| Selección de jugadores a invitar | `<input type="checkbox">` |

Los elementos nativos ya funcionan con teclado y lectores de pantalla; el estilo se aplica encima con CSS. No reemplazarlos por versiones hechas a mano.

## Formularios
- Cada campo con su `<label>` asociada (`htmlFor` / `id`).
- Campo con error: `aria-invalid="true"` y el mensaje de error enlazado con `aria-describedby`.
- Error general del formulario (por ejemplo, credenciales inválidas): `role="alert"`.

## Teclado y foco
- Todo lo que se hace con el mouse se puede hacer con el teclado.
- El foco siempre visible: contorno de 2px en `--azul`. Nunca `outline: none` sin reemplazo.
- En celular, zonas táctiles de al menos 44px de alto.

## Contenido
- Usar solo los colores de `estilo-visual.md`.
- No transmitir información solo con color: las etiquetas de estado llevan texto, los casilleros van con "N de 4" y los errores con ícono y mensaje.
- Íconos decorativos con `aria-hidden="true"`; un botón que solo tiene un ícono lleva `aria-label`.
- El logo de la barra con `alt="parejo"`; ilustraciones decorativas con `alt=""`.
