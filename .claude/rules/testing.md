---
paths:
  - "backend/tests/**"
  - "backend/conftest.py"
  - "frontend/src/**/*.test.{js,jsx}"
---

# Testing

## Backend
- **pytest** + **pytest-django** (+ `pytest-cov` para medir cobertura). Configuración en `backend/pyproject.toml`.
- Base de datos de test **PostgreSQL**, nunca SQLite: las restricciones `CHECK` y la clave compuesta deben comportarse igual que en producción.
- Estructura espejo de las apps: `tests/motor/`, `tests/usuarios/`, `tests/encuentros/`, `tests/evaluacion/`.
- Datos de prueba con funciones fábrica propias en `backend/tests/fabricas.py` (`crear_usuario(...)`, `crear_encuentro(...)`), con valores por defecto válidos. Sin `factory_boy` ni fixtures JSON.

### Qué testear en cada capa
| Capa | Qué |
|---|---|
| Motor | lo que exige la regla del motor (sin base de datos) |
| Servicios | **un test por criterio de aceptación** y por precisión del prototipo que tenga lógica; cambios de estado; casos de error |
| API | códigos de respuesta (200/201, 400, 401, 403, 404, 409), permisos por rol, formato de errores, rutas públicas y privadas |
| Modelos | solo las restricciones que no cubren los servicios (por ejemplo, invitación duplicada rechazada por la base) |

### Nombres
`test_hu007_c4_avisa_cuando_no_hay_suficientes`: HU, criterio (o `p` + número para una precisión) y qué verifica. Tests sin HU: `test_<tema>_<que_verifica>`.

### Reglas
- Cada test es independiente: crea sus datos y no depende del orden.
- Sin red ni servicios externos; correo con el backend `locmem` y verificación de `mail.outbox`.
- Fechas relativas a `timezone.localdate()` (por ejemplo, el próximo sábado), nunca fechas fijas que con el tiempo queden en el pasado. Excepción: los tests del motor, que reciben fechas explícitas.
- Si un test falla, se corrige el código. Si el test parece estar mal, se avisa al autor antes de cambiarlo.
- Cobertura objetivo: motor 95 % o más; servicios 85 % o más. Sin perseguir cobertura en vistas triviales.

## Frontend
- **Vitest** + **@testing-library/react** + **jsdom** (dependencias de desarrollo permitidas).
- Archivos `Nombre.test.jsx` junto al componente.
- Testear solo lo que tiene lógica:
  - `SelectorNivel`: arranca vacío, actualiza valor y descripciones al moverlo, una descripción en enteros y dos en medios puntos, manejo con teclado.
  - `utilidades/formato.js`: fechas, horas y coma decimal.
  - `api/cliente.js`: CSRF, conversión de errores, reacción a 401 y 403 con onboarding.
  - Rutas protegidas: redirecciones sin sesión y con onboarding incompleto.
- Buscar elementos como los ve el usuario (`getByRole`, `getByLabelText`), no por clases CSS. Sin snapshots.

## Antes de dar una tarea por terminada
`ruff check`, `ruff format --check` y `pytest` en el backend; `npm run lint` y `npm test` en el frontend. Todo en verde.
