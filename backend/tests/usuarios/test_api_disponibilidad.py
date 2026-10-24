from datetime import time

import pytest
from rest_framework.test import APIClient

from apps.usuarios.models import DiaSemana, Disponibilidad, Preferencia, Usuario
from tests.fabricas import crear_franja, crear_usuario_con_onboarding, crear_usuario_con_perfil

pytestmark = pytest.mark.django_db

URL_PERFIL = "/api/perfil"
URL_YO = "/api/auth/yo"
MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
MENSAJE_OPCION_INVALIDA = "Elegí una opción del listado."
MENSAJE_HORA_INVALIDA = "Elegí un horario entre las 08:00 y las 23:30, en pasos de 30 minutos."
MENSAJE_FIN_ANTES_DE_INICIO = "La hora de fin debe ser posterior a la de inicio."
MENSAJE_FRANJA_CORTA = "La franja debe durar al menos 60 minutos."
MENSAJE_DISPONIBLE_SIN_FRANJAS = "Para recibir invitaciones necesitás cargar al menos una franja."


@pytest.fixture
def usuario():
    return crear_usuario_con_perfil(email="tomas.rios@example.com")


@pytest.fixture
def cliente(usuario) -> APIClient:
    cliente = APIClient()
    cliente.force_login(usuario)
    return cliente


def franja(dia, desde, hasta) -> dict:
    return {"dia_semana": dia, "hora_inicio": desde, "hora_fin": hasta}


def disponibilidad(franjas=None, **campos) -> dict:
    datos = {
        "franjas": [franja(6, "17:00", "21:00")] if franjas is None else franjas,
        "tipo_encuentro": "COMPETITIVO",
        "lado_preferido": "DRIVE",
        "disponible_para_invitaciones": True,
    }
    datos.update(campos)
    return datos


def guardar_disponibilidad(cliente, datos):
    return cliente.patch(URL_PERFIL, {"disponibilidad": datos}, format="json")


def errores_de_disponibilidad(respuesta) -> dict:
    assert respuesta.status_code == 400
    return respuesta.json()["errores"]["disponibilidad"]


def test_hu005_c1_guarda_y_devuelve_franjas_y_preferencias(cliente, usuario):
    datos = disponibilidad([franja(6, "17:00", "21:00"), franja(3, "19:00", "22:00")])

    respuesta = guardar_disponibilidad(cliente, datos)

    assert respuesta.status_code == 200
    assert respuesta.json()["disponibilidad"] == {
        "franjas": [franja(3, "19:00", "22:00"), franja(6, "17:00", "21:00")],
        "tipo_encuentro": "COMPETITIVO",
        "lado_preferido": "DRIVE",
        "disponible_para_invitaciones": True,
    }
    assert cliente.get(URL_PERFIL).json()["disponibilidad"] == respuesta.json()["disponibilidad"]


def test_hu005_c2_c3_el_interruptor_se_activa_y_se_desactiva(cliente, usuario):
    guardar_disponibilidad(cliente, disponibilidad(disponible_para_invitaciones=True))
    usuario.refresh_from_db()
    assert usuario.disponible_para_invitaciones is True

    respuesta = guardar_disponibilidad(cliente, disponibilidad(disponible_para_invitaciones=False))

    assert respuesta.status_code == 200
    assert respuesta.json()["disponibilidad"]["disponible_para_invitaciones"] is False
    usuario.refresh_from_db()
    assert usuario.disponible_para_invitaciones is False


def test_hu005_c4_modifica_la_informacion_ya_registrada():
    usuario = crear_usuario_con_onboarding()
    crear_franja(usuario, dia_semana=DiaSemana.LUNES)
    cliente = APIClient()
    cliente.force_login(usuario)

    respuesta = guardar_disponibilidad(
        cliente,
        disponibilidad(
            [franja(7, "09:00", "12:00")], tipo_encuentro="RECREATIVO", lado_preferido="REVES"
        ),
    )

    assert respuesta.status_code == 200
    actual = cliente.get(URL_PERFIL).json()["disponibilidad"]
    assert actual["franjas"] == [franja(7, "09:00", "12:00")]
    assert (actual["tipo_encuentro"], actual["lado_preferido"]) == ("RECREATIVO", "REVES")


