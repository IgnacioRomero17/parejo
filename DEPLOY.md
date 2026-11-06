# Publicar parejo en Render y Neon

Guía para publicar la aplicación gratis: un único servidor en Render (Django sirve la API y el frontend compilado) y la base de datos PostgreSQL en Neon. El correo de recuperación de contraseña sale por SMTP con Brevo.

Las pantallas de Render, Neon y Brevo pueden cambiar; si un nombre no coincide, buscá la opción equivalente.

## 1. Antes de empezar

Hace falta:

- Una cuenta en [Render](https://render.com), una en [Neon](https://neon.com) y una en [Brevo](https://www.brevo.com).
- El repositorio en GitHub, con la rama que se va a publicar ya subida (`git push`).
- El proyecto funcionando en tu PC, con el entorno virtual de `backend/`: la carga de datos del paso 6 se hace desde ahí.

Límites del plan gratis de Render:

| Límite | Qué significa |
|---|---|
| Se duerme tras 15 minutos sin visitas | la primera visita después de eso tarda bastante en responder |
| 750 horas de instancia por mes | si se agotan, el servicio queda suspendido hasta el mes siguiente |
| Sin consola ni tareas puntuales | los comandos de carga de datos se corren desde tu PC (paso 6) |
| Puertos 25, 465 y 587 bloqueados | Gmail no funciona y por eso se usa Brevo por el puerto 2525 (ver paso 9) |

## 2. Crear la base en Neon

1. Crear un proyecto nuevo. Como región, elegir **AWS US East 2 (Ohio)**. Lo importante es que la base y el servidor de Render estén en la misma región; si elegís otra, usá la misma en los dos.
2. Abrir **Connect** y **desactivar "Connection pooling"**. El host correcto es el directo: **no** tiene `-pooler` en el nombre. Las migraciones no deben pasar por el pooler.
3. Anotar estos datos para los pasos siguientes:

| Dato de Neon | Variable | Ejemplo |
|---|---|---|
| Host | `DB_HOST` | `ep-ejemplo-123456.us-east-2.aws.neon.tech` |
| Database | `DB_NAME` | `neondb` |
| Role | `DB_USER` | `neondb_owner` |
| Password | `DB_PASSWORD` | la que muestra Neon |

No hace falta crear tablas: las crea el paso de construcción en Render.

## 3. Preparar el correo en Brevo

1. En **Senders, Domains & Dedicated IPs → Senders**, agregar el correo remitente y confirmarlo con el código de 6 dígitos que te llega. Se recomienda un Gmail creado solo para la app, no tu correo personal.
2. En **SMTP & API → SMTP**, generar una **clave SMTP** y anotarla junto con el **usuario (login)** que aparece en esa pantalla. La clave SMTP no es la contraseña de tu cuenta ni una clave de API.
3. Si la cuenta es nueva, puede que Brevo tenga que aprobarla antes de permitir envíos.

**A tener en cuenta:** sin dominio propio, Brevo puede reemplazar el remitente visible y el correo puede caer en spam. Para una demostración alcanza, pero conviene avisarlo a quien lo vaya a probar. Además, la clave SMTP vence tras 90 días sin envíos (ver "Problemas frecuentes").

## 4. Crear el servicio en Render

**New → Web Service**, conectar el repositorio de GitHub y completar:

| Campo | Valor |
|---|---|
| Name | el nombre define la dirección: `https://<nombre>.onrender.com` |
| Language | Python |
| Branch | la rama que vas a publicar |
| Region | Ohio (US East), la misma región que la base de Neon |
| Root Directory | **vacío** (si se completa, no quedan disponibles `backend/` y `frontend/` a la vez) |
| Build Command | `bash build.sh` |
| Start Command | `gunicorn --chdir backend config.wsgi:application --bind 0.0.0.0:$PORT` |
| Instance Type | Free |

No lo crees todavía: primero cargá las variables del paso siguiente, en la misma pantalla.

## 5. Cargar las variables de entorno

En **Environment Variables** se pueden cargar de a una o pegar todas juntas con **Add from .env**, en formato `VARIABLE=valor`, una por línea. Armá ese texto con los valores de esta tabla, no con el `.env` de tu PC, que es de desarrollo.

| Variable | Valor |
|---|---|
| `PYTHON_VERSION` | `3.13.17` |
| `NODE_VERSION` | `22.12.0` |
| `DJANGO_SECRET_KEY` | una clave nueva (ver abajo) |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `<nombre>.onrender.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://<nombre>.onrender.com` |
| `URL_FRONTEND` | `https://<nombre>.onrender.com` |
| `DB_HOST` | host directo de Neon |
| `DB_PORT` | `5432` |
| `DB_NAME` | base de Neon |
| `DB_USER` | rol de Neon |
| `DB_PASSWORD` | contraseña de Neon |
| `DB_SSLMODE` | `require` |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | `smtp-relay.brevo.com` |
| `EMAIL_PORT` | `2525` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | usuario SMTP de Brevo |
| `EMAIL_HOST_PASSWORD` | clave SMTP de Brevo |
| `DEFAULT_FROM_EMAIL` | `parejo <tu-correo-verificado@gmail.com>` |

Para generar la clave secreta, usá una nueva y distinta de la de tu `.env`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Creá el servicio. Render ejecuta `build.sh`, que instala las dependencias, compila el frontend, junta los estáticos y aplica las migraciones. Cuando termine, el log indica que el servicio está activo.

**Si Render asigna otra dirección** (por ejemplo, porque el nombre estaba ocupado), corregí `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` y `URL_FRONTEND` con la dirección real y volvé a publicar.

## 6. Cargar localidades, dataset y superusuario

El plan gratis no tiene consola, así que estos comandos se corren **desde tu PC, conectados a Neon**. Las variables definidas en la terminal tienen prioridad sobre el `.env`, y duran solo mientras esa terminal esté abierta.

```powershell
cd backend
.\.venv\Scripts\Activate.ps1

$env:DB_HOST = "ep-ejemplo-123456.us-east-2.aws.neon.tech"
$env:DB_PORT = "5432"
$env:DB_NAME = "neondb"
$env:DB_USER = "neondb_owner"
$env:DB_PASSWORD = Read-Host "Contraseña de Neon"
$env:DB_SSLMODE = "require"
```

La contraseña se pide con `Read-Host` para que no quede en el historial de PowerShell. Pegala con **clic derecho** y confirmá con Enter; se va a ver en pantalla mientras la pegás. Para comprobar que se cargó sin mostrarla, mirá su largo, que tiene que coincidir con el de la contraseña de Neon:

```powershell
$env:DB_PASSWORD.Length
```

Antes de cargar nada, comprobá que estás conectado a Neon:

```powershell
python manage.py shell -c "from django.db import connection; print(connection.settings_dict['HOST'])"
python manage.py showmigrations
```

El primer comando tiene que mostrar el host de Neon, y en el segundo todas las migraciones tienen que figurar aplicadas (`[X]`). Si es así, cargá los datos, en este orden:

```powershell
python manage.py loaddata localidades
python manage.py cargar_datos
python manage.py createsuperuser
```

`createsuperuser` pide correo, nombre, apellido y contraseña. Usá una contraseña fuerte, porque el admin queda en internet.

Al terminar, **cerrá la terminal** para no seguir conectado a Neon por error.

**Sobre los jugadores de demostración:** comparten la contraseña `parejo2026`, que está publicada en este repositorio, así que cualquiera puede entrar con esas cuentas y modificarlas. No guardes datos reales en ellas. Para devolverlas a los datos originales, ver el paso 8.

## 7. Comprobar que funciona

En `https://<nombre>.onrender.com`:

1. La pantalla de bienvenida carga con sus estilos, y al recargar en una ruta interna (por ejemplo `/ingresar`) sigue funcionando.
2. Ingresar con `tomas.rios@demo.parejo.example` y `parejo2026`.
3. Crear un encuentro y ver los jugadores recomendados.
4. Entrar a `/admin/` con el superusuario.
5. Registrar una cuenta con un correo tuyo real y pedir la recuperación de contraseña. Revisá también la carpeta de spam. Las cuentas de demostración usan el dominio `.example` y no reciben correo.

Por último, agregá la dirección publicada en la sección "Versión publicada" del `README.md`.

## 8. Reiniciar la demo

`reiniciar_demo` deja la demostración como recién cargada: borra **todos** los encuentros (con sus invitaciones, participaciones y propuestas, también los de cuentas que no son del dataset) y devuelve a los jugadores del dataset sus datos y la contraseña común. No toca localidades, superusuarios ni otras cuentas, ni la estructura de la base. Antes de borrar muestra el host de la base y cuántos encuentros, invitaciones y propuestas va a borrar, y pide escribir `si`. Si algo falla, no se borra nada.

En tu PC, contra la base de desarrollo:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py reiniciar_demo
```

Contra Neon, en una terminal nueva, cargá las mismas variables del paso 6 y comprobá el host antes de correrlo:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1

$env:DB_HOST = "ep-ejemplo-123456.us-east-2.aws.neon.tech"
$env:DB_PORT = "5432"
$env:DB_NAME = "neondb"
$env:DB_USER = "neondb_owner"
$env:DB_PASSWORD = Read-Host "Contraseña de Neon"
$env:DB_SSLMODE = "require"
$env:DB_PASSWORD.Length

python manage.py shell -c "from django.db import connection; print(connection.settings_dict['HOST'])"
python manage.py reiniciar_demo
```

Confirmá solo si el host que muestra el comando es el de Neon. Al terminar, **cerrá la terminal**.

## 9. Nota sobre Gmail

Gmail SMTP (`smtp.gmail.com`) solo atiende por puertos que el plan gratis de Render bloquea, así que **ahí no funciona**. Solo sirve con una instancia paga de Render. En ese caso:

1. En la cuenta de Google, activar la verificación en dos pasos y crear una [contraseña de aplicación](https://myaccount.google.com/apppasswords).
2. Cambiar estas variables en Render:

| Variable | Valor |
|---|---|
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_HOST_USER` | tu correo de Gmail |
| `EMAIL_HOST_PASSWORD` | la contraseña de aplicación |
| `DEFAULT_FROM_EMAIL` | `parejo <tu-correo@gmail.com>` |

## 10. Problemas frecuentes

| Qué se ve | Causa probable | Qué hacer |
|---|---|---|
| Error 400 en todas las páginas | el dominio no está en `DJANGO_ALLOWED_HOSTS` | poner solo el dominio, sin `https://` ni barra final |
| Error 403 de CSRF al ingresar o registrarse | `DJANGO_CSRF_TRUSTED_ORIGINS` mal cargada | poner la dirección con `https://` y sin barra final |
| El navegador avisa de demasiadas redirecciones | el servicio no recibe la cabecera del proxy de Render | revisar que se publicó esta rama, con `SECURE_PROXY_SSL_HEADER` en `settings.py` |
| La construcción falla al compilar el frontend, por la versión de Node | Render no tomó `NODE_VERSION` | mirar la primera línea del log (`Node v...`) y revisar la variable |
| La construcción falla con `Falta la variable de entorno` | falta una variable obligatoria | cargar la que indica el mensaje |
| La construcción falla al migrar | datos de Neon incorrectos | revisar las variables `DB_*` y que el host sea el directo |
| Error al pedir la recuperación de contraseña | datos SMTP incorrectos o cuenta de Brevo sin aprobar | revisar `EMAIL_*`, el puerto `2525` y los logs de Render |
| No llegan los correos | la clave SMTP de Brevo venció (90 días sin envíos) | generar una clave nueva en Brevo y reemplazar `EMAIL_HOST_PASSWORD` en Render |
| La localidad no aparece o `cargar_datos` pide cargarlas | faltan las localidades | correr `loaddata localidades` (paso 6) |
| Tarda mucho la primera visita | el servicio estaba dormido | es normal en el plan gratis |
