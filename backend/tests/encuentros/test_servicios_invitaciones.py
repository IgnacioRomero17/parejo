import threading
from datetime import time, timedelta
from decimal import Decimal

import pytest
from django.db import connection
from django.utils import timezone

from apps.comun.errores import ErrorNegocio
from apps.encuentros import servicios
from apps.encuentros.models import (
    EstadoEncuentro,
    EstadoInvitacion,
    Invitacion,
    Participante,
)
from tests.fabricas import (
    crear_encuentro,
    crear_invitacion,
    crear_jugador_disponible,
    crear_localidad,
    crear_usuario_con_onboarding,
)

pytestmark = pytest.mark.django_db

MENSAJE_YA_COMENZO = "Este encuentro ya comenzó."
MENSAJE_NO_DISPONIBLE = (
    "Alguno de los jugadores ya no está disponible para este encuentro. Actualizá la lista."
)
MENSAJE_MAS_QUE_LUGARES = "Seleccionaste más jugadores que lugares libres."
MENSAJE_NO_BUSCA = "Este encuentro ya no está buscando participantes."
MENSAJE_RESPONDIDA = "Ya respondiste esta invitación."


@pytest.fixture
def rio_ceballos():
    return crear_localidad()


@pytest.fixture
def organizador(rio_ceballos):
    return crear_usuario_con_onboarding(
        localidad=rio_ceballos, email="tomas@example.com", nivel_estimado=Decimal("4.5")
    )


@pytest.fixture
def encuentro(organizador):
    return crear_encuentro(organizador)


def jugador(localidad, nombre, **campos):
    datos = {"nombre": nombre.capitalize(), "nivel_estimado": Decimal("4.5"), **campos}
    return crear_jugador_disponible(localidad, f"{nombre}@example.com", **datos)


def ayer():
    return timezone.localdate() - timedelta(days=1)


def confirmar(encuentro, *usuarios):
    for usuario in usuarios:
        Participante.objects.create(encuentro=encuentro, usuario=usuario)


def error_de(funcion, *argumentos) -> ErrorNegocio:
    with pytest.raises(ErrorNegocio) as error:
        funcion(*argumentos)
    return error.value


# Invitar


