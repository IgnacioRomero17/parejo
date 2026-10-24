from datetime import time

import pytest
from django.db import IntegrityError

from tests.fabricas import crear_franja, crear_preferencia, crear_usuario

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("desde", "hasta"),
    [
        (time(19), time(17)),
        (time(17), time(17, 30)),
        (time(17, 15), time(19)),
        (time(17), time(19, 0, 30)),
    ],
)
def test_disponibilidad_la_base_rechaza_franjas_invalidas(desde, hasta):
    with pytest.raises(IntegrityError):
        crear_franja(crear_usuario(), hora_inicio=desde, hora_fin=hasta)


def test_disponibilidad_la_base_rechaza_un_dia_fuera_de_rango():
    with pytest.raises(IntegrityError):
        crear_franja(crear_usuario(), dia_semana=8)


def test_preferencia_la_base_admite_una_sola_por_usuario():
    usuario = crear_usuario()
    crear_preferencia(usuario)

    with pytest.raises(IntegrityError):
        crear_preferencia(usuario)


def test_preferencia_la_base_rechaza_valores_fuera_de_la_enumeracion():
    with pytest.raises(IntegrityError):
        crear_preferencia(crear_usuario(), lado_preferido="DERECHA")
