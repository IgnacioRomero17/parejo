from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.encuentros.models import EstadoEncuentro, EstadoInvitacion, Invitacion, Participante
from apps.usuarios.models import Genero
from tests.fabricas import (
    crear_encuentro,
    crear_invitacion,
    crear_jugador_disponible,
    crear_localidad,
    crear_usuario,
    crear_usuario_con_onboarding,
)

pytestmark = pytest.mark.django_db

MENSAJE_ENCUENTRO_INEXISTENTE = "El encuentro no existe."
MENSAJE_INVITACION_INEXISTENTE = "La invitación no existe."
MENSAJE_YA_COMENZO = "Este encuentro ya comenzó."
MENSAJE_NO_DISPONIBLE = (
    "Alguno de los jugadores ya no está disponible para este encuentro. Actualizá la lista."
)
MENSAJE_MAS_QUE_LUGARES = "Seleccionaste más jugadores que lugares libres."
MENSAJE_RESPONDIDA = "Ya respondiste esta invitación."
MENSAJE_SIN_SELECCION = "Seleccioná al menos un jugador."
MENSAJE_OPCION_INVALIDA = "Elegí una opción del listado."


@pytest.fixture
def rio_ceballos():
    return crear_localidad()


@pytest.fixture
def organizador(rio_ceballos):
    return crear_usuario_con_onboarding(
        localidad=rio_ceballos,
        email="tomas@example.com",
        nombre="Tomás",
        apellido="Ríos",
        genero=Genero.MASCULINO,
        nivel_estimado=Decimal("4.5"),
    )


@pytest.fixture
def encuentro(organizador):
    return crear_encuentro(organizador)


@pytest.fixture
def valentina(rio_ceballos):
    return crear_jugador_disponible(
        rio_ceballos,
        "valentina@example.com",
        nombre="Valentina",
        apellido="Sosa",
        nivel_estimado=Decimal("4.5"),
    )


def cliente_de(usuario) -> APIClient:
    cliente = APIClient()
    cliente.force_login(usuario)
    return cliente


def invitar(usuario, id_encuentro, datos):
    return cliente_de(usuario).post(
        f"/api/encuentros/{id_encuentro}/invitaciones", datos, format="json"
    )


def responder(usuario, id_invitacion, accion):
    return cliente_de(usuario).post(f"/api/invitaciones/{id_invitacion}/{accion}")


def ayer():
    return timezone.localdate() - timedelta(days=1)


# POST encuentros/{id}/invitaciones


def test_hu008_c1_invitar_responde_201_con_las_invitaciones(
    encuentro, organizador, valentina, rio_ceballos
):
    respuesta = invitar(organizador, encuentro.pk, {"usuarios": [valentina.pk]})

    assert respuesta.status_code == 201
    invitacion = Invitacion.objects.get()
    assert respuesta.json() == [
        {
            "id": invitacion.pk,
            "jugador": {
                "id": valentina.pk,
                "nombre": "Valentina",
                "apellido": "Sosa",
                "localidad": {"id": rio_ceballos.pk, "nombre": "Río Ceballos"},
                "nivel": 4.5,
            },
            "estado": "PENDIENTE",
            "fecha_envio": respuesta.json()[0]["fecha_envio"],
        }
    ]
    assert invitacion.encuentro == encuentro


@pytest.mark.parametrize(
    ("datos", "mensaje"),
    [
        ({}, "Completá este campo para poder guardar."),
        ({"usuarios": []}, MENSAJE_SIN_SELECCION),
        ({"usuarios": "uno"}, MENSAJE_OPCION_INVALIDA),
        ({"usuarios": ["uno"]}, MENSAJE_OPCION_INVALIDA),
        ({"usuarios": [0]}, MENSAJE_OPCION_INVALIDA),
    ],
)
def test_hu008_invitar_con_datos_invalidos_responde_400(encuentro, organizador, datos, mensaje):
    respuesta = invitar(organizador, encuentro.pk, datos)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"usuarios": [mensaje]}}


def test_hu008_invitar_con_ids_repetidos_responde_400(encuentro, organizador, valentina):
    respuesta = invitar(organizador, encuentro.pk, {"usuarios": [valentina.pk, valentina.pk]})

    assert respuesta.status_code == 400
    assert respuesta.json() == {"errores": {"usuarios": [MENSAJE_OPCION_INVALIDA]}}
    assert not Invitacion.objects.exists()


