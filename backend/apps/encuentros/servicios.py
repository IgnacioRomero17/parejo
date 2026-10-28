from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Prefetch, Q, QuerySet
from django.utils import timezone

from apps.comun.errores import ErrorNegocio
from apps.comun.horarios import MENSAJE_HORA_INVALIDA, hora_valida, minutos
from apps.encuentros.models import (
    MINUTOS_FIN_MAXIMO,
    Combinacion,
    Encuentro,
    EstadoEncuentro,
    EstadoInvitacion,
    Invitacion,
    Pareja,
    ParejaIntegrante,
    Participante,
    PropuestaEncuentro,
)
from apps.usuarios import servicios as servicios_usuarios
from apps.usuarios.models import Usuario
from motor.equilibrio import elegir_mejor, evaluar_combinaciones
from motor.filtros import franja_que_cubre
from motor.parametros import PARAMETROS
from motor.recomendar import recomendar
from motor.tipos import (
    CandidatoEntrada,
    CombinacionResultado,
    EncuentroEntrada,
    Franja,
    JugadorEntrada,
)

MENSAJE_FIN_TARDE = "El encuentro tiene que terminar a las 23:30 como máximo."
MENSAJE_EN_EL_PASADO = "Elegí una fecha y hora futuras."
MENSAJE_FECHA_LEJANA = "Elegí una fecha dentro de los próximos 60 días."
DIAS_MAXIMOS_ANTICIPACION = 60
MENSAJE_SIN_ONBOARDING = "Completá tu perfil para continuar."
MENSAJE_ENCUENTRO_INEXISTENTE = "El encuentro no existe."
MENSAJE_INVITACION_INEXISTENTE = "La invitación no existe."
MENSAJE_YA_COMENZO = "Este encuentro ya comenzó."
MENSAJE_NO_BUSCA_PARTICIPANTES = "Este encuentro ya no está buscando participantes."
MENSAJE_MAS_QUE_LUGARES = "Seleccionaste más jugadores que lugares libres."
MENSAJE_JUGADOR_NO_DISPONIBLE = (
    "Alguno de los jugadores ya no está disponible para este encuentro. Actualizá la lista."
)
MENSAJE_INVITACION_RESPONDIDA = "Ya respondiste esta invitación."
MENSAJE_YA_TIENE_PROPUESTA = "Este encuentro ya tiene una propuesta."
MENSAJE_SIN_CUATRO_CONFIRMADOS = "El encuentro todavía no tiene 4 jugadores confirmados."
MENSAJE_SIN_PROPUESTA = "Este encuentro todavía no tiene una propuesta."
ID_MAXIMO = 2_147_483_647  # máximo de las columnas integer de id_encuentro e id_invitacion


def _inicio_en_cordoba(fecha: date, hora_inicio: time) -> datetime:
    # La fecha y la hora se interpretan en Córdoba, no en UTC: a las 22:00 de Córdoba ya es
    # el día siguiente en UTC y un encuentro de hoy a las 22:30 todavía es futuro.
    return datetime.combine(fecha, hora_inicio, tzinfo=timezone.get_default_timezone())


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
    ahora = timezone.now()
    hoy = timezone.localdate(ahora)
    if _inicio_en_cordoba(fecha, hora_inicio) <= ahora:
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


def _id_valido(id_objeto: int) -> bool:
    # Un id fuera del rango de la columna haría fallar la consulta en PostgreSQL.
    return 0 < id_objeto <= ID_MAXIMO


def obtener_encuentro(id_encuentro: int) -> Encuentro:
    """Devuelve el encuentro con ese id, con su localidad.

    Lanza ErrorNegocio 404 si no existe.
    """
    if not _id_valido(id_encuentro):
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


def ya_comenzo(encuentro: Encuentro) -> bool:
    """Indica si la fecha y hora de inicio del encuentro ya pasaron (en Córdoba)."""
    return _inicio_en_cordoba(encuentro.fecha, encuentro.hora_inicio) <= timezone.now()


