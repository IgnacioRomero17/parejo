from datetime import time

import pytest

from apps.comun.errores import ErrorNegocio
from apps.usuarios.models import (
    DiaSemana,
    Disponibilidad,
    LadoPreferido,
    Preferencia,
    TipoEncuentro,
    Usuario,
)
from apps.usuarios.servicios import (
    MENSAJE_DISPONIBLE_SIN_FRANJAS,
    MENSAJE_FIN_ANTES_DE_INICIO,
    MENSAJE_FRANJA_CORTA,
    MENSAJE_HORA_INVALIDA,
    actualizar_perfil,
    paso_onboarding_pendiente,
    unir_franjas,
    validar_franja,
)
from tests.fabricas import (
    crear_franja,
    crear_preferencia,
    crear_usuario_con_onboarding,
    crear_usuario_con_perfil,
)

pytestmark = pytest.mark.django_db


def franja(dia, desde, hasta) -> dict:
    return {"dia_semana": dia, "hora_inicio": desde, "hora_fin": hasta}


def disponibilidad(franjas=None, **campos) -> dict:
    datos = {
        "franjas": [franja(DiaSemana.SABADO, time(17), time(21))] if franjas is None else franjas,
        "tipo_encuentro": TipoEncuentro.COMPETITIVO,
        "lado_preferido": LadoPreferido.REVES,
        "disponible_para_invitaciones": True,
    }
    datos.update(campos)
    return datos


def franjas_guardadas(usuario) -> list[tuple]:
    return list(
        Disponibilidad.objects.filter(usuario=usuario).values_list(
            "dia_semana", "hora_inicio", "hora_fin"
        )
    )


def test_hu005_c1_guarda_franjas_y_preferencias_asociadas_al_jugador():
    usuario = crear_usuario_con_perfil()
    otro = crear_usuario_con_onboarding(email="otro@example.com", localidad=usuario.localidad)
    franjas = [
        franja(DiaSemana.SABADO, time(17), time(21)),
        franja(DiaSemana.MIERCOLES, time(19), time(22)),
    ]

    actualizar_perfil(usuario, disponibilidad=disponibilidad(franjas))

    assert franjas_guardadas(usuario) == [
        (DiaSemana.MIERCOLES, time(19), time(22)),
        (DiaSemana.SABADO, time(17), time(21)),
    ]
    preferencia = Preferencia.objects.get(usuario=usuario)
    assert preferencia.tipo_encuentro == TipoEncuentro.COMPETITIVO
    assert preferencia.lado_preferido == LadoPreferido.REVES
    assert franjas_guardadas(otro) == []


def test_hu005_c2_registra_que_esta_disponible_para_invitaciones():
    usuario = crear_usuario_con_perfil()

    actualizar_perfil(usuario, disponibilidad=disponibilidad(disponible_para_invitaciones=True))

    assert Usuario.objects.get(pk=usuario.pk).disponible_para_invitaciones is True


def test_hu005_c3_al_pasar_a_no_disponible_actualiza_el_estado_y_conserva_lo_demas():
    usuario = crear_usuario_con_onboarding(disponible_para_invitaciones=True)
    crear_franja(usuario)

    actualizar_perfil(
        usuario,
        disponibilidad=disponibilidad(
            [franja(DiaSemana.SABADO, time(17), time(21))],
            tipo_encuentro=TipoEncuentro.RECREATIVO,
            lado_preferido=LadoPreferido.DRIVE,
            disponible_para_invitaciones=False,
        ),
    )

    assert Usuario.objects.get(pk=usuario.pk).disponible_para_invitaciones is False
    assert franjas_guardadas(usuario) == [(DiaSemana.SABADO, time(17), time(21))]


