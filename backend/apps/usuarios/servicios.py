from datetime import time

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
from apps.comun.horarios import MENSAJE_HORA_INVALIDA, hora_valida, minutos
from apps.usuarios.models import Disponibilidad, Preferencia, Usuario

MENSAJE_CORREO_REGISTRADO = "Este correo ya está registrado."
MENSAJE_CREDENCIALES_INVALIDAS = "Las credenciales ingresadas no son válidas."
MENSAJE_CUENTA_INEXISTENTE = "La cuenta no existe. Revisá el correo ingresado."
MENSAJE_ENLACE_INVALIDO = "El enlace no es válido."
ASUNTO_RECUPERACION = "Restablecé tu contraseña de parejo"
ID_MAXIMO = 2_147_483_647  # máximo de la columna integer de id_usuario
MENSAJE_FIN_ANTES_DE_INICIO = "La hora de fin debe ser posterior a la de inicio."
MENSAJE_FRANJA_CORTA = "La franja debe durar al menos 60 minutos."
MENSAJE_DISPONIBLE_SIN_FRANJAS = "Para recibir invitaciones necesitás cargar al menos una franja."
DURACION_MINIMA_FRANJA = 60  # minutos: el encuentro más corto


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


def validar_franja(hora_inicio: time, hora_fin: time) -> None:
    """Verifica una franja de disponibilidad (HU-005).

    Recibe sus horas de inicio y de fin. Cada hora va en pasos de 30 minutos, entre las 08:00 y
    las 23:30; el fin es posterior al inicio y la franja dura al menos 60 minutos. Lanza
    ErrorNegocio en el campo `hora_inicio` o `hora_fin` con la primera regla que no se cumple.
    """
    if not hora_valida(hora_inicio):
        raise ErrorNegocio(MENSAJE_HORA_INVALIDA, campo="hora_inicio")
    if not hora_valida(hora_fin):
        raise ErrorNegocio(MENSAJE_HORA_INVALIDA, campo="hora_fin")
    if hora_fin <= hora_inicio:
        raise ErrorNegocio(MENSAJE_FIN_ANTES_DE_INICIO, campo="hora_fin")
    if minutos(hora_fin) - minutos(hora_inicio) < DURACION_MINIMA_FRANJA:
        raise ErrorNegocio(MENSAJE_FRANJA_CORTA, campo="hora_fin")


def validar_disponible_con_franjas(franjas: list[dict], disponible: bool) -> None:
    """Verifica que un jugador disponible para recibir invitaciones tenga franjas (HU-005).

    Recibe las franjas que quedarían guardadas y el valor del interruptor. Lanza ErrorNegocio
    en el campo `disponible_para_invitaciones` si está disponible y no hay ninguna franja.
    """
    if disponible and not franjas:
        raise ErrorNegocio(MENSAJE_DISPONIBLE_SIN_FRANJAS, campo="disponible_para_invitaciones")


def unir_franjas(franjas: list[dict]) -> list[dict]:
    """Une las franjas del mismo día que se superponen o se tocan (HU-005).

    Recibe franjas `{dia_semana, hora_inicio, hora_fin}` en cualquier orden. Devuelve franjas
    nuevas, ordenadas por día y hora de inicio: 17:00–19:00 y 18:30–21:00 quedan 17:00–21:00,
    igual que 17:00–19:00 y 19:00–21:00. El motor exige que una sola franja cubra el encuentro.
    """
    unidas: list[dict] = []
    orden = sorted(franjas, key=lambda f: (f["dia_semana"], f["hora_inicio"], f["hora_fin"]))
    for franja in orden:
        anterior = unidas[-1] if unidas else None
        if (
            anterior
            and anterior["dia_semana"] == franja["dia_semana"]
            and franja["hora_inicio"] <= anterior["hora_fin"]
        ):
            anterior["hora_fin"] = max(anterior["hora_fin"], franja["hora_fin"])
        else:
            unidas.append(dict(franja))
    return unidas


def _guardar_preferencia_y_franjas(usuario: Usuario, disponibilidad: dict) -> None:
    preferencia, _ = Preferencia.objects.update_or_create(
        usuario=usuario,
        defaults={
            "tipo_encuentro": disponibilidad["tipo_encuentro"],
            "lado_preferido": disponibilidad["lado_preferido"],
        },
    )
    # Deja la relación del objeto al día para la respuesta, que la lee del mismo usuario.
    usuario.preferencia = preferencia
    # Se guardan las franjas completas de la pantalla: reemplazan a las anteriores.
    Disponibilidad.objects.filter(usuario=usuario).delete()
    Disponibilidad.objects.bulk_create(
        Disponibilidad(usuario=usuario, **franja)
        for franja in unir_franjas(disponibilidad["franjas"])
    )


def actualizar_perfil(
    usuario: Usuario,
    datos_personales: dict | None = None,
    perfil_deportivo: dict | None = None,
    disponibilidad: dict | None = None,
) -> Usuario:
    """Guarda las secciones del perfil que el jugador modificó (HU-004 y HU-005).

    Recibe el usuario y, por sección, los datos ya validados en formato: `datos_personales`
    (nombre y apellido), `perfil_deportivo` (edad, género, localidad, frecuencia de juego y
    nivel estimado) y `disponibilidad` (franjas, tipo de encuentro, lado preferido y
    disponible para invitaciones). Cada sección llega completa y una que no llega no se toca.
    Las franjas se guardan ya unidas. Todo se guarda en una transacción: todo o nada.
    Devuelve el usuario. Lanza ErrorNegocio si una franja no es válida o si el jugador queda
    disponible sin franjas.
    """
    cambios = {**(datos_personales or {}), **(perfil_deportivo or {})}
    if disponibilidad is not None:
        for franja in disponibilidad["franjas"]:
            validar_franja(franja["hora_inicio"], franja["hora_fin"])
        disponible = disponibilidad["disponible_para_invitaciones"]
        validar_disponible_con_franjas(disponibilidad["franjas"], disponible)
        cambios["disponible_para_invitaciones"] = disponible
    if not cambios:
        return usuario
    with transaction.atomic():
        for campo, valor in cambios.items():
            setattr(usuario, campo, valor)
        usuario.save(update_fields=list(cambios))
        if disponibilidad is not None:
            _guardar_preferencia_y_franjas(usuario, disponibilidad)
    return usuario


def paso_onboarding_pendiente(usuario: Usuario) -> str | None:
    """Devuelve el paso de onboarding que le falta al usuario, o None si no le falta ninguno.

    El paso "perfil" (HU-004) queda hecho cuando el perfil está completo (nivel y localidad);
    el paso "disponibilidad" (HU-005), cuando el jugador guardó sus preferencias.
    """
    if not usuario.perfil_completo:
        return "perfil"
    # Consulta y no `usuario.preferencia`: la relación queda en caché y no vería un alta nueva.
    if not Preferencia.objects.filter(usuario=usuario).exists():
        return "disponibilidad"
    return None