def _bloquear_encuentro(id_encuentro: int) -> Encuentro:
    # `of` bloquea solo la fila del encuentro, no la de su localidad.
    return (
        Encuentro.objects.select_related("localidad")
        .select_for_update(of=("self",))
        .get(pk=id_encuentro)
    )


def _verificar_no_comenzo(encuentro: Encuentro) -> None:
    if ya_comenzo(encuentro):
        raise ErrorNegocio(MENSAJE_YA_COMENZO, estado=409)


def _verificar_busca_participantes(encuentro: Encuentro) -> None:
    if encuentro.estado != EstadoEncuentro.BUSCANDO_PARTICIPANTES:
        raise ErrorNegocio(MENSAJE_NO_BUSCA_PARTICIPANTES, estado=409)


def invitar_jugadores(encuentro: Encuentro, ids_usuarios: list[int]) -> list[Invitacion]:
    """Invita a los jugadores elegidos por el organizador (HU-008).

    Recibe el encuentro y los ids de los jugadores, en el orden en que se invitan. Con el
    encuentro bloqueado, verifica que no haya comenzado, que esté buscando participantes y que
    no se pidan más jugadores que lugares libres; después recalcula la recomendación con el
    motor y exige que cada id esté entre los recomendados (el motor ya excluye a los invitados
    antes, en cualquier estado). Crea una invitación pendiente por jugador, todas o ninguna.
    Devuelve las invitaciones creadas. Lanza ErrorNegocio 409 si el encuentro ya comenzó, si no
    busca participantes o si algún jugador no es recomendado, y 400 si se superan los lugares.
    """
    ids = list(dict.fromkeys(ids_usuarios))
    with transaction.atomic():
        encuentro = _bloquear_encuentro(encuentro.pk)
        _verificar_no_comenzo(encuentro)
        _verificar_busca_participantes(encuentro)
        if len(ids) > encuentro.lugares_libres():
            raise ErrorNegocio(MENSAJE_MAS_QUE_LUGARES)
        recomendados = {jugador.usuario.pk for jugador in recomendar_jugadores(encuentro).jugadores}
        if not recomendados.issuperset(ids):
            raise ErrorNegocio(MENSAJE_JUGADOR_NO_DISPONIBLE, estado=409)
        return Invitacion.objects.bulk_create(
            Invitacion(encuentro=encuentro, usuario_invitado_id=id_usuario) for id_usuario in ids
        )


def obtener_invitacion(id_invitacion: int) -> Invitacion:
    """Devuelve la invitación con ese id. Lanza ErrorNegocio 404 si no existe."""
    if not _id_valido(id_invitacion):
        raise ErrorNegocio(MENSAJE_INVITACION_INEXISTENTE, estado=404)
    invitacion = Invitacion.objects.filter(pk=id_invitacion).first()
    if invitacion is None:
        raise ErrorNegocio(MENSAJE_INVITACION_INEXISTENTE, estado=404)
    return invitacion


def es_invitado(usuario: Usuario, invitacion: Invitacion) -> bool:
    """Indica si la invitación fue enviada al usuario."""
    return invitacion.usuario_invitado_id == usuario.pk


def _bloquear_para_responder(invitacion: Invitacion) -> tuple[Encuentro, Invitacion]:
    # Siempre primero el encuentro y después la invitación: el mismo orden en aceptar,
    # rechazar e invitar evita bloqueos cruzados.
    encuentro = _bloquear_encuentro(invitacion.encuentro_id)
    invitacion = Invitacion.objects.select_for_update().get(pk=invitacion.pk)
    _verificar_no_comenzo(encuentro)
    if invitacion.estado != EstadoInvitacion.PENDIENTE:
        raise ErrorNegocio(MENSAJE_INVITACION_RESPONDIDA, estado=409)
    return encuentro, invitacion


