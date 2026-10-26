import json
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.comun.management.commands.cargar_datos import RUTA_DATASET
from apps.encuentros import servicios as servicios_encuentros
from apps.localidades.models import Localidad
from apps.usuarios import servicios as servicios_usuarios
from apps.usuarios.models import Usuario
from tests.fabricas import crear_encuentro, crear_usuario

pytestmark = pytest.mark.django_db

DATASET = json.loads(RUTA_DATASET.read_text(encoding="utf-8"))
CORREOS = {jugador["email"] for jugador in DATASET["jugadores"]}
CASO_EJEMPLO = ["Valentina", "Joaquín", "Camila", "Federico", "Bruno", "Agustina"]


@pytest.fixture(autouse=True)
def localidades():
    call_command("loaddata", "localidades", verbosity=0)


def cargar(*argumentos):
    call_command("cargar_datos", *argumentos, verbosity=0)


def jugadores_demo():
    return Usuario.objects.filter(email__in=CORREOS)


def test_cargar_datos_carga_jugadores_con_el_onboarding_completo():
    cargar()

    jugadores = list(jugadores_demo())
    assert 15 <= len(jugadores) <= 30
    assert len(jugadores) == len(DATASET["jugadores"])
    assert all(servicios_usuarios.paso_onboarding_pendiente(j) is None for j in jugadores)
    assert all(j.check_password(DATASET["contrasena"]) for j in jugadores)


def test_cargar_datos_incluye_a_los_jugadores_del_caso_de_ejemplo():
    cargar()

    esperado = {
        "Tomás": ("4.5", "Río Ceballos", "COMPETITIVO", "DRIVE"),
        "Valentina": ("4.5", "Río Ceballos", "COMPETITIVO", "REVES"),
        "Joaquín": ("4.5", "Unquillo", "COMPETITIVO", "DRIVE"),
        "Camila": ("5.0", "Mendiolaza", "COMPETITIVO", "REVES"),
        "Federico": ("5.0", "Villa Allende", "INDIFERENTE", "DRIVE"),
        "Bruno": ("4.0", "Salsipuedes", "RECREATIVO", "REVES"),
        "Agustina": ("5.0", "La Calera", "COMPETITIVO", "INDIFERENTE"),
    }
    for nombre, (nivel, localidad, tipo, lado) in esperado.items():
        jugador = jugadores_demo().get(nombre=nombre)
        assert jugador.nivel_estimado == Decimal(nivel)
        assert jugador.localidad.nombre == localidad
        assert jugador.preferencia.tipo_encuentro == tipo
        assert jugador.preferencia.lado_preferido == lado


def test_cargar_datos_frena_si_el_dataset_ya_esta_cargado():
    cargar()

    with pytest.raises(CommandError, match="--reemplazar"):
        cargar()


def test_cargar_datos_reemplazar_restaura_el_dataset_sin_tocar_otros_usuarios():
    cargar()
    manual = crear_usuario(email="cargado.a.mano@example.com", nombre="Manual")
    tomas = jugadores_demo().get(nombre="Tomás")
    tomas.nivel_estimado = Decimal("2.0")
    tomas.save()
    tomas.disponibilidades.all().delete()

    cargar("--reemplazar")

    tomas.refresh_from_db()
    assert tomas.nivel_estimado == Decimal("4.5")
    assert tomas.disponibilidades.count() == 2
    assert jugadores_demo().count() == len(DATASET["jugadores"])
    assert Usuario.objects.filter(pk=manual.pk, nombre="Manual").exists()


def test_cargar_datos_reemplazar_crea_los_que_faltan():
    cargar()
    jugadores_demo().get(nombre="Lucía").delete()

    cargar("--reemplazar")

    assert jugadores_demo().filter(nombre="Lucía").exists()


def test_cargar_datos_sin_el_catalogo_de_localidades_avisa():
    Localidad.objects.all().delete()

    with pytest.raises(CommandError, match="loaddata localidades"):
        cargar()
    assert not jugadores_demo().exists()


def test_cargar_datos_con_el_demo_se_recomienda_el_caso_de_ejemplo():
    cargar()
    tomas = jugadores_demo().get(nombre="Tomás")
    encuentro = crear_encuentro(tomas)  # próximo sábado, 18:00, 90 min, Competitivo

    resultado = servicios_encuentros.recomendar_jugadores(encuentro)

    assert [j.usuario.nombre for j in resultado.jugadores] == CASO_EJEMPLO
    assert resultado.suficientes
