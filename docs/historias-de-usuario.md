# Historias de usuario — prototipo parejo

Fuente de verdad de **qué** debe hacer el prototipo. Contiene solo lo que se implementa en el prototipo.

Cómo leer cada historia:
- **Criterios de aceptación**: los del documento del TFG, adaptados al prototipo. Son obligatorios.
- **Precisiones del prototipo**: decisiones posteriores que completan los criterios. También son obligatorias.
- **Pantallas**: ilustrativos en `docs/interfaces/`.
- Las fórmulas, filtros y parámetros del motor están en `.claude/rules/motor-recomendacion.md`; acá solo se nombran.
- Si algo no está definido acá ni en las reglas, **preguntar antes de implementar**.

## Roles

No hay tipos de cuenta. Todo usuario registrado es **Jugador** y pasa a ser **Organizador** solo de los encuentros que crea.

| Acción | Jugador | Organizador |
|---|---|---|
| Gestionar sus propios datos, perfil, disponibilidad y preferencias | Sí | Sí |
| Crear un encuentro | Sí | Sí |
| Ver recomendaciones y enviar invitaciones | No | Sí, de sus encuentros |
| Aceptar o rechazar invitaciones recibidas | Sí | Sí |
| Iniciar la formación de parejas equilibradas | No | Sí, de sus encuentros |
| Ver la propuesta del encuentro | Solo si participa | Sí, de sus encuentros |
| Ver o modificar datos de otros usuarios | No | No |

Toda acción se valida en el backend; ocultar un botón en el frontend no alcanza.

## Flujo general

Bienvenida → registro → onboarding paso 1 (HU-004) → onboarding paso 2 (HU-005) → panel principal → crear encuentro (HU-006) → recomendados (HU-007) → invitar (HU-008) → 4 confirmados → formar parejas (HU-009, HU-010) → propuesta (HU-011, HU-012).

Estados del encuentro: `CREADO` → `BUSCANDO_PARTICIPANTES` → `COMPLETO` → `PROPUESTA_GENERADA`.

---

## HU-001 · Registro del usuario

**Como** usuario, **quiero** registrarme en la plataforma web **para** crear una cuenta que me permita acceder a encuentros equilibrados de pádel.

Pantallas: 05 Bienvenida, 06a Registro.

**Criterios de aceptación**
1. Dado un correo electrónico que ya está registrado, cuando el usuario lo ingresa, el sistema muestra el error "Este correo ya está registrado."
2. Dada una contraseña que no cumple la política, cuando el usuario la ingresa, el sistema le avisa la restricción: "La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número."
3. Dado un campo incompleto, cuando el usuario intenta registrarse, el sistema avisa que todos los campos son requeridos.

**Precisiones del prototipo**
- Campos: nombre, apellido, correo electrónico y contraseña. Todos obligatorios.
- Política de contraseña: entre 8 y 64 caracteres, con al menos una letra y un número; se permiten otros caracteres.
- El correo es el identificador de inicio de sesión, es único y se guarda en minúsculas.
- La contraseña se guarda con el hasher por defecto de Django; nunca en texto plano.
- Después de registrarse, el usuario entra directamente al onboarding paso 1.

---

## HU-002 · Ingreso del usuario

**Como** usuario registrado, **quiero** iniciar sesión **para** acceder a las funcionalidades.

Pantallas: 06b Inicio de sesión.

**Criterios de aceptación**
1. Dado un usuario registrado, cuando ingresa correo y contraseña correctos, accede a su cuenta.
2. Dada una contraseña incorrecta, cuando intenta ingresar, el sistema muestra "Las credenciales ingresadas no son válidas."
3. Dado un correo no registrado, cuando intenta ingresar, el sistema muestra el mismo mensaje del criterio 2.

**Precisiones del prototipo**
- Si el usuario no terminó el onboarding, al ingresar va al paso que le falta, no al panel principal.
- Las pantallas internas requieren sesión iniciada; sin sesión se redirige al inicio de sesión.

---

## HU-003 · Recuperación de contraseña

**Como** usuario, **quiero** recuperar mi contraseña si la olvidé **para** acceder nuevamente a la plataforma.

Pantallas: 06c Paso 1, 06d Paso 2, 06e Paso 3.

