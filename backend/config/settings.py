import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def cargar_archivo_env(ruta: Path) -> None:
    """Carga las líneas CLAVE=VALOR de un archivo .env en os.environ.

    Las variables ya definidas en el entorno tienen prioridad sobre el archivo.
    Si el archivo no existe, no hace nada.
    """
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip())


def variable_obligatoria(nombre: str) -> str:
    """Devuelve una variable de entorno o lanza ImproperlyConfigured si falta o está vacía."""
    valor = os.environ.get(nombre)
    if not valor:
        raise ImproperlyConfigured(f"Falta la variable de entorno {nombre} (ver .env.example).")
    return valor


cargar_archivo_env(BASE_DIR / ".env")

SECRET_KEY = variable_obligatoria("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.localidades",
    "apps.usuarios",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "parejo"),
        "USER": variable_obligatoria("DB_USER"),
        "PASSWORD": variable_obligatoria("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTH_USER_MODEL = "usuarios.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "apps.usuarios.validadores.ValidadorPoliticaContrasena"},
]

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Cordoba"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

BACKEND_CORREO = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
CORREO_POR_DEFECTO = {"BACKEND": BACKEND_CORREO}
# Solo el backend SMTP acepta estas opciones; el de consola las rechaza.
if BACKEND_CORREO == "django.core.mail.backends.smtp.EmailBackend":
    CORREO_POR_DEFECTO["OPTIONS"] = {
        "host": variable_obligatoria("EMAIL_HOST"),
        "port": int(os.environ.get("EMAIL_PORT", "587")),
        "username": os.environ.get("EMAIL_HOST_USER", ""),
        "password": os.environ.get("EMAIL_HOST_PASSWORD", ""),
        "use_tls": os.environ.get("EMAIL_USE_TLS", "True").lower() == "true",
    }
MAILERS = {"default": CORREO_POR_DEFECTO}
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "parejo <no-responder@localhost>")

# Base de los enlaces que se envían por correo: la ruta del frontend, no la de Django.
URL_FRONTEND = os.environ.get("URL_FRONTEND", "http://localhost:5173").rstrip("/")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "COERCE_DECIMAL_TO_STRING": False,
    "EXCEPTION_HANDLER": "apps.comun.errores.manejar_excepcion",
}
