"""Encuentros activos del panel principal (pantalla 08, HU-012)."""

from datetime import UTC, datetime, time, timedelta

import pytest
from django.utils import timezone

from apps.encuentros import servicios
from apps.encuentros.models import EstadoInvitacion, Participante
from tests.fabricas import (
    crear_encuentro,
    crear_invitacion,
    crear_localidad,
    crear_usuario_con_onboarding,
    proximo_sabado,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def rio_ceballos():
    return crear_localidad()


@pytest.fixture
def usuario(rio_ceballos):
    return crear_usuario_con_onboarding(localidad=rio_ceballos, email="tomas@example.com")


@pytest.fixture
def otro(rio_ceballos):
    return crear_usuario_con_onboarding(localidad=rio_ceballos, email="lucia@example.com")


@pytest.fixture
def fijar_ahora(monkeypatch):
    """Fija `timezone.now()` en una fecha y hora de Córdoba."""

    def fijar(fecha, hora):
        ahora = datetime.combine(fecha, hora, tzinfo=timezone.get_default_timezone())
        monkeypatch.setattr(timezone, "now", lambda: ahora.astimezone(UTC))

    return fijar


def ids(encuentros) -> list[int]:
    return [encuentro.pk for encuentro in encuentros]


def test_hu012_incluye_los_que_organiza_y_los_que_acepto(usuario, otro):
    organizado = crear_encuentro(usuario)
    aceptado = crear_encuentro(otro, hora_inicio=time(20))
    crear_invitacion(aceptado, usuario, estado=EstadoInvitacion.ACEPTADA)
    Participante.objects.create(encuentro=aceptado, usuario=usuario)

    assert ids(servicios.encuentros_activos(usuario)) == [organizado.pk, aceptado.pk]


@pytest.mark.parametrize("estado", [EstadoInvitacion.PENDIENTE, EstadoInvitacion.RECHAZADA])
def test_hu012_no_incluye_invitaciones_sin_aceptar(usuario, otro, estado):
    encuentro = crear_encuentro(otro)
    crear_invitacion(encuentro, usuario, estado=estado)

    assert servicios.encuentros_activos(usuario) == ()


def test_hu012_no_incluye_encuentros_ajenos(usuario, otro):
    crear_encuentro(otro)

    assert servicios.encuentros_activos(usuario) == ()


def test_hu012_no_incluye_los_que_ya_comenzaron(usuario, fijar_ahora):
    sabado = proximo_sabado()
    crear_encuentro(usuario, fecha=sabado - timedelta(days=1), hora_inicio=time(20))
    crear_encuentro(usuario, fecha=sabado, hora_inicio=time(18))
    mas_tarde = crear_encuentro(usuario, fecha=sabado, hora_inicio=time(18, 30))
    fijar_ahora(sabado, time(18))

    assert ids(servicios.encuentros_activos(usuario)) == [mas_tarde.pk]


def test_hu012_los_ordena_por_fecha_y_hora_ascendentes(usuario):
    sabado = proximo_sabado()
    domingo = crear_encuentro(usuario, fecha=sabado + timedelta(days=1), hora_inicio=time(9))
    sabado_tarde = crear_encuentro(usuario, fecha=sabado, hora_inicio=time(20))
    sabado_temprano = crear_encuentro(usuario, fecha=sabado, hora_inicio=time(10))

    assert ids(servicios.encuentros_activos(usuario)) == [
        sabado_temprano.pk,
        sabado_tarde.pk,
        domingo.pk,
    ]


def test_hu012_cuenta_confirmados_e_invitaciones_pendientes(usuario, otro, rio_ceballos):
    encuentro = crear_encuentro(usuario)
    Participante.objects.create(encuentro=encuentro, usuario=otro)
    for numero in range(3):
        invitado = crear_usuario_con_onboarding(
            localidad=rio_ceballos, email=f"invitado{numero}@example.com"
        )
        estado = EstadoInvitacion.RECHAZADA if numero == 0 else EstadoInvitacion.PENDIENTE
        crear_invitacion(encuentro, invitado, estado=estado)

    [activo] = servicios.encuentros_activos(usuario)

    assert (activo.confirmados, activo.invitaciones_pendientes) == (2, 2)
    assert activo.organizador == usuario