def aceptar_invitacion(invitacion: Invitacion) -> Invitacion:
    """El invitado acepta la invitación y pasa a ser participante confirmado (HU-008).

    Con el encuentro y la invitación bloqueados, verifica que el encuentro no haya comenzado,
    que la invitación siga pendiente y que el encuentro busque participantes con menos de 4
    confirmados; así, de dos aceptaciones simultáneas del último lugar solo entra una. Marca
    la invitación como aceptada, registra al participante y, si llega a 4 confirmados, pasa el
    encuentro a COMPLETO. Devuelve la invitación con los datos de la bandeja. Lanza
    ErrorNegocio 409 si algo no se cumple.
    """
    with transaction.atomic():
        encuentro, invitacion = _bloquear_para_responder(invitacion)
        _verificar_busca_participantes(encuentro)
        confirmados = cantidad_confirmados(encuentro)
        if confirmados >= PARAMETROS.lugares_por_encuentro:
            raise ErrorNegocio(MENSAJE_NO_BUSCA_PARTICIPANTES, estado=409)
        invitacion.estado = EstadoInvitacion.ACEPTADA
        invitacion.fecha_respuesta = timezone.now()
        invitacion.save(update_fields=["estado", "fecha_respuesta"])
        Participante.objects.create(encuentro=encuentro, usuario_id=invitacion.usuario_invitado_id)
        if confirmados + 1 == PARAMETROS.lugares_por_encuentro:
            encuentro.estado = EstadoEncuentro.COMPLETO
            encuentro.save(update_fields=["estado"])
    return invitacion_recibida(invitacion)


def rechazar_invitacion(invitacion: Invitacion) -> Invitacion:
    """El invitado rechaza la invitación (HU-008).

    Con el encuentro y la invitación bloqueados, verifica que el encuentro no haya comenzado y
    que la invitación siga pendiente, y la marca como rechazada. El jugador no puede volver a
    ser invitado a ese encuentro. Devuelve la invitación con los datos de la bandeja. Lanza
    ErrorNegocio 409 si el encuentro ya comenzó o la invitación ya fue respondida.
    """
    with transaction.atomic():
        _, invitacion = _bloquear_para_responder(invitacion)
        invitacion.estado = EstadoInvitacion.RECHAZADA
        invitacion.fecha_respuesta = timezone.now()
        invitacion.save(update_fields=["estado", "fecha_respuesta"])
    return invitacion_recibida(invitacion)


@dataclass(frozen=True)
class DetalleEncuentro:
    """Lo que muestran las pantallas 12 y 14; `invitaciones` es None para quien no organiza."""

    encuentro: Encuentro
    lugares_libres: int
    participantes: tuple[Participante, ...]
    invitaciones: tuple[Invitacion, ...] | None


def detalle_encuentro(encuentro: Encuentro, usuario: Usuario) -> DetalleEncuentro:
    """Arma el seguimiento del encuentro (HU-008).

    Recibe el encuentro y el usuario que lo consulta, ya verificado como participante.
    Devuelve los lugares libres, los participantes confirmados en orden de confirmación y,
    solo si el usuario organiza el encuentro, las invitaciones en orden de envío.
    """
    participantes = encuentro.participantes.select_related(
        "usuario__localidad", "usuario__preferencia"
    ).order_by("fecha_confirmacion", "id_participante")
    invitaciones = None
    if es_organizador(usuario, encuentro):
        invitaciones = tuple(
            encuentro.invitaciones.select_related("usuario_invitado__localidad").order_by(
                "fecha_envio", "id_invitacion"
            )
        )
    return DetalleEncuentro(
        encuentro=encuentro,
        lugares_libres=encuentro.lugares_libres(),
        participantes=tuple(participantes),
        invitaciones=invitaciones,
    )