def test_hu008_p2_mas_jugadores_que_lugares_libres_responde_400(
    encuentro, organizador, rio_ceballos
):
    ids = [
        crear_jugador_disponible(rio_ceballos, f"j{numero}@example.com").pk for numero in range(4)
    ]

    respuesta = invitar(organizador, encuentro.pk, {"usuarios": ids})

    assert respuesta.status_code == 400
    assert respuesta.json() == {"detalle": MENSAJE_MAS_QUE_LUGARES}


def test_hu008_p3_invitar_de_nuevo_responde_409(encuentro, organizador, valentina):
    crear_invitacion(encuentro, valentina, estado=EstadoInvitacion.RECHAZADA)

    respuesta = invitar(organizador, encuentro.pk, {"usuarios": [valentina.pk]})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detalle": MENSAJE_NO_DISPONIBLE}


def test_hu008_p6_invitar_a_un_encuentro_comenzado_responde_409(organizador, valentina):
    encuentro = crear_encuentro(organizador, fecha=ayer())

    respuesta = invitar(organizador, encuentro.pk, {"usuarios": [valentina.pk]})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detalle": MENSAJE_YA_COMENZO}


def test_hu008_solo_el_organizador_puede_invitar(encuentro, valentina, rio_ceballos):
    participante = crear_usuario_con_onboarding(localidad=rio_ceballos, email="p@example.com")
    Participante.objects.create(encuentro=encuentro, usuario=participante)

    respuesta = invitar(participante, encuentro.pk, {"usuarios": [valentina.pk]})

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_ENCUENTRO_INEXISTENTE}
    assert not Invitacion.objects.exists()


def test_hu008_invitar_sin_sesion_responde_401(encuentro, valentina):
    respuesta = APIClient().post(
        f"/api/encuentros/{encuentro.pk}/invitaciones",
        {"usuarios": [valentina.pk]},
        format="json",
    )

    assert respuesta.status_code == 401


# GET encuentros/{id}


def test_hu008_el_organizador_ve_participantes_e_invitaciones(
    encuentro, organizador, valentina, rio_ceballos
):
    aceptada = crear_invitacion(encuentro, valentina, estado=EstadoInvitacion.ACEPTADA)
    Participante.objects.create(encuentro=encuentro, usuario=valentina)
    joaquin = crear_jugador_disponible(rio_ceballos, "joaquin@example.com", nombre="Joaquín")
    pendiente = crear_invitacion(encuentro, joaquin)

    cuerpo = cliente_de(organizador).get(f"/api/encuentros/{encuentro.pk}").json()

    assert cuerpo["confirmados"] == 2
    assert cuerpo["lugares_libres"] == 1
    assert [(p["id"], p["nombre"], p["lado"]) for p in cuerpo["participantes"]] == [
        (organizador.pk, "Tomás", "DRIVE"),
        (valentina.pk, "Valentina", "DRIVE"),
    ]
    assert [(i["id"], i["jugador"]["id"], i["estado"]) for i in cuerpo["invitaciones"]] == [
        (aceptada.pk, valentina.pk, "ACEPTADA"),
        (pendiente.pk, joaquin.pk, "PENDIENTE"),
    ]


def test_hu008_un_participante_no_ve_las_invitaciones(encuentro, valentina):
    Participante.objects.create(encuentro=encuentro, usuario=valentina)

    respuesta = cliente_de(valentina).get(f"/api/encuentros/{encuentro.pk}")

    assert respuesta.status_code == 200
    assert "invitaciones" not in respuesta.json()


def test_hu008_un_invitado_que_no_acepto_no_ve_el_encuentro(encuentro, valentina):
    crear_invitacion(encuentro, valentina)

    assert cliente_de(valentina).get(f"/api/encuentros/{encuentro.pk}").status_code == 404


# GET invitaciones


def test_hu008_c2_la_bandeja_muestra_el_encuentro_y_el_organizador(
    encuentro, organizador, valentina, rio_ceballos
):
    invitacion = crear_invitacion(encuentro, valentina)

    respuesta = cliente_de(valentina).get("/api/invitaciones")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["respondidas"] == []
    (pendiente,) = cuerpo["pendientes"]
    assert pendiente == {
        "id": invitacion.pk,
        "estado": "PENDIENTE",
        "fecha_envio": pendiente["fecha_envio"],
        "organizador": {
            "id": organizador.pk,
            "nombre": "Tomás",
            "apellido": "Ríos",
            "genero": "MASCULINO",
        },
        "encuentro": {
            "id": encuentro.pk,
            "fecha": encuentro.fecha.isoformat(),
            "hora_inicio": "18:00",
            "duracion_minutos": 90,
            "localidad": {"id": rio_ceballos.pk, "nombre": "Río Ceballos"},
            "ubicacion": "Av. San Martín 4500",
            "tipo_encuentro": "COMPETITIVO",
            "estado": "BUSCANDO_PARTICIPANTES",
            "confirmados": 1,
        },
    }


