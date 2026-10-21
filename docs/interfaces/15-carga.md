# 15 · Pantalla de carga

Imagen: `15-carga.png` · Ruta: `/encuentros/:id/formando` · Acceso: solo el organizador · HU: HU-009, HU-010

## Contenido
- "PROCESAMIENTO AUTOMÁTICO" y título "Generando una propuesta equilibrada".
- Nombres de los 4 participantes separados por " · ".
- Ilustración de cancha con el avatar del organizador en una posición y "?" en las otras tres, y un indicador de carga en el centro.
- "Paso N de 3", barra de progreso y "Esto puede tardar unos segundos".
- Lista de pasos, cada uno con estado Listo / En curso / En espera:
  1. "Evaluando las 3 combinaciones posibles"
  2. "Formando parejas equilibradas"
  3. "Generando la propuesta de encuentro"
- Pie: "La propuesta se abrirá automáticamente al terminar."

## Comportamiento
- Al entrar, el frontend llama **una vez** al endpoint que evalúa combinaciones, forma parejas y genera la propuesta en una sola transacción.
- Los tres pasos son una animación: avanzan en secuencia durante un mínimo de 1,5 segundos en total, aunque el backend responda antes.
- Al terminar la animación y llegar la respuesta, redirige a `/encuentros/:id/propuesta`.
- Si el backend devuelve error: se reemplaza la lista por "No pudimos generar la propuesta. Intentá de nuevo." con botón "Reintentar" y enlace "Volver al encuentro".
- Si el encuentro ya tiene propuesta, redirige directamente a la propuesta sin volver a evaluar.