def test_hu005_c4_modifica_la_informacion_ya_registrada():
    usuario = crear_usuario_con_onboarding()
    crear_franja(usuario, dia_semana=DiaSemana.LUNES)
    crear_franja(usuario, dia_semana=DiaSemana.MARTES)

    actualizar_perfil(
        usuario,
        disponibilidad=disponibilidad(
            [franja(DiaSemana.DOMINGO, time(9), time(12))],
            tipo_encuentro=TipoEncuentro.INDIFERENTE,
            lado_preferido=LadoPreferido.INDIFERENTE,
        ),
    )

    assert franjas_guardadas(usuario) == [(DiaSemana.DOMINGO, time(9), time(12))]
    preferencia = Preferencia.objects.get(usuario=usuario)
    assert preferencia.tipo_encuentro == TipoEncuentro.INDIFERENTE
    assert preferencia.lado_preferido == LadoPreferido.INDIFERENTE
    assert Preferencia.objects.filter(usuario=usuario).count() == 1


def test_hu005_c4_quitar_todas_las_franjas_sin_estar_disponible():
    usuario = crear_usuario_con_onboarding()
    crear_franja(usuario)

    actualizar_perfil(
        usuario, disponibilidad=disponibilidad([], disponible_para_invitaciones=False)
    )

    assert franjas_guardadas(usuario) == []


@pytest.mark.parametrize(
    ("franjas", "esperadas"),
    [
        (
            [franja(6, time(17), time(19)), franja(6, time(18, 30), time(21))],
            [franja(6, time(17), time(21))],
        ),
        (
            [franja(6, time(19), time(21)), franja(6, time(17), time(19))],
            [franja(6, time(17), time(21))],
        ),
        (
            [franja(6, time(17), time(22)), franja(6, time(18), time(20))],
            [franja(6, time(17), time(22))],
        ),
        (
            [
                franja(6, time(17), time(19)),
                franja(6, time(20), time(22)),
                franja(6, time(18), time(20)),
            ],
            [franja(6, time(17), time(22))],
        ),
        (
            [franja(6, time(17), time(19)), franja(6, time(19, 30), time(21))],
            [franja(6, time(17), time(19)), franja(6, time(19, 30), time(21))],
        ),
        (
            [franja(6, time(17), time(19)), franja(3, time(18), time(21))],
            [franja(3, time(18), time(21)), franja(6, time(17), time(19))],
        ),
    ],
)
def test_hu005_p5_une_las_franjas_superpuestas_o_contiguas_del_mismo_dia(franjas, esperadas):
    assert unir_franjas(franjas) == esperadas


def test_hu005_p5_guarda_las_franjas_ya_unidas():
    usuario = crear_usuario_con_perfil()

    actualizar_perfil(
        usuario,
        disponibilidad=disponibilidad(
            [
                franja(DiaSemana.SABADO, time(17), time(19)),
                franja(DiaSemana.SABADO, time(18, 30), time(21)),
                franja(DiaSemana.MIERCOLES, time(17), time(19)),
                franja(DiaSemana.MIERCOLES, time(19), time(21)),
            ]
        ),
    )

    assert franjas_guardadas(usuario) == [
        (DiaSemana.MIERCOLES, time(17), time(21)),
        (DiaSemana.SABADO, time(17), time(21)),
    ]


@pytest.mark.parametrize(
    ("desde", "hasta", "campo", "mensaje"),
    [
        (time(19), time(17), "hora_fin", MENSAJE_FIN_ANTES_DE_INICIO),
        (time(19), time(19), "hora_fin", MENSAJE_FIN_ANTES_DE_INICIO),
        (time(17), time(17, 30), "hora_fin", MENSAJE_FRANJA_CORTA),
        (time(23), time(23, 30), "hora_fin", MENSAJE_FRANJA_CORTA),
        (time(17, 15), time(19), "hora_inicio", MENSAJE_HORA_INVALIDA),
        (time(17), time(19, 45), "hora_fin", MENSAJE_HORA_INVALIDA),
        (time(17, 0, 30), time(19), "hora_inicio", MENSAJE_HORA_INVALIDA),
        (time(22), time(23, 59), "hora_fin", MENSAJE_HORA_INVALIDA),
        (time(23, 45), time(23, 30), "hora_inicio", MENSAJE_HORA_INVALIDA),
    ],
)
def test_hu005_p1_p2_p3_rechaza_franjas_invalidas(desde, hasta, campo, mensaje):
    with pytest.raises(ErrorNegocio) as error:
        validar_franja(desde, hasta)

    assert error.value.campo == campo
    assert error.value.mensaje == mensaje


