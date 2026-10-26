from datetime import time
from decimal import Decimal

import pytest

from apps.encuentros import servicios
from apps.encuentros.models import EstadoInvitacion, Participante
from apps.usuarios.models import DiaSemana, TipoEncuentro
from motor.tipos import Franja
from tests.fabricas import (
    crear_encuentro,
    crear_franja,
    crear_invitacion,
    crear_jugador_disponible,
    crear_localidad,
    crear_usuario_con_onboarding,
)

pytestmark = pytest.mark.django_db


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
    return crear_jugador_disponible(localidad, f"{nombre}@example.com", nombre=nombre, **campos)


def ids(resultado):
    return [recomendado.usuario.pk for recomendado in resultado.jugadores]


def test_hu007_c1_genera_la_lista_de_recomendados(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina", nivel_estimado=Decimal("4.5"))

    resultado = servicios.recomendar_jugadores(encuentro)

    assert ids(resultado) == [valentina.pk]
    assert resultado.lugares_libres == 3


def test_hu007_c2_aplica_los_criterios_de_compatibilidad(encuentro, rio_ceballos):
    lejana = crear_localidad(nombre="Lejana", latitud=Decimal("-31.9"), longitud=Decimal("-64.3"))
    compatible = jugador(rio_ceballos, "compatible", nivel_estimado=Decimal("4.5"))
    jugador(rio_ceballos, "otro_nivel", nivel_estimado=Decimal("6.0"))
    jugador(lejana, "lejos", nivel_estimado=Decimal("4.5"))
    sin_horario = jugador(rio_ceballos, "sin_horario", nivel_estimado=Decimal("4.5"))
    sin_horario.disponibilidades.update(dia_semana=DiaSemana.DOMINGO)

    assert ids(servicios.recomendar_jugadores(encuentro)) == [compatible.pk]


def test_hu007_c3_ordena_por_puntaje_de_compatibilidad(encuentro, rio_ceballos):
    mismo_nivel = jugador(rio_ceballos, "mismo", nivel_estimado=Decimal("4.5"))
    medio_punto = jugador(rio_ceballos, "medio", nivel_estimado=Decimal("5.0"))

    assert ids(servicios.recomendar_jugadores(encuentro)) == [mismo_nivel.pk, medio_punto.pk]


def test_hu007_c4_informa_cuando_no_hay_suficientes(encuentro, rio_ceballos):
    jugador(rio_ceballos, "unico", nivel_estimado=Decimal("4.5"))

    resultado = servicios.recomendar_jugadores(encuentro)

    assert len(resultado.jugadores) == 1
    assert not resultado.suficientes


def test_hu007_c4_sin_candidatos_la_lista_esta_vacia(encuentro):
    resultado = servicios.recomendar_jugadores(encuentro)

    assert resultado.jugadores == ()
    assert not resultado.suficientes


def test_hu007_p2_suficientes_cuando_alcanzan_los_lugares_libres(encuentro, rio_ceballos):
    for nombre in ("ana", "bea", "caro"):
        jugador(rio_ceballos, nombre, nivel_estimado=Decimal("4.5"))

    assert servicios.recomendar_jugadores(encuentro).suficientes


def test_hu007_p2_las_invitaciones_pendientes_ocupan_lugar(encuentro, rio_ceballos):
    invitado = jugador(rio_ceballos, "invitado", nivel_estimado=Decimal("4.5"))
    otro = jugador(rio_ceballos, "otro", nivel_estimado=Decimal("4.5"))
    crear_invitacion(encuentro, invitado)

    resultado = servicios.recomendar_jugadores(encuentro)

    assert resultado.lugares_libres == 2
    assert ids(resultado) == [otro.pk]


def test_hu007_p4_el_nivel_de_referencia_es_el_promedio_de_los_confirmados(encuentro, rio_ceballos):
    cuatro_y_medio = jugador(rio_ceballos, "cuatro", nivel_estimado=Decimal("4.5"))
    cinco = jugador(rio_ceballos, "cinco", nivel_estimado=Decimal("5.0"))
    confirmado = jugador(rio_ceballos, "confirmado", nivel_estimado=Decimal("5.5"))
    assert ids(servicios.recomendar_jugadores(encuentro))[:2] == [cuatro_y_medio.pk, cinco.pk]

    Participante.objects.create(encuentro=encuentro, usuario=confirmado)

    # Promedio de 4,5 y 5,5: 5,0.
    assert ids(servicios.recomendar_jugadores(encuentro)) == [cinco.pk, cuatro_y_medio.pk]


@pytest.mark.parametrize(
    "estado",
    [EstadoInvitacion.PENDIENTE, EstadoInvitacion.ACEPTADA, EstadoInvitacion.RECHAZADA],
)
def test_hu007_excluye_a_los_invitados_en_cualquier_estado(encuentro, rio_ceballos, estado):
    invitado = jugador(rio_ceballos, "invitado", nivel_estimado=Decimal("4.5"))
    crear_invitacion(encuentro, invitado, estado=estado)

    assert ids(servicios.recomendar_jugadores(encuentro)) == []


def test_hu007_excluye_al_organizador_y_a_los_participantes(encuentro, organizador, rio_ceballos):
    organizador.disponible_para_invitaciones = True
    organizador.save()
    crear_franja(organizador)
    participante = jugador(rio_ceballos, "participante", nivel_estimado=Decimal("4.5"))
    Participante.objects.create(encuentro=encuentro, usuario=participante)

    assert ids(servicios.recomendar_jugadores(encuentro)) == []


def test_hu007_excluye_no_disponibles_inactivos_y_perfiles_incompletos(encuentro, rio_ceballos):
    jugador(rio_ceballos, "no_disponible", disponible_para_invitaciones=False)
    jugador(rio_ceballos, "inactivo", is_active=False)
    sin_localidad = jugador(rio_ceballos, "sin_localidad")
    sin_localidad.localidad = None
    sin_localidad.save()

    assert ids(servicios.recomendar_jugadores(encuentro)) == []


def test_hu007_p5_el_ranking_se_recalcula_en_cada_consulta(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina", nivel_estimado=Decimal("4.5"))
    assert ids(servicios.recomendar_jugadores(encuentro)) == [valentina.pk]

    valentina.disponible_para_invitaciones = False
    valentina.save()

    assert ids(servicios.recomendar_jugadores(encuentro)) == []


def test_hu007_devuelve_la_franja_que_cubre_el_encuentro(encuentro, rio_ceballos):
    valentina = jugador(rio_ceballos, "valentina", nivel_estimado=Decimal("4.5"))
    crear_franja(valentina, dia_semana=DiaSemana.MARTES, hora_inicio=time(9), hora_fin=time(12))

    recomendado = servicios.recomendar_jugadores(encuentro).jugadores[0]

    assert recomendado.franja == Franja(dia=6, inicio=time(17), fin=time(21))


def test_hu007_usa_el_tipo_de_encuentro(organizador, rio_ceballos):
    recreativo = crear_encuentro(organizador, tipo_encuentro=TipoEncuentro.RECREATIVO)
    # Mismo nivel y lugar, tipo opuesto: 0,6 + 0,3 + 0 = 0,9; sigue arriba del umbral.
    valentina = jugador(rio_ceballos, "valentina", nivel_estimado=Decimal("4.5"))
    # Medio punto y tipo opuesto: 0,3 + 0,3 + 0 = 0,6.
    camila = jugador(rio_ceballos, "camila", nivel_estimado=Decimal("5.0"))
    # Un punto y tipo opuesto: 0 + 0,3 + 0 = 0,3; queda afuera.
    jugador(rio_ceballos, "lejos_de_nivel", nivel_estimado=Decimal("5.5"))

    assert ids(servicios.recomendar_jugadores(recreativo)) == [valentina.pk, camila.pk]


def test_hu007_ids_excluidos(encuentro, organizador, rio_ceballos):
    participante = jugador(rio_ceballos, "participante")
    invitado = jugador(rio_ceballos, "invitado")
    Participante.objects.create(encuentro=encuentro, usuario=participante)
    crear_invitacion(encuentro, invitado, estado=EstadoInvitacion.RECHAZADA)

    assert servicios.ids_excluidos(encuentro) == {organizador.pk, participante.pk, invitado.pk}