def _no_comenzo(prefijo: str = "") -> Q:
    # Condición de consulta equivalente a `not ya_comenzo(encuentro)`; `prefijo` lleva hasta el
    # encuentro desde otro modelo (por ejemplo, "encuentro__").
    ahora = timezone.localtime()
    return Q(**{f"{prefijo}fecha__gt": ahora.date()}) | Q(
        **{f"{prefijo}fecha": ahora.date(), f"{prefijo}hora_inicio__gt": ahora.time()}
    )


def encuentros_activos(usuario: Usuario) -> tuple[Encuentro, ...]:
    """Devuelve los encuentros activos del usuario para el panel principal (HU-012).

    Son los que organiza y aquellos a los que aceptó una invitación (en ambos casos es
    participante confirmado) cuya fecha y hora todavía no pasaron, ordenados por fecha y hora
    ascendentes. Cada uno trae su localidad, el organizador, `confirmados` e
    `invitaciones_pendientes` contados en la consulta.
    """
    # Por subconsulta y no con `participantes__usuario`: ese filtro reusaría la unión y el
    # conteo de confirmados daría siempre 1.
    propios = Participante.objects.filter(usuario=usuario).values("encuentro_id")
    pendientes = Q(invitaciones__estado=EstadoInvitacion.PENDIENTE)
    encuentros = (
        Encuentro.objects.filter(_no_comenzo(), pk__in=propios)
        .select_related("localidad", "organizador")
        .annotate(
            confirmados=Count("participantes", distinct=True),
            invitaciones_pendientes=Count("invitaciones", filter=pendientes, distinct=True),
        )
        .order_by("fecha", "hora_inicio", "id_encuentro")
    )
    return tuple(encuentros)


def _invitaciones_vigentes(usuario: Usuario) -> QuerySet[Invitacion]:
    # Las invitaciones de un encuentro que ya comenzó no se muestran ni se cuentan.
    return Invitacion.objects.filter(_no_comenzo("encuentro__"), usuario_invitado=usuario)


@dataclass(frozen=True)
class BandejaInvitaciones:
    """Invitaciones recibidas para la pantalla 13."""

    pendientes: tuple[Invitacion, ...]
    respondidas: tuple[Invitacion, ...]


def _con_datos_del_encuentro(invitaciones: QuerySet[Invitacion]) -> QuerySet[Invitacion]:
    encuentros = Encuentro.objects.select_related("localidad", "organizador").annotate(
        confirmados=Count("participantes")
    )
    return invitaciones.prefetch_related(Prefetch("encuentro", queryset=encuentros))


def bandeja_invitaciones(usuario: Usuario) -> BandejaInvitaciones:
    """Devuelve las invitaciones que recibió el usuario, de encuentros que no comenzaron (HU-008).

    Las pendientes van de la más reciente a la más antigua; las respondidas, de la última
    respondida a la primera. Cada una trae su encuentro, el organizador y los confirmados.
    """
    invitaciones = _con_datos_del_encuentro(_invitaciones_vigentes(usuario))
    pendientes = invitaciones.filter(estado=EstadoInvitacion.PENDIENTE).order_by(
        "-fecha_envio", "-id_invitacion"
    )
    respondidas = invitaciones.exclude(estado=EstadoInvitacion.PENDIENTE).order_by(
        "-fecha_respuesta", "-id_invitacion"
    )
    return BandejaInvitaciones(pendientes=tuple(pendientes), respondidas=tuple(respondidas))


def invitacion_recibida(invitacion: Invitacion) -> Invitacion:
    """Devuelve la invitación con los mismos datos que una de la bandeja."""
    return _con_datos_del_encuentro(Invitacion.objects.filter(pk=invitacion.pk)).get()


def cantidad_invitaciones_pendientes(usuario: Usuario) -> int:
    """Cuenta las invitaciones pendientes del usuario que muestra la bandeja (HU-008)."""
    return _invitaciones_vigentes(usuario).filter(estado=EstadoInvitacion.PENDIENTE).count()


@dataclass(frozen=True)
class ParejaDetalle:
    """Una pareja de la propuesta: su número, el promedio recalculado y sus 2 integrantes."""

    numero: int
    promedio: float
    integrantes: tuple[Usuario, ...]


