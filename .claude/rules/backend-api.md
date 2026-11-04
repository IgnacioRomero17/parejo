---
paths:
  - "backend/apps/**"
  - "backend/config/**"
---

# Backend y API (Django + DRF)

## Archivos de cada app
```
apps/<app>/
  models.py        # ver regla modelo-datos
  servicios.py     # reglas de negocio y transacciones
  serializers.py   # formato de entrada y salida
  vistas.py        # endpoints (APIView o vistas genéricas de DRF)
  permisos.py      # clases de permiso propias
  urls.py
  admin.py
```
Tests en `backend/tests/<app>/`.

## Responsabilidad de cada capa
| Capa | Hace | No hace |
|---|---|---|
| Vista | autentica, aplica permisos, usa el serializer, llama a **un** servicio, arma la respuesta | consultas complejas, reglas de negocio |
| Serializer | valida formato y tipos, convierte a JSON | cambiar estados, crear objetos de otros modelos |
| Servicio | reglas de negocio, cambios de estado, transacciones, llamadas al motor | conocer `request` ni devolver respuestas HTTP |
| Modelo | datos y consultas simples propias | ver regla modelo-datos |

- Los servicios son **funciones** (`crear_encuentro(organizador, datos)`), no clases.
- Toda operación que escribe en más de una tabla va en `transaction.atomic()`.
- Invitar, aceptar una invitación y formar parejas bloquean el encuentro con `select_for_update()` antes de contar participantes o invitaciones.
- Un módulo usa a otro solo por sus servicios o consultas de lectura, nunca escribiendo en sus tablas.

## Errores
- Los servicios lanzan `ErrorNegocio(mensaje, campo=None, estado=400)` (definida en `apps/comun/errores.py`).
- Un manejador de excepciones de DRF la convierte en respuesta. Formato único:
  - Errores de campos: `{"errores": {"campo": ["mensaje"]}}` (400).
  - Error general: `{"detalle": "mensaje"}`.
- Códigos: 400 datos inválidos · 401 sin sesión · 403 sin permiso sobre algo que puede ver · 404 no existe o no le pertenece · 409 estado del encuentro no permite la acción.
- Los mensajes son los de `docs/historias-de-usuario.md` y `docs/interfaces/`, en español y textuales.
- Credenciales inválidas al ingresar y "La cuenta no existe" al recuperar responden **400**, no 401 (el 401 es solo para pedidos sin sesión).

## Endpoints
Todos bajo `/api/`. JSON en ambos sentidos. Fechas ISO 8601, horas `HH:MM`, niveles y puntajes como números (`COERCE_DECIMAL_TO_STRING = False`).

| Método y ruta | HU | Acceso |
|---|---|---|
| `GET auth/csrf` | — | pública (entrega la cookie CSRF) |
| `POST auth/registro` | HU-001 | pública; inicia sesión al crear |
| `POST auth/ingresar` · `POST auth/salir` | HU-002 | pública · sesión |
| `GET auth/yo` | — | sesión; datos básicos, paso de onboarding pendiente y `invitaciones_pendientes` (para el indicador de la barra) |
| `POST auth/recuperar` · `GET auth/recuperar/{uid}/{token}` · `POST auth/recuperar/confirmar` | HU-003 | pública, con o sin sesión; el `GET` valida el enlace y devuelve el correo (400 si no es válido) |
| `GET perfil` · `PATCH perfil` | HU-004, HU-005 | sesión; `PATCH` recibe las secciones que cambian y guarda todo o nada |
| `GET localidades` | HU-004, HU-006 | sesión |
| `GET encuentros` | HU-012 | onboarding completo; encuentros activos del usuario |
| `POST encuentros` | HU-006 | onboarding completo |
| `GET encuentros/{id}` | HU-008 | organizador o participante. Devuelve datos del encuentro, `confirmados`, `lugares_libres`, participantes (id, nombre, localidad, nivel, lado) y, solo al organizador, invitaciones (id, jugador con nombre, localidad y nivel, estado, fecha de envío) |
| `GET encuentros/{id}/recomendados` | HU-007 | organizador |
| `POST encuentros/{id}/invitaciones` | HU-008 | organizador; recibe `{"usuarios": [ids]}` |
| `POST encuentros/{id}/formar-parejas` | HU-009 a HU-011 | organizador |
| `GET encuentros/{id}/propuesta` | HU-012 | participantes |
| `GET invitaciones` | HU-008 | onboarding completo; las recibidas |
| `POST invitaciones/{id}/aceptar` · `.../rechazar` | HU-008 | el invitado |

No crear endpoints que no estén en esta tabla sin consultar.

## Permisos
- Por defecto `IsAuthenticated` en toda la API, salvo las rutas públicas de la tabla.
- `OnboardingCompleto`: perfil completo y preferencia cargada; si falta, 403 con `{"detalle": "...", "onboarding": "perfil" | "disponibilidad"}`.
- `EsOrganizador`, `EsParticipante`, `EsInvitado`: verifican sobre el objeto. Si el usuario no tiene relación con el encuentro o la invitación, responder **404**.

## Estados del encuentro
| Desde | Hacia | Cuándo (en el servicio) |
|---|---|---|
| — | `BUSCANDO_PARTICIPANTES` | al crear (`CREADO` es transitorio dentro de la misma transacción) |
| `BUSCANDO_PARTICIPANTES` | `COMPLETO` | al aceptar la invitación que lleva a 4 confirmados |
| `COMPLETO` | `PROPUESTA_GENERADA` | al formar parejas |
Cualquier otra acción sobre un estado que no corresponde responde 409.

**Validaciones adicionales**
- Invitar: el servicio recalcula la recomendación en ese momento. Cada id debe estar entre los recomendados y no invitado antes; si no, 409 "Alguno de los jugadores ya no está disponible para este encuentro. Actualizá la lista.". Si se envían más ids que lugares libres, 400 "Seleccionaste más jugadores que lugares libres.".
- Encuentro ya iniciado (fecha y hora de inicio pasadas): invitar, aceptar, rechazar y formar parejas responden 409 "Este encuentro ya comenzó.". Sus invitaciones pendientes no se muestran en la bandeja.

## Autenticación y seguridad
- Sesiones de Django con cookie (`SessionAuthentication` de DRF) y CSRF activo. El frontend pide `auth/csrf` al iniciar y envía el token en `X-CSRFToken`.
- Política de contraseña: validador propio en `AUTH_PASSWORD_VALIDATORS` (8 a 64 caracteres, al menos una letra y un número), usado en registro y en recuperación.
- Correo siempre en minúsculas antes de buscar o guardar.
- Recuperación con `PasswordResetTokenGenerator` de Django; el enlace apunta a la ruta del frontend `/recuperar/:uid/:token`.
- La HU-003 exige informar "La cuenta no existe": se respeta aunque revele qué correos están registrados.
- No escribir en logs correos, edades, géneros ni localidades.

## Configuración (`config/`)
- Valores sensibles y de entorno (`SECRET_KEY`, base de datos, SMTP, `DEBUG`) desde variables de entorno con `os.environ`, con valores por defecto solo para desarrollo. Sin librerías extra para esto.
- `LANGUAGE_CODE = "es-ar"`, `TIME_ZONE = "America/Argentina/Cordoba"`, `USE_TZ = True`.
- Desarrollo: `EMAIL_BACKEND` de consola. Producción: SMTP.
- Dependencias permitidas: `Django>=5.2`, `djangorestframework`, `psycopg[binary]`. Las de testing, en su regla. En producción, gunicorn (servidor de aplicación) y whitenoise (archivos estáticos y frontend compilado)
