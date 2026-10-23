from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.comun.errores import ErrorNegocio
from apps.usuarios.models import Usuario

MENSAJE_CORREO_REGISTRADO = "Este correo ya está registrado."
MENSAJE_CREDENCIALES_INVALIDAS = "Las credenciales ingresadas no son válidas."
MENSAJE_CUENTA_INEXISTENTE = "La cuenta no existe. Revisá el correo ingresado."
MENSAJE_ENLACE_INVALIDO = "El enlace no es válido."
ASUNTO_RECUPERACION = "Restablecé tu contraseña de parejo"
ID_MAXIMO = 2_147_483_647  # máximo de la columna integer de id_usuario


def normalizar_correo(email: str) -> str:
    """Devuelve el correo sin espacios alrededor y en minúsculas, como se guarda y se busca."""
    return email.strip().lower()


def validar_correo_disponible(email: str) -> None:
    """Verifica que ningún usuario tenga ya ese correo (comparado en minúsculas).

    Lanza ErrorNegocio en el campo `email` si ya está registrado.
    """
    if Usuario.objects.filter(email=normalizar_correo(email)).exists():
        raise ErrorNegocio(MENSAJE_CORREO_REGISTRADO, campo="email")


def validar_contrasena(contrasena: str, usuario: Usuario | None = None) -> None:
    """Aplica los validadores de AUTH_PASSWORD_VALIDATORS (política de contraseña).

    Recibe la contraseña y, si ya existe, el usuario al que pertenece.
    Lanza ErrorNegocio en el campo `contrasena` con el primer mensaje del validador.
    """
    try:
        validate_password(contrasena, usuario)
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


def enlace_recuperacion(usuario: Usuario) -> str:
    """Arma el enlace de recuperación de contraseña hacia la ruta del frontend (HU-003).

    Devuelve `{URL_FRONTEND}/recuperar/{uid}/{token}`, con el id en base64 y un token de
    PasswordResetTokenGenerator, que deja de servir cuando cambia la contraseña.
    """
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)
    return f"{settings.URL_FRONTEND}/recuperar/{uid}/{token}"


def solicitar_recuperacion(email: str) -> None:
    """Envía al usuario el correo con el enlace para restablecer la contraseña (HU-003).

    Recibe el correo (en cualquier combinación de mayúsculas). Lanza ErrorNegocio en el campo
    `email` si no hay una cuenta activa con ese correo; la HU exige informarlo.
    """
    usuario = Usuario.objects.filter(email=normalizar_correo(email), is_active=True).first()
    if usuario is None:
        raise ErrorNegocio(MENSAJE_CUENTA_INEXISTENTE, campo="email")
    cuerpo = (
        f"Hola, {usuario.nombre}:\n\n"
        "Para definir una nueva contraseña, abrí este enlace:\n"
        f"{enlace_recuperacion(usuario)}\n\n"
        "Si no lo pediste, podés ignorar este correo.\n"
    )
    EmailMessage(ASUNTO_RECUPERACION, cuerpo, to=[usuario.email]).send()


def _usuario_del_uid(uid: str, consulta: QuerySet[Usuario]) -> Usuario:
    try:
        id_usuario = int(urlsafe_base64_decode(uid).decode())
    except (ValueError, UnicodeDecodeError) as error:
        raise ErrorNegocio(MENSAJE_ENLACE_INVALIDO) from error
    # Un id fuera del rango de la columna haría fallar la consulta en PostgreSQL.
    if not 0 < id_usuario <= ID_MAXIMO:
        raise ErrorNegocio(MENSAJE_ENLACE_INVALIDO)
    usuario = consulta.filter(pk=id_usuario, is_active=True).first()
    if usuario is None:
        raise ErrorNegocio(MENSAJE_ENLACE_INVALIDO)
    return usuario


def usuario_por_enlace(uid: str, token: str) -> Usuario:
    """Devuelve el usuario de un enlace de recuperación válido (HU-003).

    Recibe el uid y el token de la ruta `/recuperar/:uid/:token`. Lanza ErrorNegocio general
    si el uid no corresponde a una cuenta activa o si el token no es válido o ya se usó.
    """
    usuario = _usuario_del_uid(uid, Usuario.objects.all())
    if not default_token_generator.check_token(usuario, token):
        raise ErrorNegocio(MENSAJE_ENLACE_INVALIDO)
    return usuario


def restablecer_contrasena(uid: str, token: str, contrasena: str) -> Usuario:
    """Guarda la nueva contraseña de un usuario a partir del enlace del correo (HU-003).

    Recibe el uid y el token del enlace y la nueva contraseña, que debe cumplir la política
    de HU-001. Devuelve el usuario. Lanza ErrorNegocio general si el enlace no es válido o ya
    se usó, o en el campo `contrasena` si no cumple la política.
    """
    with transaction.atomic():
        # Bloquear al usuario evita que dos envíos simultáneos usen el mismo enlace.
        usuario = _usuario_del_uid(uid, Usuario.objects.select_for_update())
        if not default_token_generator.check_token(usuario, token):
            raise ErrorNegocio(MENSAJE_ENLACE_INVALIDO)
        validar_contrasena(contrasena, usuario)
        usuario.set_password(contrasena)
        usuario.save(update_fields=["password"])
    return usuario


def actualizar_perfil(
    usuario: Usuario,
    datos_personales: dict | None = None,
    perfil_deportivo: dict | None = None,
) -> Usuario:
    """Guarda las secciones del perfil que el jugador modificó (HU-004).

    Recibe el usuario y, por sección, los datos ya validados en formato: `datos_personales`
    (nombre y apellido) y `perfil_deportivo` (edad, género, localidad, frecuencia de juego y
    nivel estimado, todos juntos). Una sección que no llega no se toca. Las secciones se
    guardan juntas en un solo cambio, así que se guarda todo o nada. Devuelve el usuario.
    """
    cambios = {**(datos_personales or {}), **(perfil_deportivo or {})}
    if not cambios:
        return usuario
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    usuario.save(update_fields=list(cambios))
    return usuario


def paso_onboarding_pendiente(usuario: Usuario) -> str | None:
    """Devuelve el paso de onboarding que le falta al usuario, o None si no le falta ninguno.

    El paso "perfil" (HU-004) queda hecho cuando el perfil está completo (nivel y localidad).
    El paso "disponibilidad" se suma con la preferencia de HU-005, que todavía no existe.
    """
    if not usuario.perfil_completo:
        return "perfil"
    return None
