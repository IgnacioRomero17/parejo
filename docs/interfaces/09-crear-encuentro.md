# 09 · Crear encuentro

Imagen: `09-crear-encuentro.png` · Ruta: `/encuentros/nuevo` · Acceso: sesión + onboarding · HU: HU-006

## Contenido
- Título "Crear encuentro" y texto "Definí las condiciones. Con ellas el sistema buscará jugadores compatibles."
- Formulario a la izquierda; tarjeta "Lugares del encuentro" a la derecha.

## Campos
| Campo | Control | Validación / ayuda |
|---|---|---|
| Fecha | selector de fecha | hoy o posterior |
| Hora de inicio | desplegable (`<select>` nativo) con horas de 08:00 a 22:30 en pasos de 30 minutos (la última que permite terminar a las 23:30 con la duración mínima) | pasos de 30 minutos; si la fecha es hoy, posterior a la hora actual |
| Duración | desplegable | 60, 90 o 120 minutos |
| Localidad | desplegable (`<select>` nativo), localidades en orden alfabético | catálogo. Ayuda: "Localidad donde se jugará. El sistema la usa para calcular la distancia con cada jugador." |
| Tipo de encuentro | selector segmentado | Recreativo · Competitivo · Indiferente |
| Dirección o lugar | texto | hasta 150 caracteres. Ayuda: "Dirección o nombre del lugar. Es solo informativo: los jugadores lo ven al recibir la invitación." |

Todos obligatorios ("Completá este campo para poder guardar."). Otros errores:
- Fecha u hora pasada: "Elegí una fecha y hora futuras."
- Termina después de las 23:30: "El encuentro tiene que terminar a las 23:30 como máximo."

Valores iniciales: localidad del usuario precargada; el resto vacío.

## Tarjeta "Lugares del encuentro"
- "1 de 4 · al crear el encuentro".
- Lugar 1: "Vos · {nombre}" con "Organizador". Lugares 2 a 4: "Lugar N · por invitar".
- Nota: "Al crear el encuentro quedás registrado como participante 1. Faltan 3 lugares, que se completan con invitaciones."

## Acciones
| Elemento | Resultado |
|---|---|
| Cancelar | vuelve a `/inicio` sin guardar |
| Crear encuentro y buscar jugadores | crea el encuentro (estado Buscando participantes, organizador como participante 1) y lleva a `/encuentros/:id/recomendados` |
