from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from apps.comun.errores import ErrorNegocio
from apps.comun.horarios import MENSAJE_HORA_INVALIDA, hora_valida, minutos
from apps.encuentros.models import MINUTOS_FIN_MAXIMO, Encuentro, EstadoEncuentro, Participante
from apps.usuarios import servicios as servicios_usuarios
from apps.usuarios.models import Usuario
from motor.filtros import franja_que_cubre
from motor.recomendar import recomendar
from motor.tipos import CandidatoEntrada, EncuentroEntrada, Franja

MENSAJE_FIN_TARDE = "El encuentro tiene que terminar a las 23:30 como máximo."
MENSAJE_EN_EL_PASADO = "Elegí una fecha y hora futuras."
MENSAJE_FECHA_LEJANA = "Elegí una fecha dentro de los próximos 60 días."
DIAS_MAXIMOS_ANTICIPACION = 60
MENSAJE_SIN_ONBOARDING = "Completá tu perfil para continuar."
MENSAJE_ENCUENTRO_INEXISTENTE = "El encuentro no existe."
ID_MAXIMO = 2_147_483_647  # máximo de la columna integer de id_encuentro


def validar_condiciones(fecha: date, hora_inicio: time, duracion_minutos: int) -> None:
    """Verifica el horario de un encuentro nuevo (HU-006).

    Recibe la fecha, la hora de inicio y la duración. La hora va en pasos de 30 minutos entre
    las 08:00 y las 23:30; el encuentro termina a las 23:30 como máximo; empieza después del
    momento actual y su fecha no pasa de hoy + 60 días, ambos en la zona horaria del sistema
    (America/Argentina/Cordoba). Lanza ErrorNegocio en el campo `hora_inicio`,
    `duracion_minutos` o `fecha` con la primera regla que no se cumple.
    """
    if not hora_valida(hora_inicio):
        raise ErrorNegocio(MENSAJE_HORA_INVALIDA, campo="hora_inicio")
    if minutos(hora_inicio) + duracion_minutos > MINUTOS_FIN_MAXIMO:
        raise ErrorNegocio(MENSAJE_FIN_TARDE, campo="duracion_minutos")
    # La fecha y la hora se interpretan en Córdoba, no en UTC: a las 22:00 de Córdoba ya es
    # el día siguiente en UTC y un encuentro de hoy a las 22:30 todavía es futuro.
    zona = timezone.get_default_timezone()
    inicio = datetime.combine(fecha, hora_inicio, tzinfo=zona)
    ahora = timezone.now()
    hoy = ahora.astimezone(zona).date()
    if inicio <= ahora:
        campo = "fecha" if fecha < hoy else "hora_inicio"
        raise ErrorNegocio(MENSAJE_EN_EL_PASADO, campo=campo)
    if fecha > hoy + timedelta(days=DIAS_MAXIMOS_ANTICIPACION):
        raise ErrorNegocio(MENSAJE_FECHA_LEJANA, campo="fecha")


def crear_encuentro(organizador: Usuario, datos: dict) -> Encuentro:
    """Crea un encuentro con sus condiciones y registra al organizador (HU-006).

    Recibe el organizador, con el onboarding completo, y los datos ya validados en formato:
    `fecha`, `hora_inicio`, `duracion_minutos`, `localidad`, `ubicacion` y `tipo_encuentro`.
    En una transacción crea el encuentro, registra al organizador como primer participante
    confirmado (1 de 4) y lo deja en BUSCANDO_PARTICIPANTES. Devuelve el encuentro.
    Lanza ErrorNegocio 403 si al organizador le falta el onboarding, o en un campo si el
    horario no es válido (ver `validar_condiciones`).
    """
    if servicios_usuarios.paso_onboarding_pendiente(organizador) is not None:
        raise ErrorNegocio(MENSAJE_SIN_ONBOARDING, estado=403)
    validar_condiciones(datos["fecha"], datos["hora_inicio"], datos["duracion_minutos"])
    with transaction.atomic():
        encuentro = Encuentro.objects.create(organizador=organizador, **datos)
        Participante.objects.create(encuentro=encuentro, usuario=organizador)
        # CREADO dura solo dentro de esta transacción: con el organizador registrado, el
        # encuentro ya está listo para buscar participantes.
        encuentro.estado = EstadoEncuentro.BUSCANDO_PARTICIPANTES
        encuentro.save(update_fields=["estado"])
    return encuentro


def obtener_encuentro(id_encuentro: int) -> Encuentro:
    """Devuelve el encuentro con ese id, con su localidad.

    Lanza ErrorNegocio 404 si no existe.
    """
    # Un id fuera del rango de la columna haría fallar la consulta en PostgreSQL.
    if not 0 < id_encuentro <= ID_MAXIMO:
        raise ErrorNegocio(MENSAJE_ENCUENTRO_INEXISTENTE, estado=404)
    encuentro = Encuentro.objects.select_related("localidad").filter(pk=id_encuentro).first()
    if encuentro is None:
        raise ErrorNegocio(MENSAJE_ENCUENTRO_INEXISTENTE, estado=404)
    return encuentro