@dataclass(frozen=True)
class CombinacionDetalle:
    """Una combinación evaluada: el puntaje guardado y los equilibrios recalculados."""

    numero: int
    puntaje_equilibrio: Decimal
    equilibrio_nivel: float
    equilibrio_lado: float
    parejas: tuple[ParejaDetalle, ...]


@dataclass(frozen=True)
class DetallePropuesta:
    """La propuesta del encuentro: las 3 combinaciones y cuál se eligió."""

    encuentro: Encuentro
    combinacion_elegida: int
    puntaje_equilibrio: Decimal
    combinaciones: tuple[CombinacionDetalle, ...]


def _jugador_entrada(usuario: Usuario) -> JugadorEntrada:
    # Sin preferencia, la relación inversa lanza una excepción que también es AttributeError.
    preferencia = getattr(usuario, "preferencia", None)
    return JugadorEntrada(
        id=usuario.pk,
        nivel=None if usuario.nivel_estimado is None else float(usuario.nivel_estimado),
        lado=None if preferencia is None else preferencia.lado_preferido,
    )


def _verificar_listo_para_parejas(encuentro: Encuentro) -> None:
    if encuentro.estado == EstadoEncuentro.PROPUESTA_GENERADA:
        raise ErrorNegocio(MENSAJE_YA_TIENE_PROPUESTA, estado=409)
    if encuentro.estado != EstadoEncuentro.COMPLETO or not encuentro.esta_completo():
        raise ErrorNegocio(MENSAJE_SIN_CUATRO_CONFIRMADOS, estado=409)


def _guardar_combinaciones(
    encuentro: Encuentro,
    resultados: tuple[CombinacionResultado, ...],
    participantes: dict[int, Participante],
) -> list[Combinacion]:
    # Una por una y en el orden del motor: la tabla no tiene número, se deduce del orden por id.
    combinaciones = []
    for resultado in resultados:
        combinacion = Combinacion.objects.create(
            encuentro=encuentro, puntaje_equilibrio=resultado.puntaje
        )
        for numero, ids_usuarios in ((1, resultado.pareja1), (2, resultado.pareja2)):
            pareja = Pareja.objects.create(combinacion=combinacion, numero=numero)
            ParejaIntegrante.objects.bulk_create(
                ParejaIntegrante(pareja=pareja, participante=participantes[id_usuario])
                for id_usuario in ids_usuarios
            )
        combinaciones.append(combinacion)
    return combinaciones


def formar_parejas(encuentro: Encuentro) -> DetallePropuesta:
    """Evalúa las combinaciones, forma las parejas y genera la propuesta (HU-009 a HU-011).

    Con el encuentro bloqueado, verifica que no haya comenzado, que esté COMPLETO y que tenga 4
    confirmados; así, de dos pedidos simultáneos solo uno genera la propuesta. Llama al motor
    con los 4 confirmados (id de usuario, nivel y lado actuales), guarda las 3 combinaciones en
    el orden 1, 2, 3 con su puntaje, sus parejas e integrantes, y la propuesta que apunta a la
    elegida; pasa el encuentro a PROPUESTA_GENERADA. Todo en una transacción. Devuelve el
    detalle de la propuesta. Lanza ErrorNegocio 409 si el encuentro ya comenzó, ya tiene
    propuesta o no tiene 4 confirmados.
    """
    with transaction.atomic():
        encuentro = _bloquear_encuentro(encuentro.pk)
        _verificar_no_comenzo(encuentro)
        _verificar_listo_para_parejas(encuentro)
        participantes = {
            participante.usuario_id: participante
            for participante in encuentro.participantes.select_related("usuario__preferencia")
        }
        resultados = evaluar_combinaciones(
            tuple(_jugador_entrada(participante.usuario) for participante in participantes.values())
        )
        elegida = elegir_mejor(resultados)
        combinaciones = _guardar_combinaciones(encuentro, resultados, participantes)
        PropuestaEncuentro.objects.create(
            encuentro=encuentro, combinacion=combinaciones[elegida.numero - 1]
        )
        encuentro.estado = EstadoEncuentro.PROPUESTA_GENERADA
        encuentro.save(update_fields=["estado"])
    return detalle_propuesta(encuentro)