**Criterios de aceptación**
1. Dado un usuario registrado, cuando selecciona "¿Olvidaste tu contraseña?" e ingresa su correo, recibe un correo con un enlace para restablecerla.
2. Dado un correo no registrado, cuando intenta recuperar la contraseña, el sistema muestra "La cuenta no existe. Revisá el correo ingresado."
3. Dado que sigue el enlace del correo, cuando define una nueva contraseña, puede iniciar sesión con ella.

**Precisiones del prototipo**
- Paso 1: ingresar correo. Paso 2: "Revisá tu correo". Paso 3: definir la nueva contraseña.
- La nueva contraseña cumple la misma política de HU-001.
- El enlace usa el mecanismo de tokens de Django y deja de servir una vez usado.
- El correo se envía por SMTP; en desarrollo se usa el backend de consola de Django.
- "Guardar e iniciar sesión" guarda la contraseña e inicia la sesión.

---

## HU-004 · Configuración del perfil deportivo

**Como** usuario, **quiero** configurar mi perfil deportivo **para** que el sistema disponga de información sobre mí para generar recomendaciones.

Pantallas: 07a Onboarding paso 1, 17 Perfil.

**Criterios de aceptación**
1. Dado que faltan uno o más datos requeridos, cuando el jugador intenta guardar, el sistema impide el guardado e indica los campos pendientes.
2. Dado un valor que no cumple las condiciones del dato, cuando intenta guardar, el sistema impide el guardado y solicita la corrección.
3. Dado un perfil ya registrado, cuando el jugador modifica datos y guarda, el sistema actualiza la información.

**Precisiones del prototipo**
- Datos requeridos: edad, género, localidad, frecuencia de juego y nivel estimado.
- Edad: número entero entre 18 y 99. Menores de 18 no pueden completar el perfil (la app organiza encuentros presenciales entre desconocidos).
- Género: Masculino, Femenino o Prefiero no decirlo.
- Frecuencia de juego: Menos de 1 vez por semana, 1 vez por semana, 2 o 3 veces por semana, 4 o más veces por semana.
- Localidad: se elige de un desplegable con el catálogo cerrado de localidades. Si la del jugador no está, elige la más cercana.
- Nivel estimado: de 1,0 a 7,0 en pasos de 0,5. Selector tipo barra que **arranca vacío** en el primer ingreso; al moverlo se actualizan en vivo el valor y las descripciones (una descripción si el valor es entero, dos si termina en ,5).
- Edad, género y frecuencia se guardan pero **no se usan** en el cálculo del motor.
- El onboarding no se puede saltear. Mientras el perfil esté incompleto, el jugador no puede crear encuentros ni ser recomendado.
- Un cambio de perfil afecta las recomendaciones futuras, no las invitaciones ya enviadas.

---

## HU-005 · Registro de disponibilidad y preferencias

**Como** jugador, **quiero** registrar mi disponibilidad, mis preferencias y mi disposición para recibir invitaciones **para** que el sistema las considere al determinar participantes compatibles.

Pantallas: 07b Onboarding paso 2, 17 Perfil.

**Criterios de aceptación**
1. Dado que el jugador configura su perfil, cuando registra días, horarios y preferencias, el sistema los almacena asociados a su perfil.
2. Dado que indica que está disponible para recibir invitaciones, el sistema registra esa condición y lo considera candidato para nuevos encuentros.
3. Dado que está disponible, cuando cambia a no disponible, el sistema actualiza su estado y deja de considerarlo para nuevas invitaciones.
4. Dada información ya registrada, cuando la modifica y guarda, el sistema la actualiza.

**Precisiones del prototipo**
- Franja de disponibilidad: día de la semana, hora desde y hora hasta. La hora hasta debe ser mayor que la hora desde; una franja no cruza la medianoche.
- Horarios en pasos de 30 minutos (:00 y :30).
- Cada franja dura como mínimo 60 minutos (el encuentro más corto). Si dura menos, se impide el guardado: "La franja debe durar al menos 60 minutos."
- Se pueden cargar varias franjas ("Agregar franja") y quitarlas ("Quitar"), sin límite de cantidad.
- Al guardar, las franjas del mismo día que se superponen o se tocan se unen en una sola (17:00–19:00 y 18:30–21:00 quedan 17:00–21:00; 17:00–19:00 y 19:00–21:00 quedan 17:00–21:00). La pantalla muestra el resultado ya unido. Motivo: el motor exige que una sola franja cubra el encuentro completo.
- Para estar disponible hace falta al menos una franja. Si el jugador activa "Disponible para recibir invitaciones" sin franjas, o quita la última estando disponible, se impide el guardado: "Para recibir invitaciones necesitás cargar al menos una franja."
- Tipo de encuentro preferido: Recreativo, Competitivo o Indiferente.
- Lado preferido: Drive, Revés o Indiferente.
- "Disponible para recibir invitaciones" está desactivado hasta que el jugador lo active en este paso.
- Dejar de estar disponible no cancela invitaciones ya recibidas ni participaciones confirmadas.