def test_hu008_la_bandeja_exige_el_onboarding(rio_ceballos):
    sin_onboarding = crear_usuario(email="nuevo@example.com")

    respuesta = cliente_de(sin_onboarding).get("/api/invitaciones")

    assert respuesta.status_code == 403
    assert respuesta.json()["onboarding"] == "perfil"


def test_hu008_la_bandeja_sin_sesion_responde_401():
    assert APIClient().get("/api/invitaciones").status_code == 401


# POST invitaciones/{id}/aceptar · rechazar


def test_hu008_c3_aceptar_responde_200_y_confirma_al_jugador(encuentro, valentina):
    invitacion = crear_invitacion(encuentro, valentina)

    respuesta = responder(valentina, invitacion.pk, "aceptar")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ACEPTADA"
    assert respuesta.json()["encuentro"]["confirmados"] == 2
    assert Participante.objects.filter(encuentro=encuentro, usuario=valentina).exists()


def test_hu008_c3_rechazar_responde_200(encuentro, valentina):
    invitacion = crear_invitacion(encuentro, valentina)

    respuesta = responder(valentina, invitacion.pk, "rechazar")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "RECHAZADA"
    assert respuesta.json()["encuentro"]["confirmados"] == 1


def test_hu008_p4_aceptar_el_cuarto_lugar_completa_el_encuentro(encuentro, valentina, rio_ceballos):
    for numero in range(2):
        otro = crear_usuario_con_onboarding(localidad=rio_ceballos, email=f"o{numero}@example.com")
        Participante.objects.create(encuentro=encuentro, usuario=otro)
    invitacion = crear_invitacion(encuentro, valentina)

    respuesta = responder(valentina, invitacion.pk, "aceptar")

    assert respuesta.json()["encuentro"]["estado"] == EstadoEncuentro.COMPLETO
    assert respuesta.json()["encuentro"]["confirmados"] == 4


@pytest.mark.parametrize("accion", ["aceptar", "rechazar"])
def test_hu008_p6_responder_en_un_encuentro_comenzado_responde_409(organizador, valentina, accion):
    invitacion = crear_invitacion(crear_encuentro(organizador, fecha=ayer()), valentina)

    respuesta = responder(valentina, invitacion.pk, accion)

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detalle": MENSAJE_YA_COMENZO}


@pytest.mark.parametrize("accion", ["aceptar", "rechazar"])
def test_hu008_responder_una_invitacion_respondida_responde_409(encuentro, valentina, accion):
    invitacion = crear_invitacion(encuentro, valentina, estado=EstadoInvitacion.RECHAZADA)

    respuesta = responder(valentina, invitacion.pk, accion)

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detalle": MENSAJE_RESPONDIDA}


@pytest.mark.parametrize("accion", ["aceptar", "rechazar"])
def test_hu008_solo_el_invitado_puede_responder(encuentro, organizador, valentina, accion):
    invitacion = crear_invitacion(encuentro, valentina)

    respuesta = responder(organizador, invitacion.pk, accion)

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_INVITACION_INEXISTENTE}
    invitacion.refresh_from_db()
    assert invitacion.estado == EstadoInvitacion.PENDIENTE


@pytest.mark.parametrize("id_invitacion", [999_999, 2_147_483_648])
def test_hu008_responder_una_invitacion_inexistente_responde_404(valentina, id_invitacion):
    respuesta = responder(valentina, id_invitacion, "aceptar")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": MENSAJE_INVITACION_INEXISTENTE}


def test_hu008_responder_sin_sesion_responde_401(encuentro, valentina):
    invitacion = crear_invitacion(encuentro, valentina)

    assert APIClient().post(f"/api/invitaciones/{invitacion.pk}/aceptar").status_code == 401


# GET auth/yo


def test_hu008_auth_yo_informa_las_invitaciones_pendientes(organizador, valentina):
    crear_invitacion(crear_encuentro(organizador), valentina)
    crear_invitacion(crear_encuentro(organizador), valentina)
    crear_invitacion(crear_encuentro(organizador, fecha=ayer()), valentina)
    crear_invitacion(crear_encuentro(organizador), valentina, estado=EstadoInvitacion.ACEPTADA)

    respuesta = cliente_de(valentina).get("/api/auth/yo")

    assert respuesta.json()["invitaciones_pendientes"] == 2
