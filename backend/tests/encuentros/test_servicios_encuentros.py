from datetime import UTC, datetime, time, timedelta

import pytest
from django.utils import timezone

from apps.comun.errores import ErrorNegocio
from apps.comun.horarios import MENSAJE_HORA_INVALIDA
from apps.encuentros.models import Encuentro, EstadoEncuentro, Participante
from apps.encuentros.servicios import (
    MENSAJE_EN_EL_PASADO,
    MENSAJE_ENCUENTRO_INEXISTENTE,
    MENSAJE_FECHA_LEJANA,
    MENSAJE_FIN_TARDE,
    cantidad_confirmados,
    crear_encuentro,
    es_participante,
    obtener_encuentro,
    validar_condiciones,
)
from apps.usuarios.models import TipoEncuentro
from tests.fabricas import (
    crear_localidad,
    crear_usuario_con_onboarding,
    crear_usuario_con_perfil,
    proximo_sabado,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def organizador():
    return crear_usuario_con_onboarding(email="tomas.rios@example.com")


@pytest.fixture
def fijar_ahora(monkeypatch):
    """Fija `timezone.now()` en una fecha y hora de Córdoba; devuelve el instante en UTC."""

    def fijar(fecha, hora):
        ahora = datetime.combine(fecha, hora, tzinfo=timezone.get_default_timezone())
        monkeypatch.setattr(timezone, "now", lambda: ahora.astimezone(UTC))
        return ahora

    return fijar


def condiciones(**campos) -> dict:
    datos = {
        "fecha": proximo_sabado(),
        "hora_inicio": time(18),
        "duracion_minutos": 90,
        "localidad": crear_localidad(nombre="Unquillo"),
        "ubicacion": "Av. San Martín 4500",
        "tipo_encuentro": TipoEncuentro.COMPETITIVO,
    }
    datos.update(campos)
    return datos


def error_de(funcion, *argumentos) -> ErrorNegocio:
    with pytest.raises(ErrorNegocio) as error:
        funcion(*argumentos)
    return error.value


def test_hu006_c1_crea_el_encuentro_listo_para_buscar_participantes(organizador):
    encuentro = crear_encuentro(organizador, condiciones())

    encuentro.refresh_from_db()
    assert encuentro.estado == EstadoEncuentro.BUSCANDO_PARTICIPANTES
    assert encuentro.organizador == organizador


def test_hu006_c3_registra_las_condiciones(organizador):
    datos = condiciones()

    encuentro = crear_encuentro(organizador, datos)

    guardado = Encuentro.objects.get(pk=encuentro.pk)
    assert {campo: getattr(guardado, campo) for campo in datos} == datos


def test_hu006_p7_el_organizador_es_el_primer_participante_confirmado(organizador):
    encuentro = crear_encuentro(organizador, condiciones())

    assert list(
        Participante.objects.filter(encuentro=encuentro).values_list("usuario", flat=True)
    ) == [organizador.pk]
    assert cantidad_confirmados(encuentro) == 1
    assert es_participante(organizador, encuentro)


@pytest.mark.parametrize(
    "crear_usuario",
    [
        crear_usuario_con_perfil,  # sin preferencia: falta el paso 2
        lambda: crear_usuario_con_onboarding(nivel_estimado=None),  # perfil incompleto
    ],
    ids=["sin_disponibilidad", "sin_perfil"],
)
def test_hu006_c1_sin_onboarding_completo_no_crea_el_encuentro(crear_usuario):
    usuario = crear_usuario()

    error = error_de(crear_encuentro, usuario, condiciones())

    assert error.estado == 403
    assert not Encuentro.objects.exists()


@pytest.mark.parametrize(
    "hora_inicio", [time(18, 15), time(18, 0, 30), time(7, 30), time(0), time(23, 45)]
)
def test_hu006_p2_rechaza_horas_fuera_de_los_pasos_o_del_horario(hora_inicio):
    error = error_de(validar_condiciones, proximo_sabado(), hora_inicio, 60)

    assert (error.campo, error.mensaje) == ("hora_inicio", MENSAJE_HORA_INVALIDA)


@pytest.mark.parametrize(
    ("hora_inicio", "duracion"),
    [(time(8), 60), (time(18, 30), 90), (time(22, 30), 60), (time(22), 90), (time(21, 30), 120)],
)
def test_hu006_p3_p6_acepta_encuentros_que_terminan_a_las_23_30_o_antes(hora_inicio, duracion):
    validar_condiciones(proximo_sabado(), hora_inicio, duracion)


@pytest.mark.parametrize(
    ("hora_inicio", "duracion"),
    [(time(22, 30), 90), (time(22, 30), 120), (time(23), 60), (time(23, 30), 60)],
)
def test_hu006_p6_rechaza_encuentros_que_terminan_despues_de_las_23_30(hora_inicio, duracion):
    error = error_de(validar_condiciones, proximo_sabado(), hora_inicio, duracion)

    assert (error.campo, error.mensaje) == ("duracion_minutos", MENSAJE_FIN_TARDE)


def test_hu006_p6_con_un_error_no_guarda_nada(organizador):
    error_de(
        crear_encuentro, organizador, condiciones(hora_inicio=time(22, 30), duracion_minutos=120)
    )

    assert not Encuentro.objects.exists()
    assert not Participante.objects.exists()


def test_hu006_p4_rechaza_una_fecha_pasada(fijar_ahora):
    hoy = timezone.localdate()
    fijar_ahora(hoy, time(10))

    error = error_de(validar_condiciones, hoy - timedelta(days=1), time(18), 60)

    assert (error.campo, error.mensaje) == ("fecha", MENSAJE_EN_EL_PASADO)


@pytest.mark.parametrize("hora_inicio", [time(9, 30), time(10)])
def test_hu006_p4_rechaza_hoy_a_una_hora_pasada_o_actual(fijar_ahora, hora_inicio):
    hoy = timezone.localdate()
    fijar_ahora(hoy, time(10))

    error = error_de(validar_condiciones, hoy, hora_inicio, 60)

    assert (error.campo, error.mensaje) == ("hora_inicio", MENSAJE_EN_EL_PASADO)


def test_hu006_p4_acepta_hoy_a_una_hora_posterior(fijar_ahora):
    hoy = timezone.localdate()
    fijar_ahora(hoy, time(10, 1))

    validar_condiciones(hoy, time(10, 30), 60)


def test_hu006_p4_usa_la_hora_de_cordoba_a_la_noche(fijar_ahora):
    # 22:00 en Córdoba es la 01:00 del día siguiente en UTC: el encuentro de hoy a las 22:30
    # todavía no empezó, aunque en UTC su fecha ya haya pasado.
    hoy = timezone.localdate()
    ahora = fijar_ahora(hoy, time(22))
    assert timezone.now().date() == hoy + timedelta(days=1)
    assert ahora.utcoffset() == timedelta(hours=-3)

    validar_condiciones(hoy, time(22, 30), 60)
    error = error_de(validar_condiciones, hoy, time(21, 30), 60)

    assert (error.campo, error.mensaje) == ("hora_inicio", MENSAJE_EN_EL_PASADO)


def test_hu006_p4_usa_la_hora_de_cordoba_a_la_manana(fijar_ahora):
    # 09:00 en Córdoba son las 12:00 en UTC: un encuentro a las 10:00 todavía es futuro.
    hoy = timezone.localdate()
    fijar_ahora(hoy, time(9))

    validar_condiciones(hoy, time(10), 60)
    error = error_de(validar_condiciones, hoy, time(8, 30), 60)

    assert error.campo == "hora_inicio"


def test_hu006_p4_acepta_el_dia_60(fijar_ahora):
    hoy = timezone.localdate()
    fijar_ahora(hoy, time(10))

    validar_condiciones(hoy + timedelta(days=60), time(8), 60)


def test_hu006_p4_rechaza_el_dia_61(fijar_ahora):
    hoy = timezone.localdate()
    fijar_ahora(hoy, time(10))

    error = error_de(validar_condiciones, hoy + timedelta(days=61), time(18), 60)

    assert (error.campo, error.mensaje) == ("fecha", MENSAJE_FECHA_LEJANA)


def test_hu006_p4_cuenta_los_60_dias_desde_hoy_en_cordoba(fijar_ahora):
    # A las 22:00 de Córdoba ya es mañana en UTC: si se contara desde la fecha UTC, el día 61
    # se aceptaría.
    hoy = timezone.localdate()
    fijar_ahora(hoy, time(22))
    assert timezone.now().date() == hoy + timedelta(days=1)

    validar_condiciones(hoy + timedelta(days=60), time(22, 30), 60)
    error = error_de(validar_condiciones, hoy + timedelta(days=61), time(8), 60)

    assert (error.campo, error.mensaje) == ("fecha", MENSAJE_FECHA_LEJANA)


def test_hu006_obtener_encuentro_devuelve_el_encuentro(organizador):
    encuentro = crear_encuentro(organizador, condiciones())

    assert obtener_encuentro(encuentro.pk) == encuentro


@pytest.mark.parametrize("id_encuentro", [999_999, 0, 99_999_999_999])
def test_hu006_obtener_encuentro_inexistente_responde_404(id_encuentro):
    error = error_de(obtener_encuentro, id_encuentro)

    assert (error.estado, error.mensaje) == (404, MENSAJE_ENCUENTRO_INEXISTENTE)


def test_hu006_quien_no_participa_no_es_participante(organizador):
    encuentro = crear_encuentro(organizador, condiciones())
    otro = crear_usuario_con_onboarding(
        email="valentina.sosa@example.com", localidad=organizador.localidad
    )

    assert not es_participante(otro, encuentro)
