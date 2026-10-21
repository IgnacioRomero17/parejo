# CLAUDE.md — parejo

## Qué es
**parejo** es una aplicación web que organiza encuentros de pádel amateur: registra nivel, disponibilidad y preferencias de los jugadores, recomienda participantes compatibles y arma parejas equilibradas (2 vs 2).
Es el prototipo de un **Trabajo Final de Graduación** (Ingeniería de Software). La pieza central es el **motor de recomendación y balanceo**; la app web existe para demostrarlo y evaluarlo.
Autor: Julio Ignacio Romero Molina. Zona del prototipo: Río Ceballos y alrededores (Córdoba, Argentina).

## Qué es obligatorio
- Las 12 historias de usuario de `docs/historias-de-usuario.md`, con sus criterios y precisiones; el modelo de `docs/`; las pantallas de `docs/interfaces/`; este archivo y `.claude/rules/`.
- **Sin extras:** no agregar funcionalidades, pantallas, campos ni tablas que no estén definidos. Si algo no está definido, **preguntar antes de inventar**.
- No existe otra documentación del proyecto en el repositorio: no buscar requisitos fuera de `docs/`.

## Stack
- **Frontend:** React + JavaScript (sin TypeScript), con Vite.
- **Backend:** Python, Django 5.2 o superior, Django REST Framework. La API es el único canal entre frontend y backend.
- **Base de datos:** PostgreSQL (sin PostGIS).
- **Correo:** SMTP, solo para recuperar la contraseña (backend de consola en desarrollo).
- Zona horaria `America/Argentina/Cordoba`. Dominio, código e interfaz en **español**.

## Arquitectura
- **Cliente-servidor con backend monolítico modular.** Una sola aplicación Django y una sola base de datos; nada de microservicios ni servicios aparte.
- **Módulos del backend:** `usuarios`, `localidades`, `encuentros` y `motor` (más `comun`, solo para utilidades compartidas como los errores). Un módulo usa a otro solo por sus servicios, nunca tocando sus tablas directamente.
- **Capas, siempre en este sentido:** vistas + serializers (formato, permisos) → servicios (reglas de negocio, transacciones) → motor (cálculos, Python puro) y modelos (datos).
- **Autenticación:** sesiones de Django con cookie y protección CSRF. Sin JWT ni tokens en el navegador.
- **Frontend:** SPA en React con React Router. Llamadas al backend con `fetch` desde `src/api/`. Usuario logueado en un contexto de React; sin Redux ni librerías de estado.
- **Ejecución:** en desarrollo, Vite y Django por separado, con Vite redirigiendo `/api` al backend. Publicado, Django sirve la API y el frontend compilado desde un único servidor.
- **No agregar dependencias** (librerías de Python o npm) sin avisar y explicar por qué hacen falta.

## Estructura del repositorio
```
parejo/
  CLAUDE.md
  .claude/rules/   # reglas por tema; cada una se carga sola al tocar sus archivos
  docs/            # requisitos: HU, modelo, esquema, pantallas, recursos (logo); no se carga sola
  backend/
    config/        # settings Django
    apps/          # usuarios, localidades, encuentros (+ comun: errores y utilidades compartidas)
    motor/         # motor de recomendación: Python puro, SIN imports de Django
    evaluacion/    # datasets, oráculo, líneas base, sensibilidad
    tests/
  frontend/
    src/
```

## Qué leer según la tarea
`docs/` no se carga automáticamente. **Leer solo lo que la tarea necesita**, nunca la carpeta entera:

| Tarea | Leer |
|---|---|
| Implementar o corregir una HU | solo la sección de esa HU en `historias-de-usuario.md` (buscar `## HU-0XX`) |
| Tocar modelos o migraciones | la clase en `modelo-clases.md` y su tabla en `esquema.sql` |
| Construir o modificar una pantalla | su `.md` en `docs/interfaces/`; la imagen `.png` solo si hace falta ver el diseño |
| Algo común a varias pantallas (barra, mensajes, etiquetas) | `docs/interfaces/README.md` |
| Motor, filtros o puntajes | nada de `docs/`: está todo en la regla del motor |

- No releer un archivo que ya se leyó en la misma sesión.
- No abrir imágenes para tareas de backend.
- Si la tarea toca varias HU, leer una por vez a medida que se avanza.

## Reglas que nunca se rompen
1. **El motor es independiente:** `backend/motor/` no importa Django ni accede a la base. Recibe datos simples y parámetros, devuelve resultados. Ni las vistas ni los modelos calculan puntajes.
2. **El motor es determinista:** misma entrada, misma salida. Todo desempate termina en el id.
3. **Parámetros en un solo lugar:** pesos, umbrales y distancias viven en `backend/motor/parametros.py`.
4. **Alcance del cálculo:** entran nivel, localidad, disponibilidad, tipo de encuentro y lado preferido. **No entran** edad, género ni frecuencia de juego.
5. **Onboarding obligatorio:** con el perfil incompleto el jugador no puede crear encuentros ni ser recomendado.
6. **El backend valida todo:** permisos, estados y datos se verifican en el servidor aunque el frontend ya los controle.
7. **Datos personales:** edad, género y localidad no se exponen más allá de lo que muestran las pantallas ni se escriben en logs.

## Fuera de alcance (no implementar)
Baja o restauración de cuentas; bloqueo por intentos fallidos; historial de contraseñas; cancelar participaciones, revocar invitaciones o reemplazar jugadores; notificaciones fuera de la app; geocodificación o distancia por ruta; avisos de bajo equilibrio; guardar copias del nivel de los jugadores en la propuesta; versión para celulares.

## Cómo trabajar
- Una HU o unidad lógica por vez, con sus tests. El ciclo de trabajo, los commits y cuándo frenar a preguntar están en `git-y-flujo-de-trabajo.md`.
- No modificar `docs/` ni `.claude/`.

## Índice de reglas (`.claude/rules/`)
| Regla | Se carga | Contiene |
|---|---|---|
| `git-y-flujo-de-trabajo.md` | siempre | commits, ramas, cuándo preguntar |
| `python.md` | al tocar `**/*.py` | estilo, nombres, tipado, linter |
| `javascript-react.md` | al tocar `frontend/**/*.{js,jsx}` | componentes, estado, llamadas a la API |
| `motor-recomendacion.md` | al tocar `backend/motor/**` | filtros, fórmulas, parámetros, desempates |
| `modelo-datos.md` | al tocar modelos y migraciones | convenciones Django para el esquema |
| `backend-api.md` | al tocar `backend/apps/**` | capas, serializers, permisos, validaciones |
| `estilo-visual.md` | al tocar `frontend/src/**` | colores, tipografías, componentes |
| `accesibilidad.md` | al tocar `frontend/src/**` | contraste, teclado, etiquetas, errores |
| `textos-ui.md` | al tocar `frontend/src/**` | español rioplatense, tono, mensajes |
| `testing.md` | al tocar tests | qué testear y cómo |
| `evaluacion.md` | al tocar `backend/evaluacion/**` | datasets, semilla, métricas |