def es_participante(usuario: Usuario, encuentro: Encuentro) -> bool:
    """Indica si el usuario es participante confirmado del encuentro (el organizador lo es)."""
    return encuentro.participantes.filter(usuario=usuario).exists()


def cantidad_confirmados(encuentro: Encuentro) -> int:
    """Devuelve cuántos participantes confirmados tiene el encuentro (de 1 a 4)."""
    return encuentro.participantes.count()


def es_organizador(usuario: Usuario, encuentro: Encuentro) -> bool:
    """Indica si el usuario organiza el encuentro."""
    return encuentro.organizador_id == usuario.pk


@dataclass(frozen=True)
class JugadorRecomendado:
    """Un jugador recomendado y la franja suya que cubre el encuentro."""

    usuario: Usuario
    franja: Franja


@dataclass(frozen=True)
class JugadoresRecomendados:
    """Resultado de la recomendación para mostrar en la pantalla 10."""

    lugares_libres: int
    suficientes: bool
    jugadores: tuple[JugadorRecomendado, ...]


def ids_excluidos(encuentro: Encuentro) -> frozenset[int]:
    """Ids que no se pueden recomendar: organizador, participantes e invitados (en cualquier
    estado, porque un jugador no puede ser invitado dos veces al mismo encuentro)."""
    participantes = encuentro.participantes.values_list("usuario_id", flat=True)
    invitados = encuentro.invitaciones.values_list("usuario_invitado_id", flat=True)
    return frozenset({encuentro.organizador_id, *participantes, *invitados})


def _encuentro_entrada(encuentro: Encuentro) -> EncuentroEntrada:
    niveles = encuentro.participantes.values_list("usuario__nivel_estimado", flat=True)
    return EncuentroEntrada(
        fecha=encuentro.fecha,
        hora_inicio=encuentro.hora_inicio,
        duracion_minutos=encuentro.duracion_minutos,
        lat=float(encuentro.localidad.latitud),
        lon=float(encuentro.localidad.longitud),
        tipo=encuentro.tipo_encuentro,
        niveles_confirmados=tuple(float(nivel) for nivel in niveles.order_by("usuario_id")),
        ids_excluidos=ids_excluidos(encuentro),
    )


def _candidato_entrada(usuario: Usuario) -> CandidatoEntrada:
    localidad = usuario.localidad
    # Sin preferencia, la relación inversa lanza una excepción que también es AttributeError.
    preferencia = getattr(usuario, "preferencia", None)
    return CandidatoEntrada(
        id=usuario.pk,
        activo=usuario.is_active,
        disponible=usuario.disponible_para_invitaciones,
        nivel=None if usuario.nivel_estimado is None else float(usuario.nivel_estimado),
        lat=None if localidad is None else float(localidad.latitud),
        lon=None if localidad is None else float(localidad.longitud),
        tipo_preferido=None if preferencia is None else preferencia.tipo_encuentro,
        franjas=tuple(
            Franja(dia=franja.dia_semana, inicio=franja.hora_inicio, fin=franja.hora_fin)
            for franja in usuario.disponibilidades.all()
        ),
    )


def recomendar_jugadores(encuentro: Encuentro) -> JugadoresRecomendados:
    """Recomienda jugadores compatibles con el encuentro (HU-007).

    Arma las entradas del motor desde la base (nivel de referencia: los participantes
    confirmados, organizador incluido; excluidos: organizador, participantes e invitados) y
    llama a `motor.recomendar` con `Encuentro.lugares_libres()`. Devuelve los recomendados
    en el orden del motor, cada uno con la franja que cubre el encuentro, los lugares libres
    y si alcanzan. El ranking no se guarda: se recalcula en cada consulta.
    """
    entrada = _encuentro_entrada(encuentro)
    lugares_libres = encuentro.lugares_libres()
    usuarios = {usuario.pk: usuario for usuario in servicios_usuarios.candidatos_para_recomendar()}
    candidatos = {id_usuario: _candidato_entrada(u) for id_usuario, u in usuarios.items()}
    resultado = recomendar(entrada, tuple(candidatos.values()), lugares_libres)
    jugadores = tuple(
        JugadorRecomendado(
            usuario=usuarios[recomendacion.id],
            franja=franja_que_cubre(candidatos[recomendacion.id].franjas, entrada),
        )
        for recomendacion in resultado.recomendados
    )
    return JugadoresRecomendados(
        lugares_libres=lugares_libres, suficientes=resultado.suficientes, jugadores=jugadores
    )