def test_hu005_p5_devuelve_las_franjas_ya_unidas(cliente):
    respuesta = guardar_disponibilidad(
        cliente,
        disponibilidad(
            [
                franja(6, "17:00", "19:00"),
                franja(6, "18:30", "21:00"),
                franja(3, "17:00", "19:00"),
                franja(3, "19:00", "21:00"),
            ]
        ),
    )

    assert respuesta.json()["disponibilidad"]["franjas"] == [
        franja(3, "17:00", "21:00"),
        franja(6, "17:00", "21:00"),
    ]


def test_hu005_p1_p3_marca_el_error_en_la_fila_que_corresponde(cliente, usuario):
    respuesta = guardar_disponibilidad(
        cliente,
        disponibilidad(
            [
                franja(6, "17:00", "21:00"),
                franja(3, "19:00", "18:00"),
                franja(1, "17:00", "17:30"),
            ]
        ),
    )

    # Solo las filas con error, por su posición en la lista enviada.
    assert errores_de_disponibilidad(respuesta) == {
        "franjas": {
            "1": {"hora_fin": [MENSAJE_FIN_ANTES_DE_INICIO]},
            "2": {"hora_fin": [MENSAJE_FRANJA_CORTA]},
        }
    }
    assert not Disponibilidad.objects.filter(usuario=usuario).exists()


@pytest.mark.parametrize(
    ("datos_franja", "errores"),
    [
        (franja(6, "17:15", "19:00"), {"hora_inicio": [MENSAJE_HORA_INVALIDA]}),
        (franja(6, "07:30", "09:00"), {"hora_inicio": [MENSAJE_HORA_INVALIDA]}),
        (franja(6, "00:00", "02:00"), {"hora_inicio": [MENSAJE_HORA_INVALIDA]}),
        (franja(6, "22:00", "23:45"), {"hora_fin": [MENSAJE_HORA_INVALIDA]}),
        (franja(6, "22:00", "24:00"), {"hora_fin": [MENSAJE_HORA_INVALIDA]}),
        (franja(6, "las cinco", "19:00"), {"hora_inicio": [MENSAJE_HORA_INVALIDA]}),
        (franja(6, "17:00:00", "19:00"), {"hora_inicio": [MENSAJE_HORA_INVALIDA]}),
        (franja(8, "17:00", "19:00"), {"dia_semana": [MENSAJE_OPCION_INVALIDA]}),
        (franja("SABADO", "17:00", "19:00"), {"dia_semana": [MENSAJE_OPCION_INVALIDA]}),
        (
            {"dia_semana": None, "hora_inicio": "", "hora_fin": None},
            {
                "dia_semana": [MENSAJE_CAMPO_VACIO],
                "hora_inicio": [MENSAJE_HORA_INVALIDA],
                "hora_fin": [MENSAJE_CAMPO_VACIO],
            },
        ),
        (
            {},
            {
                "dia_semana": [MENSAJE_CAMPO_VACIO],
                "hora_inicio": [MENSAJE_CAMPO_VACIO],
                "hora_fin": [MENSAJE_CAMPO_VACIO],
            },
        ),
    ],
)
def test_hu005_p1_p2_rechaza_datos_de_franja_invalidos(cliente, datos_franja, errores):
    respuesta = guardar_disponibilidad(cliente, disponibilidad([datos_franja]))

    assert errores_de_disponibilidad(respuesta) == {"franjas": {"0": errores}}


def test_hu005_p2_acepta_franjas_en_los_limites_de_8_a_23_30(cliente):
    limites = [franja(5, "08:00", "09:00"), franja(5, "22:30", "23:30")]

    respuesta = guardar_disponibilidad(cliente, disponibilidad(limites))

    assert respuesta.status_code == 200
    assert respuesta.json()["disponibilidad"]["franjas"] == limites