---

## HU-006 · Creación de encuentro

**Como** usuario, **quiero** crear un encuentro indicando las condiciones en las que deseo jugar **para** que el sistema busque participantes compatibles.

Pantallas: 08 Panel principal, 09 Crear encuentro.

**Criterios de aceptación**
1. Dado un usuario con perfil configurado, cuando completa las condiciones y confirma, el sistema crea el encuentro y lo deja listo para buscar participantes.
2. Dado que faltan condiciones requeridas, cuando intenta crear el encuentro, el sistema lo impide e indica la información faltante.
3. Dado un encuentro creado correctamente, el sistema muestra y registra sus condiciones.

**Precisiones del prototipo**
- Condiciones requeridas: fecha, hora de inicio, duración, localidad (del catálogo), dirección o lugar y tipo de encuentro (Recreativo, Competitivo o Indiferente).
- Hora de inicio en pasos de 30 minutos (:00 y :30).
- Duración: 60, 90 o 120 minutos.
- No se puede crear un encuentro con fecha y hora de inicio en el pasado, ni con fecha posterior a los próximos 60 días.
- La dirección o lugar es solo informativa; el cálculo de distancia usa la localidad.
- El encuentro empieza a las 08:00 como mínimo y termina a las 23:30 como máximo (inicio + duración). Las franjas, en pasos de 30 minutos, van de 08:00 a 23:30.
- El organizador queda registrado como primer participante confirmado (1 de 4).
- Al crearse, el encuentro pasa a `BUSCANDO_PARTICIPANTES` y se muestran los jugadores recomendados.

---

## HU-007 · Recomendación de jugadores compatibles

**Como** organizador, **quiero** recibir recomendaciones de jugadores compatibles con mi encuentro **para** elegir a quiénes invitar.

Pantallas: 10 Jugadores recomendados, 11 Sin participantes compatibles.

**Criterios de aceptación**
1. Dado un encuentro creado, cuando el sistema procesa a los jugadores registrados, genera una lista de recomendados.
2. Al generar las recomendaciones, el sistema aplica los criterios de compatibilidad definidos.
3. Si hay varios compatibles, el sistema los ordena según el puntaje de compatibilidad.
4. Si no hay suficientes jugadores compatibles, el sistema informa "No se encontraron suficientes participantes compatibles".

**Precisiones del prototipo**
- Filtros, puntaje (0 a 1), umbral mínimo, orden y desempates: ver `motor-recomendacion.md`.
- "Suficientes" significa al menos tantos candidatos como lugares libres. Lugares libres = 4 − confirmados − invitaciones pendientes.
- Si hay menos candidatos que lugares libres, se muestra el aviso y, aun así, los candidatos que haya.
- El nivel de referencia es el promedio de los participantes confirmados (incluye al organizador).
- El ranking se recalcula en cada consulta; no se guarda.
- Solo el organizador del encuentro ve sus recomendaciones.

---

## HU-008 · Selección e invitación de participantes

**Como** organizador, **quiero** seleccionar jugadores recomendados y enviarles invitaciones **para** completar el grupo.

Pantallas: 12 Seleccionar e invitar, 13 Bandeja de invitaciones, 14 Jugadores confirmados.

**Criterios de aceptación**
1. Cuando el organizador selecciona jugadores recomendados y envía la invitación, el sistema registra cada invitación como pendiente y asociada al encuentro.
2. Cuando un jugador invitado entra a sus invitaciones, ve la información del encuentro y las opciones aceptar y rechazar.
3. Cuando acepta o rechaza, el sistema actualiza el estado de la invitación y, si acepta, lo incorpora como participante confirmado.

