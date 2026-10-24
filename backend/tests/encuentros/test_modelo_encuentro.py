from datetime import time

import pytest
from django.db import IntegrityError

from apps.encuentros.models import Participante
from tests.fabricas import crear_encuentro, crear_usuario_con_onboarding

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