def test_hu005_p6_disponible_sin_franjas_responde_el_error_del_interruptor(cliente, usuario):
    respuesta = guardar_disponibilidad(
        cliente, disponibilidad([], disponible_para_invitaciones=True)
    )

    assert errores_de_disponibilidad(respuesta) == {
        "disponible_para_invitaciones": [MENSAJE_DISPONIBLE_SIN_FRANJAS]
    }
    assert not Preferencia.objects.filter(usuario=usuario).exists()


def test_hu005_c1_indica_las_preferencias_pendientes(cliente):
    respuesta = guardar_disponibilidad(
        cliente, disponibilidad(tipo_encuentro=None, lado_preferido=None)
    )

    assert errores_de_disponibilidad(respuesta) == {
        "tipo_encuentro": [MENSAJE_CAMPO_VACIO],
        "lado_preferido": [MENSAJE_CAMPO_VACIO],
    }


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("tipo_encuentro", "AMISTOSO"), ("lado_preferido", "DERECHA")],
)
def test_hu005_p7_p8_rechaza_preferencias_fuera_del_listado(cliente, campo, valor):
    respuesta = guardar_disponibilidad(cliente, disponibilidad(**{campo: valor}))

    assert errores_de_disponibilidad(respuesta) == {campo: [MENSAJE_OPCION_INVALIDA]}


def test_hu005_la_seccion_llega_completa(cliente):
    respuesta = guardar_disponibilidad(cliente, {})

    assert errores_de_disponibilidad(respuesta) == {
        "franjas": [MENSAJE_CAMPO_VACIO],
        "tipo_encuentro": [MENSAJE_CAMPO_VACIO],
        "lado_preferido": [MENSAJE_CAMPO_VACIO],
        "disponible_para_invitaciones": [MENSAJE_CAMPO_VACIO],
    }


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("franjas", "sábado"), ("disponible_para_invitaciones", "tal vez")],
)
def test_hu005_rechaza_datos_mal_formados(cliente, campo, valor):
    respuesta = guardar_disponibilidad(cliente, disponibilidad(**{campo: valor}))

    errores = errores_de_disponibilidad(respuesta)
    assert MENSAJE_OPCION_INVALIDA in str(errores[campo])


def test_hu005_auth_yo_informa_el_paso_disponibilidad_hasta_guardarlo(cliente):
    assert cliente.get(URL_YO).json()["onboarding"] == "disponibilidad"

    guardar_disponibilidad(cliente, disponibilidad([], disponible_para_invitaciones=False))

    assert cliente.get(URL_YO).json()["onboarding"] is None


def test_hu005_con_un_error_no_guarda_ninguna_seccion(cliente, usuario):
    respuesta = cliente.patch(
        URL_PERFIL,
        {
            "datos_personales": {"nombre": "Valentina", "apellido": "Sosa"},
            "disponibilidad": disponibilidad([franja(6, "19:00", "18:00")]),
        },
        format="json",
    )

    assert respuesta.status_code == 400
    usuario.refresh_from_db()
    assert usuario.nombre == "Ana"
    assert not Preferencia.objects.filter(usuario=usuario).exists()


def test_hu005_cada_jugador_solo_modifica_su_disponibilidad(cliente, usuario):
    otro = crear_usuario_con_onboarding(
        email="valentina.sosa@example.com", localidad=usuario.localidad
    )
    crear_franja(otro, hora_inicio=time(9), hora_fin=time(11))

    guardar_disponibilidad(cliente, disponibilidad([franja(1, "17:00", "19:00")]))

    assert list(
        Disponibilidad.objects.filter(usuario=otro).values_list("dia_semana", flat=True)
    ) == [DiaSemana.SABADO]
    assert Usuario.objects.get(pk=otro.pk).disponible_para_invitaciones is False


def test_hu005_patch_de_disponibilidad_sin_sesion_responde_401():
    respuesta = APIClient().patch(URL_PERFIL, {"disponibilidad": disponibilidad()}, format="json")

    assert respuesta.status_code == 401
