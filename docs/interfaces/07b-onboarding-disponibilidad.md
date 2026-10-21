# 07b · Onboarding · Paso 2 de 2 · Disponibilidad y preferencias

Imagen: `07b-onboarding-disponibilidad.png` · Ruta: `/onboarding/disponibilidad` · Acceso: sesión con paso 1 completo · HU: HU-005

## Contenido
- "PRIMER INGRESO · PASO 2 DE 2" y "Disponibilidad y preferencias"; barra de progreso completa.
- Título "¿Cuándo y cómo te gusta jugar?" y texto "El sistema usa tus franjas y preferencias para determinar si sos compatible con un encuentro."

## Tarjeta "Disponibilidad horaria"
- Una fila por franja: Día (desplegable lunes a domingo), Desde y Hasta (horas en pasos de 30 minutos), enlace "Quitar".
- Botón "Agregar franja": agrega una fila vacía.
- Arranca con una fila vacía.
- Errores por fila:
  - "La hora de fin debe ser posterior a la de inicio."
  - "La franja debe durar al menos 60 minutos."
- Al guardar, las franjas superpuestas o contiguas del mismo día se unen; al volver a esta pantalla o al perfil se ven ya unidas.

## Tarjeta de preferencias
| Campo | Control | Opciones | Obligatorio |
|---|---|---|---|
| Tipo de encuentro | selector segmentado | Recreativo · Competitivo · Indiferente | sí |
| Lado preferido | selector segmentado | Drive · Revés · Indiferente | sí |
Ninguna opción viene marcada al entrar.

## Tarjeta "Disponible para recibir invitaciones"
- Interruptor, **apagado** al entrar.
- Texto: "Permite que el sistema te recomiende a otros organizadores. No te suma a ningún encuentro: solo participás si aceptás una invitación."
- Si se enciende sin franjas cargadas, al guardar: "Para recibir invitaciones necesitás cargar al menos una franja."

## Acciones
| Elemento | Resultado |
|---|---|
| Volver | `/onboarding/perfil` con los datos ya guardados |
| Guardar | valida en el backend, guarda y lleva a `/inicio` con el aviso "Disponibilidad y preferencias guardadas correctamente." |

## Notas
- Se puede terminar el onboarding sin franjas y con el interruptor apagado: el jugador entra a la app pero no aparece en recomendaciones.
