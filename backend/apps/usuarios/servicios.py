from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.comun.errores import ErrorNegocio
from apps.usuarios.models import Usuario

MENSAJE_CORREO_REGISTRADO = "Este correo ya está registrado."
MENSAJE_CREDENCIALES_INVALIDAS = "Las credenciales ingresadas no son válidas."


def normalizar_correo(email: str) -> str:
    """Devuelve el correo sin espacios alrededor y en minúsculas, como se guarda y se busca."""
    return email.strip().lower()


def validar_correo_disponible(email: str) -> None:
    """Verifica que ningún usuario tenga ya ese correo (comparado en minúsculas).

    Lanza ErrorNegocio en el campo `email` si ya está registrado.
    """
    if Usuario.objects.filter(email=normalizar_correo(email)).exists():
        raise ErrorNegocio(MENSAJE_CORREO_REGISTRADO, campo="email")


def validar_contrasena(contrasena: str) -> None:
    """Aplica los validadores de AUTH_PASSWORD_VALIDATORS (política de contraseña).

    Lanza ErrorNegocio en el campo `contrasena` con el primer mensaje del validador.
    """
    try:
        validate_password(contrasena)
    except ValidationError as error:
        raise ErrorNegocio(error.messages[0], campo="contrasena") from error


def registrar_usuario(nombre: str, apellido: str, email: str, contrasena: str) -> Usuario:
    """Crea la cuenta de un jugador (HU-001).

    Recibe los datos ya validados en formato; guarda el correo en minúsculas y la contraseña
    con el hasher por defecto de Django. Devuelve el usuario creado, con el perfil incompleto.
    Lanza ErrorNegocio si el correo ya está registrado o la contraseña no cumple la política.
    """
    email = normalizar_correo(email)
    validar_correo_disponible(email)
    validar_contrasena(contrasena)
    try:
        with transaction.atomic():
            return Usuario.objects.create_user(
                email=email, password=contrasena, nombre=nombre, apellido=apellido
            )
    except IntegrityError as error:
        # Otro registro con el mismo correo pudo entrar entre la verificación y el alta.
        raise ErrorNegocio(MENSAJE_CORREO_REGISTRADO, campo="email") from error


def autenticar_usuario(email: str, contrasena: str) -> Usuario:
    """Verifica las credenciales de ingreso (HU-002).

    Recibe el correo (en cualquier combinación de mayúsculas) y la contraseña. Devuelve el
    usuario si coinciden y la cuenta está activa. Lanza ErrorNegocio general con el mismo
    mensaje si la contraseña es incorrecta o el correo no está registrado, para no revelar
    qué correos existen.
    """
    usuario = authenticate(email=normalizar_correo(email), password=contrasena)
    if usuario is None:
        raise ErrorNegocio(MENSAJE_CREDENCIALES_INVALIDAS)
    return usuario


def paso_onboarding_pendiente(usuario: Usuario) -> str | None:
    """Devuelve el paso de onboarding que le falta al usuario, o None si no le falta ninguno.

    Por ahora solo existe el paso "perfil" (nivel y localidad); "disponibilidad" se suma
    con la preferencia de HU-005.
    """
    if not usuario.perfil_completo:
        return "perfil"
    return None
