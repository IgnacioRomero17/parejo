# 07a · Onboarding · Paso 1 de 2 · Perfil deportivo

Imagen: `07a-onboarding-perfil.png` (muestra un campo con error y el nivel 4,5 elegido) · Ruta: `/onboarding/perfil` · Acceso: sesión · HU: HU-004

## Contenido
- Barra superior solo con el logo.
- "PRIMER INGRESO · PASO 1 DE 2" y "Perfil deportivo" a la derecha; barra de progreso al 50 %.
- Título "Configurá tu perfil deportivo" y texto "Tu nivel y tu localidad se usan para recomendarte a otros organizadores y para formar parejas equilibradas."

## Campos
| Campo | Control | Validación |
|---|---|---|
| Edad | número entero | 18 a 99. Error: "Ingresá una edad entre 18 y 99." |
| Género | desplegable | Masculino, Femenino, Prefiero no decirlo |
| Localidad | desplegable (`<select>` nativo), localidades en orden alfabético | catálogo de localidades. Ayuda: "Elegila del listado. Si la tuya no figura, elegí la más cercana." |
| Frecuencia de juego | desplegable | Menos de 1 vez por semana, 1 vez por semana, 2 o 3 veces por semana, 4 o más veces por semana |
| Nivel estimado | selector de nivel (ver abajo) | 1,0 a 7,0 en pasos de 0,5 |

Todos obligatorios. Campo vacío al guardar: borde rojo + "Completá este campo para poder guardar." Los desplegables arrancan en "Seleccioná una opción".

## Selector de nivel
- Barra horizontal con los niveles 1 a 7 como puntos numerados y los medios puntos como puntos chicos entre ellos. Extremos rotulados "Iniciación" y "Élite".
- **Arranca vacío**: sin valor, sin etiqueta flotante, y en la zona de descripciones el texto "Deslizá para ver qué describe cada nivel."
- Al mover el control se actualizan **en vivo**: la etiqueta flotante con el valor ("4,5"), la parte azul de la barra y las descripciones.
- Valor entero: una descripción. Valor con ,5: dos descripciones lado a lado (nivel inferior y superior).
- Debajo, siempre: "Elegí el nivel que mejor describa cómo jugás hoy, no el que aspirás a tener. Si dudás entre dos, elegí el menor."
- Se implementa sobre un `<input type="range" min="1" max="7" step="0.5">` con estilo propio. Como un `range` nativo siempre tiene valor, el componente guarda aparte el estado "sin elegir" (`valor = null`): mientras es null, el control se muestra sin la marca del valor, sin parte azul ni etiqueta flotante, con `aria-valuetext="Sin elegir"`, y el formulario lo trata como campo vacío. El primer clic, toque o tecla fija el valor.

| Nivel | Nombre | Descripción |
|---|---|---|
| 1 | Iniciación | Recién empezás: aprendés los golpes y las reglas básicas. |
| 2 | Principiante | Mantenés peloteos cortos y empezás a usar las paredes. |
| 3 | Intermedio bajo | Sostenés el peloteo, pero la volea y la bandeja todavía fallan. |
| 4 | Intermedio | Controlás los golpes básicos, jugás bien las paredes y entendés el juego en pareja. |
| 5 | Intermedio alto | Ejecutás casi todos los golpes con consistencia y construís los puntos. |
| 6 | Avanzado | Jugás con potencia, táctica y poco error. Competís en torneos. |
| 7 | Élite | Nivel profesional o de competición de alto rendimiento. |

## Pie
- A la izquierda, contador de pendientes: "1 campo pendiente" / "N campos pendientes"; si no falta nada, no se muestra.
- Botón "Guardar y continuar": valida en el backend, guarda y lleva a `/onboarding/disponibilidad`.

## Notas
- No hay forma de saltear este paso ni de volver a la bienvenida.
