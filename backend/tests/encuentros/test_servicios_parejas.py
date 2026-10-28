"""Formar parejas equilibradas (HU-009 a HU-011) con el caso de ejemplo de la regla del motor:
Tomás (4,5, Drive), Valentina (4,5, Revés), Camila (5,0, Revés) y Federico (5,0, Drive), creados
en ese orden para que sus ids queden de menor a mayor."""

import threading
from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, connection
from django.utils import timezone

from apps.comun.errores import ErrorNegocio
from apps.encuentros import servicios
from apps.encuentros.models import (
    Combinacion,
    EstadoEncuentro,
    Pareja,
    ParejaIntegrante,
    Participante,
    PropuestaEncuentro,
)
from apps.usuarios.models import LadoPreferido
from tests.fabricas import (
    crear_encuentro,
    crear_encuentro_completo,
    crear_localidad,
    crear_preferencia,
    crear_usuario_con_perfil,
)

pytestmark = pytest.mark.django_db

MENSAJE_YA_COMENZO = "Este encuentro ya comenzó."
MENSAJE_YA_TIENE_PROPUESTA = "Este encuentro ya tiene una propuesta."
MENSAJE_SIN_CUATRO = "El encuentro todavía no tiene 4 jugadores confirmados."
MENSAJE_SIN_PROPUESTA = "Este encuentro todavía no tiene una propuesta."


def jugador(localidad, nombre, nivel, lado):
    usuario = crear_usuario_con_perfil(
        localidad=localidad,
        email=f"{nombre.lower()}@example.com",
        nombre=nombre,
        nivel_estimado=Decimal(nivel),
    )
    crear_preferencia(usuario, lado_preferido=lado)
    return usuario


@pytest.fixture
def jugadores():
    rio_ceballos = crear_localidad()
    return (
        jugador(rio_ceballos, "Tomas", "4.5", LadoPreferido.DRIVE),
        jugador(rio_ceballos, "Valentina", "4.5", LadoPreferido.REVES),
        jugador(rio_ceballos, "Camila", "5.0", LadoPreferido.REVES),
        jugador(rio_ceballos, "Federico", "5.0", LadoPreferido.DRIVE),
    )


@pytest.fixture
def encuentro(jugadores):
    return crear_encuentro_completo(*jugadores)


def ayer():
    return timezone.localdate() - timedelta(days=1)


def error_de(funcion, *argumentos) -> ErrorNegocio:
    with pytest.raises(ErrorNegocio) as error:
        funcion(*argumentos)
    return error.value


def ids_de_pareja(pareja) -> set[int]:
    return {integrante.participante.usuario_id for integrante in pareja.integrantes.all()}


def combinaciones_guardadas(encuentro):
    return list(encuentro.combinaciones.order_by("id_combinacion"))


def sin_filas_nuevas():
    return not (
        Combinacion.objects.exists()
        or Pareja.objects.exists()
        or ParejaIntegrante.objects.exists()
        or PropuestaEncuentro.objects.exists()
    )


# HU-009


def test_hu009_c1_con_cuatro_confirmados_inicia_la_evaluacion(encuentro):
    servicios.formar_parejas(encuentro)

    encuentro.refresh_from_db()
    assert encuentro.estado == EstadoEncuentro.PROPUESTA_GENERADA
    assert encuentro.combinaciones.count() == 3
    assert PropuestaEncuentro.objects.filter(encuentro=encuentro).exists()


def test_hu009_c2_genera_las_combinaciones_sin_repetir_ni_excluir_jugadores(encuentro, jugadores):
    servicios.formar_parejas(encuentro)

    todos = {usuario.pk for usuario in jugadores}
    conformaciones = set()
    for combinacion in combinaciones_guardadas(encuentro):
        parejas = list(combinacion.parejas.order_by("numero"))
        assert [pareja.numero for pareja in parejas] == [1, 2]
        pareja1, pareja2 = (ids_de_pareja(pareja) for pareja in parejas)
        assert len(pareja1) == len(pareja2) == 2
        assert pareja1.isdisjoint(pareja2)
        assert pareja1 | pareja2 == todos
        conformaciones.add(frozenset({frozenset(pareja1), frozenset(pareja2)}))
    assert len(conformaciones) == 3