**Precisiones del prototipo**
- Estados de invitación: Pendiente, Aceptada, Rechazada.
- El organizador no puede seleccionar más jugadores que lugares libres.
- Un jugador no puede ser invitado dos veces al mismo encuentro, aunque haya rechazado.
- Al llegar a 4 confirmados, el encuentro pasa a `COMPLETO`.
- No se pueden revocar invitaciones ni cancelar una participación confirmada.
- Una vez pasada la fecha y hora de inicio del encuentro, no se puede invitar, aceptar, rechazar ni formar parejas ("Este encuentro ya comenzó.").

---

## HU-009 · Evaluación automática de combinaciones

**Como** organizador, **quiero** que el sistema evalúe las combinaciones posibles de los cuatro confirmados **para** determinar cuáles forman un encuentro equilibrado.

Pantallas: 14 Jugadores confirmados, 15 Pantalla de carga.

**Criterios de aceptación**
1. Con cuatro participantes confirmados, cuando el organizador selecciona "Formar parejas equilibradas", el sistema inicia la evaluación.
2. Al evaluar, el sistema genera y analiza las combinaciones válidas de dos parejas con los cuatro participantes, sin repetir ni excluir jugadores.

**Precisiones del prototipo**
- El botón se habilita solo con exactamente 4 confirmados y solo para el organizador.
- Hay exactamente 3 combinaciones posibles. Fórmula de equilibrio: ver `motor-recomendacion.md`.
- Se guardan las 3 combinaciones con su puntaje.
- La pantalla de carga dura un mínimo breve para que no parpadee y abre la propuesta al terminar.

---

## HU-010 · Formación automática de parejas equilibradas

**Como** organizador, **quiero** que el sistema forme dos parejas equilibradas **para** obtener la conformación que mejor cumpla los criterios.

Pantallas: 15 Pantalla de carga, 16 Propuesta.

**Criterios de aceptación**
1. Al terminar la evaluación, el sistema selecciona la combinación con mejor resultado de equilibrio.
2. Cada participante pertenece a una única pareja y ninguno queda excluido.
3. El resultado son dos parejas de dos jugadores cada una.

**Precisiones del prototipo**
- Ante empate se aplican los desempates de `motor-recomendacion.md`; el resultado es determinista.

---

## HU-011 · Generación de propuesta

**Como** usuario, **quiero** obtener una propuesta de encuentro con los participantes y las parejas **para** disponer del resultado del emparejamiento.

Pantallas: 16 Propuesta.

**Criterios de aceptación**
1. Al determinarse las parejas, el sistema genera una propuesta de encuentro.
2. La propuesta incluye fecha, horario y ubicación del encuentro.
3. La propuesta asocia los cuatro participantes y la pareja de cada uno.

**Precisiones del prototipo**
- La propuesta apunta a la combinación elegida, que guarda el puntaje de equilibrio (0 a 1, cuatro decimales).
- Al generarse, el encuentro pasa a `PROPUESTA_GENERADA`. No se vuelve a evaluar.

---

## HU-012 · Visualización de propuesta

**Como** usuario, **quiero** ver la propuesta **para** conocer a los jugadores, las parejas y las condiciones del encuentro.

Pantallas: 16 Propuesta, 08 Panel principal.

**Criterios de aceptación**
1. Cuando un participante accede a una propuesta generada, el sistema muestra la información completa del encuentro.
2. Se muestran fecha, horario, localidad y dirección, los cuatro participantes, las dos parejas y el resultado de equilibrio.

**Precisiones del prototipo**
- Solo pueden verla los cuatro participantes.
- El resultado de equilibrio es informativo; no hay avisos de "equilibrio bajo".
- "Ver combinaciones evaluadas" muestra las 3 combinaciones con sus puntajes.
- El puntaje de equilibrio que se muestra es el guardado y no cambia. Los promedios de nivel por pareja se calculan con el nivel actual de cada jugador; si alguien modifica su nivel después de generada la propuesta, pueden no coincidir con el puntaje. Es una limitación aceptada del prototipo: no bloquear cambios de perfil ni guardar copias del nivel.

---

## Fuera del prototipo

No implementar:
- Dar de baja una cuenta ni restaurar una cuenta dada de baja.
- Bloqueo temporal por intentos fallidos, historial de contraseñas, respaldos y monitoreo.
- Cancelar participaciones, revocar invitaciones, reemplazar jugadores.
- Avisos o notificaciones fuera de la aplicación (salvo el correo de recuperación).
