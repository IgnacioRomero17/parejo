from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection

from apps.comun.management.commands import reiniciar_demo
from apps.comun.management.commands.cargar_datos import leer_dataset
from apps.encuentros import servicios as servicios_encuentros
from apps.encuentros.models import (
    Combinacion,
    Encuentro,
    Invitacion,
    Pareja,
    ParejaIntegrante,
    Participante,
    PropuestaEncuentro,
)
from apps.localidades.models import Localidad
from apps.usuarios.models import Usuario
from tests.fabricas import (
    crear_encuentro,
    crear_encuentro_completo,
    crear_invitacion,
    crear_usuario,
)

pytestmark = pytest.mark.django_db

DATASET = leer_dataset()
CORREOS = {jugador["email"] for jugador in DATASET["jugadores"]}


@pytest.fixture(autouse=True)
def demo_cargada():
    call_command("loaddata", "localidades", verbosity=0)
    call_command("cargar_datos", verbosity=0)


def reiniciar(*argumentos) -> str:
    salida = StringIO()
    call_command("reiniciar_demo", *argumentos, stdout=salida)
    return salida.getvalue()


def jugador(nombre: str) -> Usuario:
    return Usuario.objects.get(email__in=CORREOS, nombre=nombre)


def crear_encuentros_de_prueba() -> None:
    """Un encuentro con propuesta formada y otro buscando participantes con invitaciones."""
    con_propuesta = crear_encuentro_completo(
        jugador("Tomás"), jugador("Valentina"), jugador("Camila"), jugador("Federico")
    )
    servicios_encuentros.formar_parejas(con_propuesta)
    buscando = crear_encuentro(jugador("Joaquín"))
    crear_invitacion(buscando, jugador("Bruno"))
    crear_invitacion(buscando, jugador("Agustina"))


def responder(monkeypatch, respuesta: str) -> None:
    monkeypatch.setattr("builtins.input", lambda _mensaje: respuesta)


def test_reiniciar_demo_borra_encuentros_con_invitaciones_participaciones_y_propuestas():
    crear_encuentros_de_prueba()
    ajeno = crear_usuario(email="ajeno@example.com")
    crear_encuentro(ajeno, localidad=Localidad.objects.first())

    reiniciar("--sin-confirmar")

    for modelo in (
        Encuentro,
        Invitacion,
        Participante,
        Combinacion,
        Pareja,
        ParejaIntegrante,
        PropuestaEncuentro,
    ):
        assert not modelo.objects.exists()
    assert Usuario.objects.filter(pk=ajeno.pk).exists()


def test_reiniciar_demo_restaura_los_perfiles_del_dataset():
    tomas = jugador("Tomás")
    tomas.nivel_estimado = Decimal("2.0")
    tomas.save()
    tomas.disponibilidades.all().delete()
    jugador("Lucía").delete()

    reiniciar("--sin-confirmar")

    tomas.refresh_from_db()
    assert tomas.nivel_estimado == Decimal("4.5")
    assert tomas.disponibilidades.count() == 2
    assert Usuario.objects.filter(email__in=CORREOS).count() == len(DATASET["jugadores"])


def test_reiniciar_demo_restaura_la_contrasena_comun():
    tomas = jugador("Tomás")
    tomas.set_password("otraclave123")
    tomas.save()

    reiniciar("--sin-confirmar")

    tomas.refresh_from_db()
    assert tomas.check_password(DATASET["contrasena"])


def test_reiniciar_demo_no_toca_localidades_superusuario_ni_cuentas_ajenas():
    administrador = Usuario.objects.create_superuser(
        email="admin@example.com", password="admin1234", nombre="Admin", apellido="Parejo"
    )
    ajeno = crear_usuario(email="ajeno@example.com", nombre="Ajeno", password="ajena1234")
    localidades = list(Localidad.objects.order_by("pk").values())

    reiniciar("--sin-confirmar")

    administrador.refresh_from_db()
    ajeno.refresh_from_db()
    assert administrador.is_superuser and administrador.check_password("admin1234")
    assert ajeno.nombre == "Ajeno" and ajeno.check_password("ajena1234")
    assert list(Localidad.objects.order_by("pk").values()) == localidades


def test_reiniciar_demo_si_no_se_responde_si_no_borra_nada(monkeypatch):
    crear_encuentros_de_prueba()
    responder(monkeypatch, "no")

    salida = reiniciar()

    assert "Cancelado" in salida
    assert Encuentro.objects.count() == 2
    assert PropuestaEncuentro.objects.count() == 1


def test_reiniciar_demo_confirmando_muestra_host_y_conteos_y_borra(monkeypatch):
    crear_encuentros_de_prueba()
    responder(monkeypatch, " SI ")

    salida = reiniciar()

    assert f"Base: {connection.settings_dict['HOST'] or 'localhost'}" in salida
    assert "Se van a borrar 2 encuentros, 2 invitaciones y 1 propuestas" in salida
    assert not Encuentro.objects.exists()


def test_reiniciar_demo_si_falla_la_carga_no_borra_nada(monkeypatch):
    crear_encuentros_de_prueba()

    def falla(reemplazar):
        raise CommandError("falla de prueba")

    monkeypatch.setattr(reiniciar_demo, "cargar_dataset", falla)

    with pytest.raises(CommandError, match="falla de prueba"):
        reiniciar("--sin-confirmar")
    assert Encuentro.objects.count() == 2
    assert PropuestaEncuentro.objects.count() == 1