def test_hu009_p2_guarda_las_3_combinaciones_en_el_orden_del_motor(encuentro, jugadores):
    tomas, valentina, camila, federico = (usuario.pk for usuario in jugadores)

    servicios.formar_parejas(encuentro)

    parejas_por_combinacion = [
        [ids_de_pareja(pareja) for pareja in combinacion.parejas.order_by("numero")]
        for combinacion in combinaciones_guardadas(encuentro)
    ]
    assert parejas_por_combinacion == [
        [{tomas, valentina}, {camila, federico}],
        [{tomas, camila}, {valentina, federico}],
        [{tomas, federico}, {valentina, camila}],
    ]


def test_hu009_p3_guarda_las_3_combinaciones_con_su_puntaje(encuentro):
    servicios.formar_parejas(encuentro)

    puntajes = [c.puntaje_equilibrio for c in combinaciones_guardadas(encuentro)]
    assert puntajes == [Decimal("0.8000"), Decimal("1.0000"), Decimal("0.8000")]


def test_hu009_p1_no_evalua_si_el_encuentro_busca_participantes(jugadores):
    encuentro = crear_encuentro(jugadores[0])

    error = error_de(servicios.formar_parejas, encuentro)

    assert (error.mensaje, error.estado) == (MENSAJE_SIN_CUATRO, 409)
    assert sin_filas_nuevas()


def test_hu009_p1_no_evalua_sin_exactamente_cuatro_confirmados(jugadores):
    # Un estado que no debería darse, pero el backend lo verifica igual.
    encuentro = crear_encuentro_completo(*jugadores[:3])

    error = error_de(servicios.formar_parejas, encuentro)

    assert (error.mensaje, error.estado) == (MENSAJE_SIN_CUATRO, 409)
    assert sin_filas_nuevas()
    encuentro.refresh_from_db()
    assert encuentro.estado == EstadoEncuentro.COMPLETO


def test_hu009_no_evalua_dos_veces_el_mismo_encuentro(encuentro):
    servicios.formar_parejas(encuentro)

    error = error_de(servicios.formar_parejas, encuentro)

    assert (error.mensaje, error.estado) == (MENSAJE_YA_TIENE_PROPUESTA, 409)
    assert Combinacion.objects.count() == 3
    assert PropuestaEncuentro.objects.count() == 1


def test_hu009_no_evalua_si_el_encuentro_ya_comenzo(jugadores):
    encuentro = crear_encuentro_completo(*jugadores, fecha=ayer())

    error = error_de(servicios.formar_parejas, encuentro)

    assert (error.mensaje, error.estado) == (MENSAJE_YA_COMENZO, 409)
    assert sin_filas_nuevas()


def test_hu009_si_algo_falla_no_guarda_nada(encuentro, monkeypatch):
    def fallar(*argumentos, **campos):
        raise IntegrityError("falla simulada")

    monkeypatch.setattr(PropuestaEncuentro.objects, "create", fallar)

    with pytest.raises(IntegrityError):
        servicios.formar_parejas(encuentro)

    assert sin_filas_nuevas()
    encuentro.refresh_from_db()
    assert encuentro.estado == EstadoEncuentro.COMPLETO


