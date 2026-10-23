from decimal import Decimal

import pytest

from apps.usuarios.models import FrecuenciaJuego, Genero, Usuario
from apps.usuarios.servicios import actualizar_perfil, paso_onboarding_pendiente
from tests.fabricas import crear_localidad, crear_usuario, crear_usuario_con_perfil

pytestmark = pytest.mark.django_db


def perfil_deportivo(localidad, **campos) -> dict:
    datos = {
        "edad": 34,
        "genero": Genero.MASCULINO,
        "localidad": localidad,
        "frecuencia_juego": FrecuenciaJuego.DOS_TRES_SEMANA,
        "nivel_estimado": Decimal("4.5"),
    }
    datos.update(campos)
    return datos


def test_hu004_completa_el_perfil_en_el_primer_ingreso():
    usuario = crear_usuario()
    localidad = crear_localidad()

    actualizar_perfil(usuario, perfil_deportivo=perfil_deportivo(localidad))

    guardado = Usuario.objects.get(pk=usuario.pk)
    assert guardado.edad == 34
    assert guardado.genero == Genero.MASCULINO
    assert guardado.localidad == localidad
    assert guardado.frecuencia_juego == FrecuenciaJuego.DOS_TRES_SEMANA
    assert guardado.nivel_estimado == Decimal("4.5")
    assert guardado.perfil_completo


def test_hu004_c3_actualiza_el_perfil_ya_registrado():
    usuario = crear_usuario_con_perfil()
    otra_localidad = crear_localidad(nombre="Unquillo")

    actualizar_perfil(
        usuario,
        perfil_deportivo=perfil_deportivo(otra_localidad, nivel_estimado=Decimal("5.0")),
    )

    guardado = Usuario.objects.get(pk=usuario.pk)
    assert guardado.localidad == otra_localidad
    assert guardado.nivel_estimado == Decimal("5.0")


def test_hu004_c3_actualiza_nombre_y_apellido_sin_tocar_el_perfil_deportivo():
    usuario = crear_usuario_con_perfil()

    actualizar_perfil(usuario, datos_personales={"nombre": "Valentina", "apellido": "Sosa"})

    guardado = Usuario.objects.get(pk=usuario.pk)
    assert (guardado.nombre, guardado.apellido) == ("Valentina", "Sosa")
    assert guardado.nivel_estimado == Decimal("4.0")
    assert guardado.edad == 30


def test_hu004_c3_guarda_las_dos_secciones_juntas():
    usuario = crear_usuario_con_perfil()
    localidad = crear_localidad(nombre="Salsipuedes")

    actualizar_perfil(
        usuario,
        datos_personales={"nombre": "Valentina", "apellido": "Sosa"},
        perfil_deportivo=perfil_deportivo(localidad),
    )

    guardado = Usuario.objects.get(pk=usuario.pk)
    assert guardado.nombre == "Valentina"
    assert guardado.localidad == localidad


def test_hu004_sin_secciones_no_cambia_nada():
    usuario = crear_usuario_con_perfil()

    actualizar_perfil(usuario)

    assert Usuario.objects.get(pk=usuario.pk).nivel_estimado == Decimal("4.0")


def test_hu004_p8_con_el_perfil_guardado_no_queda_paso_pendiente():
    usuario = crear_usuario()
    assert paso_onboarding_pendiente(usuario) == "perfil"

    actualizar_perfil(usuario, perfil_deportivo=perfil_deportivo(crear_localidad()))

    assert paso_onboarding_pendiente(usuario) is None