def _combinaciones_guardadas(encuentro: Encuentro) -> list[Combinacion]:
    integrantes = ParejaIntegrante.objects.select_related(
        "participante__usuario__localidad", "participante__usuario__preferencia"
    ).order_by("participante__usuario_id")
    parejas = Pareja.objects.order_by("numero").prefetch_related(
        Prefetch("integrantes", queryset=integrantes)
    )
    return list(
        encuentro.combinaciones.order_by("id_combinacion").prefetch_related(
            Prefetch("parejas", queryset=parejas)
        )
    )


def _combinacion_detalle(
    numero: int, combinacion: Combinacion, resultado: CombinacionResultado
) -> CombinacionDetalle:
    promedios = (resultado.promedio1, resultado.promedio2)
    return CombinacionDetalle(
        numero=numero,
        puntaje_equilibrio=combinacion.puntaje_equilibrio,
        equilibrio_nivel=resultado.eq_nivel,
        equilibrio_lado=resultado.eq_lado,
        parejas=tuple(
            ParejaDetalle(
                numero=pareja.numero,
                promedio=promedios[pareja.numero - 1],
                integrantes=tuple(i.participante.usuario for i in pareja.integrantes.all()),
            )
            for pareja in combinacion.parejas.all()
        ),
    )


def obtener_propuesta(encuentro: Encuentro) -> DetallePropuesta:
    """Devuelve la propuesta del encuentro para la pantalla 16 (HU-012).

    Recibe el encuentro, ya verificado como del participante que la consulta. Devuelve el
    detalle de `detalle_propuesta`. Lanza ErrorNegocio 409 si el encuentro todavía no tiene
    propuesta.
    """
    if encuentro.estado != EstadoEncuentro.PROPUESTA_GENERADA:
        raise ErrorNegocio(MENSAJE_SIN_PROPUESTA, estado=409)
    return detalle_propuesta(encuentro)


def detalle_propuesta(encuentro: Encuentro) -> DetallePropuesta:
    """Arma la propuesta generada del encuentro para mostrarla (HU-011).

    Las combinaciones van en el orden en que se guardaron (1, 2, 3) con sus parejas e
    integrantes. El puntaje de cada una es el guardado; los promedios y los equilibrios de
    nivel y de lado se recalculan con el motor a partir del nivel y el lado actuales de cada
    jugador (limitación aceptada: si alguien cambia su nivel, pueden no coincidir con el
    puntaje). Devuelve también el número y el puntaje de la combinación elegida.
    """
    propuesta = PropuestaEncuentro.objects.get(encuentro=encuentro)
    combinaciones = _combinaciones_guardadas(encuentro)
    usuarios = {
        integrante.participante.usuario
        for pareja in combinaciones[0].parejas.all()
        for integrante in pareja.integrantes.all()
    }
    resultados = evaluar_combinaciones(tuple(_jugador_entrada(usuario) for usuario in usuarios))
    detalles = tuple(
        _combinacion_detalle(numero, combinacion, resultado)
        for numero, (combinacion, resultado) in enumerate(
            zip(combinaciones, resultados, strict=True), start=1
        )
    )
    elegida = next(
        detalle
        for detalle, combinacion in zip(detalles, combinaciones, strict=True)
        if combinacion.pk == propuesta.combinacion_id
    )
    return DetallePropuesta(
        encuentro=encuentro,
        combinacion_elegida=elegida.numero,
        puntaje_equilibrio=elegida.puntaje_equilibrio,
        combinaciones=detalles,
    )