@pytest.mark.django_db(transaction=True)
def test_hu009_dos_pedidos_simultaneos_generan_una_sola_propuesta(encuentro):
    barrera = threading.Barrier(2)
    resultados = []

    def formar():
        try:
            barrera.wait()
            servicios.formar_parejas(encuentro)
            resultados.append("generada")
        except ErrorNegocio as error:
            resultados.append((error.estado, error.mensaje))
        finally:
            connection.close()

    hilos = [threading.Thread(target=formar) for _ in range(2)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    assert sorted(resultados, key=str) == [(409, MENSAJE_YA_TIENE_PROPUESTA), "generada"]
    assert PropuestaEncuentro.objects.count() == 1
    assert Combinacion.objects.count() == 3
    assert Pareja.objects.count() == 6
    assert ParejaIntegrante.objects.count() == 12


# HU-010 y HU-011


def test_hu010_c1_selecciona_la_combinacion_con_mejor_equilibrio(encuentro, jugadores):
    tomas, valentina, camila, federico = (usuario.pk for usuario in jugadores)

    detalle = servicios.formar_parejas(encuentro)

    assert detalle.combinacion_elegida == 2
    propuesta = PropuestaEncuentro.objects.get(encuentro=encuentro)
    parejas = propuesta.combinacion.parejas.order_by("numero")
    assert [ids_de_pareja(pareja) for pareja in parejas] == [
        {tomas, camila},
        {valentina, federico},
    ]


def test_hu010_c2_c3_dos_parejas_de_dos_con_cada_participante_una_sola_vez(encuentro):
    servicios.formar_parejas(encuentro)

    propuesta = PropuestaEncuentro.objects.get(encuentro=encuentro)
    integrantes = ParejaIntegrante.objects.filter(pareja__combinacion=propuesta.combinacion)
    assert propuesta.combinacion.parejas.count() == 2
    assert sorted(i.participante_id for i in integrantes) == sorted(
        Participante.objects.filter(encuentro=encuentro).values_list("pk", flat=True)
    )


def test_hu010_p1_ante_empate_total_elige_la_primera_combinacion():
    rio_ceballos = crear_localidad()
    iguales = [
        jugador(rio_ceballos, nombre, "4.5", LadoPreferido.INDIFERENTE)
        for nombre in ("Ana", "Bruno", "Carla", "Dario")
    ]
    encuentro = crear_encuentro_completo(*iguales)

    detalle = servicios.formar_parejas(encuentro)

    assert [c.puntaje_equilibrio for c in detalle.combinaciones] == [Decimal("1.0000")] * 3
    assert detalle.combinacion_elegida == 1
    propuesta = PropuestaEncuentro.objects.get(encuentro=encuentro)
    assert propuesta.combinacion == combinaciones_guardadas(encuentro)[0]


def test_hu011_c3_asocia_los_cuatro_participantes_con_su_pareja(encuentro, jugadores):
    tomas, valentina, camila, federico = jugadores

    detalle = servicios.formar_parejas(encuentro)

    elegida = detalle.combinaciones[detalle.combinacion_elegida - 1]
    assert [(p.numero, [u.pk for u in p.integrantes]) for p in elegida.parejas] == [
        (1, [tomas.pk, camila.pk]),
        (2, [valentina.pk, federico.pk]),
    ]


def test_hu012_obtener_propuesta_devuelve_la_guardada(encuentro):
    generada = servicios.formar_parejas(encuentro)
    encuentro.refresh_from_db()

    assert servicios.obtener_propuesta(encuentro) == generada


@pytest.mark.parametrize("completo", [False, True])
def test_hu012_sin_propuesta_generada_responde_409(jugadores, completo):
    encuentro = crear_encuentro_completo(*jugadores) if completo else crear_encuentro(jugadores[0])

    error = error_de(servicios.obtener_propuesta, encuentro)

    assert (error.mensaje, error.estado) == (MENSAJE_SIN_PROPUESTA, 409)


def test_hu011_p1_la_propuesta_apunta_a_la_elegida_con_su_puntaje(encuentro):
    detalle = servicios.formar_parejas(encuentro)

    propuesta = PropuestaEncuentro.objects.get(encuentro=encuentro)
    assert propuesta.combinacion == combinaciones_guardadas(encuentro)[1]
    assert propuesta.combinacion.puntaje_equilibrio == Decimal("1.0000")
    assert detalle.puntaje_equilibrio == Decimal("1.0000")


# Detalle de la propuesta


def test_hu009_el_detalle_trae_las_3_combinaciones_con_promedios_y_equilibrios(encuentro):
    detalle = servicios.formar_parejas(encuentro)

    obtenido = [
        (
            c.numero,
            c.puntaje_equilibrio,
            tuple(p.promedio for p in c.parejas),
            c.equilibrio_nivel,
            c.equilibrio_lado,
        )
        for c in detalle.combinaciones
    ]
    assert obtenido == [
        (1, Decimal("0.8000"), (4.5, 5.0), 0.75, 1.0),
        (2, Decimal("1.0000"), (4.75, 4.75), 1.0, 1.0),
        (3, Decimal("0.8000"), (4.75, 4.75), 1.0, 0.0),
    ]


def test_hu009_el_puntaje_es_el_guardado_y_los_promedios_se_recalculan(encuentro, jugadores):
    servicios.formar_parejas(encuentro)
    camila = jugadores[2]
    camila.nivel_estimado = Decimal("6.0")
    camila.save(update_fields=["nivel_estimado"])

    elegida = servicios.detalle_propuesta(encuentro).combinaciones[1]  # Tomás + Camila

    assert elegida.puntaje_equilibrio == Decimal("1.0000")
    assert [pareja.promedio for pareja in elegida.parejas] == [5.25, 4.75]
    assert elegida.equilibrio_nivel == 0.75
