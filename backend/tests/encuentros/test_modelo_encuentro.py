from datetime import time
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.encuentros.models import (
    Combinacion,
    EstadoInvitacion,
    Invitacion,
    Pareja,
    ParejaIntegrante,
    Participante,
    PropuestaEncuentro,
)
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


def test_hu009_esta_completo_con_cuatro_confirmados(organizador):
    encuentro = crear_encuentro(organizador)
    for numero in range(3):
        assert not encuentro.esta_completo()
        Participante.objects.create(
            encuentro=encuentro, usuario=crear_usuario(email=f"jugador{numero}@example.com")
        )

    assert encuentro.esta_completo()


@pytest.mark.parametrize("puntaje", [Decimal("-0.0001"), Decimal("1.0001")])
def test_hu009_la_base_rechaza_un_puntaje_fuera_de_0_a_1(organizador, puntaje):
    encuentro = crear_encuentro(organizador)

    with pytest.raises(IntegrityError, match="combinacion_puntaje_valido"):
        Combinacion.objects.create(encuentro=encuentro, puntaje_equilibrio=puntaje)


def test_hu009_la_base_rechaza_un_numero_de_pareja_invalido(organizador):
    combinacion = Combinacion.objects.create(
        encuentro=crear_encuentro(organizador), puntaje_equilibrio=Decimal("1")
    )

    with pytest.raises(IntegrityError, match="pareja_numero_valido"):
        Pareja.objects.create(combinacion=combinacion, numero=3)


def test_hu009_la_base_rechaza_dos_parejas_con_el_mismo_numero(organizador):
    combinacion = Combinacion.objects.create(
        encuentro=crear_encuentro(organizador), puntaje_equilibrio=Decimal("1")
    )
    Pareja.objects.create(combinacion=combinacion, numero=1)

    with pytest.raises(IntegrityError, match="pareja_numero_unico"):
        Pareja.objects.create(combinacion=combinacion, numero=1)


def test_hu009_la_base_rechaza_un_integrante_repetido_en_la_pareja(organizador):
    encuentro = crear_encuentro(organizador)
    combinacion = Combinacion.objects.create(encuentro=encuentro, puntaje_equilibrio=Decimal("1"))
    pareja = Pareja.objects.create(combinacion=combinacion, numero=1)
    participante = encuentro.participantes.get()
    ParejaIntegrante.objects.create(pareja=pareja, participante=participante)

    with pytest.raises(IntegrityError, match="pareja_integrante_pkey"):
        ParejaIntegrante.objects.create(pareja=pareja, participante=participante)


def test_hu011_la_base_rechaza_una_segunda_propuesta_para_el_encuentro(organizador):
    encuentro = crear_encuentro(organizador)
    primera, segunda = (
        Combinacion.objects.create(encuentro=encuentro, puntaje_equilibrio=Decimal("1"))
        for _ in range(2)
    )
    PropuestaEncuentro.objects.create(encuentro=encuentro, combinacion=primera)

    with pytest.raises(IntegrityError, match="id_encuentro"):
        PropuestaEncuentro.objects.create(encuentro=encuentro, combinacion=segunda)