@pytest.mark.parametrize(
    ("desde", "hasta"),
    [(time(17), time(18)), (time(8), time(9)), (time(22, 30), time(23, 30)), (time(8), time(23))],
)
def test_hu005_p1_p2_p3_acepta_franjas_validas(desde, hasta):
    validar_franja(desde, hasta)


@pytest.mark.parametrize(
    ("desde", "hasta"),
    [(time(7, 30), time(9)), (time(0), time(1)), (time(6), time(10)), (time(7), time(8))],
)
def test_hu005_p2_rechaza_franjas_que_empiezan_antes_de_las_8(desde, hasta):
    with pytest.raises(ErrorNegocio) as error:
        validar_franja(desde, hasta)

    assert error.value.campo == "hora_inicio"
    assert error.value.mensaje == (
        "Elegí un horario entre las 08:00 y las 23:30, en pasos de 30 minutos."
    )


def test_hu005_p3_una_franja_invalida_impide_guardar_todo():
    usuario = crear_usuario_con_onboarding(nombre="Ana")
    crear_franja(usuario)

    with pytest.raises(ErrorNegocio):
        actualizar_perfil(
            usuario,
            datos_personales={"nombre": "Valentina", "apellido": "Sosa"},
            disponibilidad=disponibilidad([franja(DiaSemana.LUNES, time(17), time(17, 30))]),
        )

    assert Usuario.objects.get(pk=usuario.pk).nombre == "Ana"
    assert franjas_guardadas(usuario) == [(DiaSemana.SABADO, time(17), time(21))]


def test_hu005_p6_disponible_sin_franjas_impide_guardar():
    usuario = crear_usuario_con_perfil()

    with pytest.raises(ErrorNegocio) as error:
        actualizar_perfil(
            usuario, disponibilidad=disponibilidad([], disponible_para_invitaciones=True)
        )

    assert error.value.campo == "disponible_para_invitaciones"
    assert error.value.mensaje == MENSAJE_DISPONIBLE_SIN_FRANJAS
    assert not Preferencia.objects.filter(usuario=usuario).exists()


def test_hu005_p6_quitar_la_ultima_franja_estando_disponible_impide_guardar():
    usuario = crear_usuario_con_onboarding(disponible_para_invitaciones=True)
    crear_franja(usuario)

    with pytest.raises(ErrorNegocio):
        actualizar_perfil(usuario, disponibilidad=disponibilidad([]))

    assert franjas_guardadas(usuario) == [(DiaSemana.SABADO, time(17), time(21))]
    assert Usuario.objects.get(pk=usuario.pk).disponible_para_invitaciones is True


def test_hu005_onboarding_se_completa_sin_franjas_y_sin_estar_disponible():
    usuario = crear_usuario_con_perfil()
    assert paso_onboarding_pendiente(usuario) == "disponibilidad"

    actualizar_perfil(
        usuario, disponibilidad=disponibilidad([], disponible_para_invitaciones=False)
    )

    assert paso_onboarding_pendiente(usuario) is None
    assert Usuario.objects.get(pk=usuario.pk).disponible_para_invitaciones is False


def test_hu005_p9_el_interruptor_arranca_apagado():
    usuario = crear_usuario_con_perfil()
    crear_preferencia(usuario)

    assert Usuario.objects.get(pk=usuario.pk).disponible_para_invitaciones is False
