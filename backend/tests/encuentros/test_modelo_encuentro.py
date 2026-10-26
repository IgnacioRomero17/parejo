from datetime import time

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.encuentros.models import EstadoInvitacion, Invitacion, Participante
from tests.fabricas import (
    crear_encuentro,
    crear_invitacion,
    crear_usuario,
    crear_usuario_con_onboarding,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def organizador():
    return crear_usuario_con_onboarding()


def test_hu006_la_base_rechaza_un_participante_repetido(organizador):
    encuentro = crear_encuentro(organizador)

    with pytest.raises(IntegrityError, match="participante_unico"):
        Participante.objects.create(encuentro=encuentro, usuario=organizador)


@pytest.mark.parametrize("hora_inicio", [time(18, 15), time(18, 0, 30)])
def test_hu006_la_base_rechaza_horas_fuera_de_los_pasos(organizador, hora_inicio):
    with pytest.raises(IntegrityError, match="encuentro_paso_30"):
        crear_encuentro(organizador, hora_inicio=hora_inicio)


@pytest.mark.parametrize(("hora_inicio", "duracion"), [(time(22, 30), 90), (time(23), 60)])
def test_hu006_la_base_rechaza_encuentros_que_pasan_de_las_23_30(
    organizador, hora_inicio, duracion
):
    with pytest.raises(IntegrityError, match="encuentro_no_cruza_medianoche"):
        crear_encuentro(organizador, hora_inicio=hora_inicio, duracion_minutos=duracion)


def test_hu006_la_base_acepta_terminar_justo_a_las_23_30(organizador):
    encuentro = crear_encuentro(organizador, hora_inicio=time(22), duracion_minutos=90)

    assert encuentro.pk is not None


def test_hu007_p2_lugares_libres_con_solo_el_organizador(organizador):
    assert crear_encuentro(organizador).lugares_libres() == 3


def test_hu007_p2_lugares_libres_descuenta_confirmados_e_invitaciones_pendientes(organizador):
    encuentro = crear_encuentro(organizador)
    confirmado, pendiente, aceptada, rechazada = (
        crear_usuario(email=f"jugador{numero}@example.com") for numero in range(4)
    )
    Participante.objects.create(encuentro=encuentro, usuario=confirmado)
    crear_invitacion(encuentro, pendiente)
    crear_invitacion(encuentro, aceptada, estado=EstadoInvitacion.ACEPTADA)
    crear_invitacion(encuentro, rechazada, estado=EstadoInvitacion.RECHAZADA)

    # 4 − 2 confirmados − 1 pendiente; aceptadas y rechazadas no ocupan lugar.
    assert encuentro.lugares_libres() == 1


def test_hu008_la_base_rechaza_una_invitacion_repetida(organizador):
    encuentro = crear_encuentro(organizador)
    invitado = crear_usuario(email="invitado@example.com")
    crear_invitacion(encuentro, invitado, estado=EstadoInvitacion.RECHAZADA)

    with pytest.raises(IntegrityError, match="invitacion_unica"):
        crear_invitacion(encuentro, invitado)


@pytest.mark.parametrize(
    ("estado", "con_respuesta"),
    [(EstadoInvitacion.PENDIENTE, True), (EstadoInvitacion.ACEPTADA, False)],
)
def test_hu008_la_base_exige_fecha_de_respuesta_solo_si_no_esta_pendiente(
    organizador, estado, con_respuesta
):
    encuentro = crear_encuentro(organizador)
    invitado = crear_usuario(email="invitado@example.com")

    with pytest.raises(IntegrityError, match="invitacion_respuesta"):
        Invitacion.objects.create(
            encuentro=encuentro,
            usuario_invitado=invitado,
            estado=estado,
            fecha_respuesta=timezone.now() if con_respuesta else None,
        )