def test_hu008_c1_registra_cada_invitacion_pendiente_asociada_al_encuentro(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    joaquin = jugador(rio_ceballos, "joaquin")

    invitaciones = servicios.invitar_jugadores(encuentro, [joaquin.pk, valentina.pk])

    assert [invitacion.usuario_invitado_id for invitacion in invitaciones] == [
        joaquin.pk,
        valentina.pk,
    ]
    guardadas = Invitacion.objects.filter(encuentro=encuentro)
    assert {invitacion.usuario_invitado_id for invitacion in guardadas} == {
        joaquin.pk,
        valentina.pk,
    }
    assert all(invitacion.estado == EstadoInvitacion.PENDIENTE for invitacion in guardadas)
    assert all(invitacion.fecha_respuesta is None for invitacion in guardadas)
    assert encuentro.lugares_libres() == 1


def test_hu008_p2_no_puede_invitar_mas_jugadores_que_lugares_libres(encuentro, rio_ceballos):
    jugadores = [jugador(rio_ceballos, nombre) for nombre in ("ana", "bea", "caro", "dani")]
    crear_invitacion(encuentro, jugadores[0])

    error = error_de(
        servicios.invitar_jugadores, encuentro, [usuario.pk for usuario in jugadores[1:]]
    )

    assert (error.mensaje, error.estado) == (MENSAJE_MAS_QUE_LUGARES, 400)
    assert Invitacion.objects.count() == 1


@pytest.mark.parametrize(
    "estado", [EstadoInvitacion.PENDIENTE, EstadoInvitacion.ACEPTADA, EstadoInvitacion.RECHAZADA]
)
def test_hu008_p3_no_puede_invitar_dos_veces_al_mismo_jugador(encuentro, rio_ceballos, estado):
    valentina = jugador(rio_ceballos, "valentina")
    crear_invitacion(encuentro, valentina, estado=estado)

    error = error_de(servicios.invitar_jugadores, encuentro, [valentina.pk])

    assert (error.mensaje, error.estado) == (MENSAJE_NO_DISPONIBLE, 409)
    assert Invitacion.objects.count() == 1


def test_hu008_recalcula_y_rechaza_a_quien_dejo_de_estar_disponible(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    valentina.disponible_para_invitaciones = False
    valentina.save(update_fields=["disponible_para_invitaciones"])

    error = error_de(servicios.invitar_jugadores, encuentro, [valentina.pk])

    assert (error.mensaje, error.estado) == (MENSAJE_NO_DISPONIBLE, 409)


def test_hu008_rechaza_a_un_jugador_que_no_es_recomendado(encuentro, rio_ceballos):
    otro_nivel = jugador(rio_ceballos, "otro", nivel_estimado=Decimal("6.5"))

    error = error_de(servicios.invitar_jugadores, encuentro, [otro_nivel.pk])

    assert (error.mensaje, error.estado) == (MENSAJE_NO_DISPONIBLE, 409)


def test_hu008_rechaza_al_organizador_y_a_un_id_inexistente(encuentro, organizador):
    for id_usuario in (organizador.pk, 999_999):
        error = error_de(servicios.invitar_jugadores, encuentro, [id_usuario])
        assert (error.mensaje, error.estado) == (MENSAJE_NO_DISPONIBLE, 409)


def test_hu008_si_uno_no_es_recomendado_no_crea_ninguna_invitacion(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    otro_nivel = jugador(rio_ceballos, "otro", nivel_estimado=Decimal("6.5"))

    error_de(servicios.invitar_jugadores, encuentro, [valentina.pk, otro_nivel.pk])

    assert not Invitacion.objects.exists()


def test_hu008_p6_no_puede_invitar_si_el_encuentro_ya_comenzo(organizador, rio_ceballos):
    encuentro = crear_encuentro(organizador, fecha=ayer())
    valentina = jugador(rio_ceballos, "valentina")

    error = error_de(servicios.invitar_jugadores, encuentro, [valentina.pk])

    assert (error.mensaje, error.estado) == (MENSAJE_YA_COMENZO, 409)


@pytest.mark.parametrize("estado", [EstadoEncuentro.COMPLETO, EstadoEncuentro.PROPUESTA_GENERADA])
def test_hu008_no_puede_invitar_si_el_encuentro_no_busca_participantes(
    organizador, rio_ceballos, estado
):
    encuentro = crear_encuentro(organizador, estado=estado)
    valentina = jugador(rio_ceballos, "valentina")

    error = error_de(servicios.invitar_jugadores, encuentro, [valentina.pk])

    assert (error.mensaje, error.estado) == (MENSAJE_NO_BUSCA, 409)


# Aceptar y rechazar


def test_hu008_c3_al_aceptar_queda_aceptada_y_es_participante_confirmado(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    invitacion = crear_invitacion(encuentro, valentina)

    servicios.aceptar_invitacion(invitacion)

    invitacion.refresh_from_db()
    assert invitacion.estado == EstadoInvitacion.ACEPTADA
    assert invitacion.fecha_respuesta is not None
    assert servicios.es_participante(valentina, encuentro)
    encuentro.refresh_from_db()
    assert encuentro.estado == EstadoEncuentro.BUSCANDO_PARTICIPANTES
    assert servicios.cantidad_confirmados(encuentro) == 2


def test_hu008_c3_al_rechazar_queda_rechazada_y_no_participa(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    invitacion = crear_invitacion(encuentro, valentina)

    servicios.rechazar_invitacion(invitacion)

    invitacion.refresh_from_db()
    assert invitacion.estado == EstadoInvitacion.RECHAZADA
    assert invitacion.fecha_respuesta is not None
    assert not servicios.es_participante(valentina, encuentro)
    assert encuentro.lugares_libres() == 3


def test_hu008_p4_con_el_cuarto_confirmado_el_encuentro_pasa_a_completo(encuentro, rio_ceballos):
    confirmar(encuentro, jugador(rio_ceballos, "ana"), jugador(rio_ceballos, "bea"))
    invitacion = crear_invitacion(encuentro, jugador(rio_ceballos, "caro"))

    servicios.aceptar_invitacion(invitacion)

    encuentro.refresh_from_db()
    assert encuentro.estado == EstadoEncuentro.COMPLETO
    assert servicios.cantidad_confirmados(encuentro) == 4


@pytest.mark.parametrize("estado", [EstadoInvitacion.ACEPTADA, EstadoInvitacion.RECHAZADA])
@pytest.mark.parametrize("responder", ["aceptar_invitacion", "rechazar_invitacion"])
def test_hu008_no_se_puede_responder_dos_veces(encuentro, rio_ceballos, estado, responder):
    invitacion = crear_invitacion(encuentro, jugador(rio_ceballos, "valentina"), estado=estado)

    error = error_de(getattr(servicios, responder), invitacion)

    assert (error.mensaje, error.estado) == (MENSAJE_RESPONDIDA, 409)
    invitacion.refresh_from_db()
    assert invitacion.estado == estado


@pytest.mark.parametrize("responder", ["aceptar_invitacion", "rechazar_invitacion"])
def test_hu008_p6_no_se_puede_responder_si_el_encuentro_ya_comenzo(
    organizador, rio_ceballos, responder
):
    encuentro = crear_encuentro(organizador, fecha=ayer())
    invitacion = crear_invitacion(encuentro, jugador(rio_ceballos, "valentina"))

    error = error_de(getattr(servicios, responder), invitacion)

    assert (error.mensaje, error.estado) == (MENSAJE_YA_COMENZO, 409)
    invitacion.refresh_from_db()
    assert invitacion.estado == EstadoInvitacion.PENDIENTE


def test_hu008_no_se_puede_aceptar_si_ya_hay_cuatro_confirmados(encuentro, rio_ceballos):
    # No debería pasar (una pendiente siempre tiene su lugar), pero el backend lo verifica.
    confirmar(encuentro, *(jugador(rio_ceballos, nombre) for nombre in ("ana", "bea", "caro")))
    invitacion = crear_invitacion(encuentro, jugador(rio_ceballos, "dani"))

    error = error_de(servicios.aceptar_invitacion, invitacion)

    assert (error.mensaje, error.estado) == (MENSAJE_NO_BUSCA, 409)
    assert servicios.cantidad_confirmados(encuentro) == 4


@pytest.mark.django_db(transaction=True)
def test_hu008_p4_dos_aceptaciones_simultaneas_del_ultimo_lugar(encuentro, rio_ceballos):
    confirmar(encuentro, jugador(rio_ceballos, "ana"), jugador(rio_ceballos, "bea"))
    # Dos pendientes para un solo lugar: el estado que se daría si dos pedidos se cruzaran.
    invitaciones = [
        crear_invitacion(encuentro, jugador(rio_ceballos, nombre)) for nombre in ("caro", "dani")
    ]
    barrera = threading.Barrier(len(invitaciones))
    resultados = []

    def aceptar(invitacion):
        try:
            barrera.wait()
            servicios.aceptar_invitacion(invitacion)
            resultados.append("aceptada")
        except ErrorNegocio as error:
            resultados.append(error.estado)
        finally:
            connection.close()

    hilos = [threading.Thread(target=aceptar, args=(invitacion,)) for invitacion in invitaciones]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    assert sorted(resultados, key=str) == [409, "aceptada"]
    encuentro.refresh_from_db()
    assert encuentro.estado == EstadoEncuentro.COMPLETO
    assert servicios.cantidad_confirmados(encuentro) == 4
    estados = sorted(Invitacion.objects.values_list("estado", flat=True))
    assert estados == [EstadoInvitacion.ACEPTADA, EstadoInvitacion.PENDIENTE]


# Seguimiento del encuentro


def test_hu008_el_detalle_muestra_participantes_e_invitaciones_al_organizador(
    encuentro, organizador, rio_ceballos
):
    valentina = jugador(rio_ceballos, "valentina")
    joaquin = jugador(rio_ceballos, "joaquin")
    crear_invitacion(encuentro, valentina, estado=EstadoInvitacion.ACEPTADA)
    confirmar(encuentro, valentina)
    crear_invitacion(encuentro, joaquin)

    detalle = servicios.detalle_encuentro(encuentro, organizador)

    assert [p.usuario_id for p in detalle.participantes] == [organizador.pk, valentina.pk]
    assert [i.usuario_invitado_id for i in detalle.invitaciones] == [valentina.pk, joaquin.pk]
    assert detalle.lugares_libres == 1


def test_hu008_el_detalle_no_muestra_invitaciones_a_otro_participante(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    confirmar(encuentro, valentina)

    assert servicios.detalle_encuentro(encuentro, valentina).invitaciones is None


# Bandeja


def test_hu008_c2_la_bandeja_trae_la_informacion_del_encuentro(
    encuentro, organizador, rio_ceballos
):
    valentina = jugador(rio_ceballos, "valentina")
    crear_invitacion(encuentro, valentina)

    bandeja = servicios.bandeja_invitaciones(valentina)

    (pendiente,) = bandeja.pendientes
    assert bandeja.respondidas == ()
    assert pendiente.encuentro == encuentro
    assert pendiente.encuentro.organizador == organizador
    assert pendiente.encuentro.confirmados == 1


def test_hu008_la_bandeja_separa_y_ordena_pendientes_y_respondidas(organizador, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    ahora = timezone.now()
    encuentros = [crear_encuentro(organizador) for _ in range(4)]
    vieja = crear_invitacion(encuentros[0], valentina, fecha_envio=ahora - timedelta(hours=2))
    nueva = crear_invitacion(encuentros[1], valentina, fecha_envio=ahora - timedelta(hours=1))
    aceptada = crear_invitacion(
        encuentros[2],
        valentina,
        estado=EstadoInvitacion.ACEPTADA,
        fecha_respuesta=ahora - timedelta(hours=3),
    )
    rechazada = crear_invitacion(
        encuentros[3],
        valentina,
        estado=EstadoInvitacion.RECHAZADA,
        fecha_respuesta=ahora - timedelta(minutes=5),
    )

    bandeja = servicios.bandeja_invitaciones(valentina)

    assert [i.pk for i in bandeja.pendientes] == [nueva.pk, vieja.pk]
    assert [i.pk for i in bandeja.respondidas] == [rechazada.pk, aceptada.pk]


def test_hu008_p6_la_bandeja_no_muestra_encuentros_que_ya_comenzaron(organizador, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    crear_invitacion(crear_encuentro(organizador, fecha=ayer()), valentina)
    crear_invitacion(
        crear_encuentro(organizador, fecha=ayer()), valentina, estado=EstadoInvitacion.ACEPTADA
    )

    bandeja = servicios.bandeja_invitaciones(valentina)

    assert bandeja.pendientes == ()
    assert bandeja.respondidas == ()
    assert servicios.cantidad_invitaciones_pendientes(valentina) == 0


def test_hu008_la_bandeja_muestra_un_encuentro_de_hoy_que_todavia_no_empezo(
    organizador, rio_ceballos
):
    ahora = timezone.localtime()
    if ahora.hour >= 22:
        pytest.skip("después de las 22:00 no queda un horario válido más tarde en el día")
    valentina = jugador(rio_ceballos, "valentina")
    encuentro = crear_encuentro(
        organizador, fecha=ahora.date(), hora_inicio=time(ahora.hour + 1), duracion_minutos=60
    )
    crear_invitacion(encuentro, valentina)

    assert len(servicios.bandeja_invitaciones(valentina).pendientes) == 1


def test_hu008_cuenta_solo_las_invitaciones_pendientes_propias(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina")
    otro = jugador(rio_ceballos, "otro")
    crear_invitacion(encuentro, valentina)
    crear_invitacion(encuentro, otro)
    crear_invitacion(
        crear_encuentro(encuentro.organizador), valentina, estado=EstadoInvitacion.RECHAZADA
    )

    assert servicios.cantidad_invitaciones_pendientes(valentina) == 1


def test_hu008_ya_comenzo_segun_la_fecha_y_hora_de_inicio(organizador):
    manana = timezone.localdate() + timedelta(days=1)

    assert servicios.ya_comenzo(crear_encuentro(organizador, fecha=ayer()))
    assert not servicios.ya_comenzo(crear_encuentro(organizador, fecha=manana))
