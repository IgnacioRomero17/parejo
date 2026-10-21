---
paths:
  - "**/*.py"
---

# Convenciones de Python

## Versión y herramientas
- Python 3.12 o superior, en un entorno virtual (`backend/.venv`, fuera de git).
- Dependencias con versión fija en `backend/requirements.txt` (producción) y `backend/requirements-dev.txt` (desarrollo y tests).
- **Ruff** para formato y linter (`ruff format` y `ruff check`), configurado en `backend/pyproject.toml` con largo de línea 100. El código se entrega sin advertencias.

## Nombres
- En español, sin tildes ni ñ en los identificadores: `contrasena`, `anio`, `dia_semana`.
- `snake_case` para funciones, variables y módulos; `PascalCase` para clases; `MAYUSCULAS` para constantes.
- Nombres que dicen qué es, sin abreviar: `lugares_libres`, no `ll`; `candidatos_filtrados`, no `cf`.
- Los nombres del dominio son los del modelo: `encuentro`, `participante`, `invitacion`, `combinacion`, `pareja`, `propuesta`.

## Estilo
- Anotaciones de tipo en todas las funciones de `motor/`, servicios y utilidades. En vistas, serializers y modelos son opcionales.
- Docstring en español en toda función pública del motor y de los servicios: qué hace, qué recibe, qué devuelve y qué error lanza. En el motor, incluir la fórmula.
- Funciones cortas, con una sola responsabilidad. Si una función pasa de unas 40 líneas, dividirla.
- Comentarios solo para explicar **por qué**, no qué hace el código.
- Sin código comentado ni sin usar, sin `print()` y sin `TODO` sin explicación.
- f-strings para armar texto.
- Excepciones específicas (`ValueError`, `ErrorNegocio`); nunca `except:` ni `except Exception` sin volver a lanzar.
- Imports en tres grupos (biblioteca estándar, terceros, propios) en orden alfabético; Ruff los ordena.
- Sin abstracciones "por si acaso": nada de clases base, fábricas o capas que hoy no se usan.

## Fechas y números
- En código Django, fecha y hora actuales con `django.utils.timezone.now()` y `timezone.localdate()`; nunca `datetime.now()` sin zona.
- El motor recibe `date` y `time` ya resueltos y no consulta la hora actual.
- Niveles y puntajes se guardan como `Decimal`; se comparan y redondean según la regla del motor.

## Logs
- Módulo `logging`, con un logger por módulo (`logger = logging.getLogger(__name__)`).
- Nunca registrar contraseñas, tokens, correos ni datos del perfil. Identificar por id.
