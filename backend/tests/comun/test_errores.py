import pytest
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APIClient

from apps.comun.errores import ErrorNegocio, OnboardingIncompleto, manejar_excepcion


def test_errores_negocio_con_campo_responde_errores_de_campo():
    respuesta = manejar_excepcion(ErrorNegocio("Mensaje.", campo="email"), {})

    assert respuesta.status_code == 400
    assert respuesta.data == {"errores": {"email": ["Mensaje."]}}


def test_errores_negocio_sin_campo_responde_detalle_con_su_estado():
    respuesta = manejar_excepcion(ErrorNegocio("Este encuentro ya comenzó.", estado=409), {})

    assert respuesta.status_code == 409
    assert respuesta.data == {"detalle": "Este encuentro ya comenzó."}


def test_errores_validacion_sin_campos_responde_detalle():
    respuesta = manejar_excepcion(ValidationError(["Mensaje general."]), {})

    assert respuesta.status_code == 400
    assert respuesta.data == {"detalle": "Mensaje general."}


def test_errores_otras_excepciones_de_la_api_responden_detalle():
    respuesta = manejar_excepcion(NotFound("No existe."), {})

    assert respuesta.status_code == 404
    assert respuesta.data == {"detalle": "No existe."}


def test_errores_onboarding_incompleto_responde_403_con_el_paso():
    respuesta = manejar_excepcion(OnboardingIncompleto("disponibilidad"), {})

    assert respuesta.status_code == 403
    assert respuesta.data == {
        "detalle": "Completá tu perfil para continuar.",
        "onboarding": "disponibilidad",
    }


def test_errores_excepciones_ajenas_a_la_api_no_se_convierten():
    assert manejar_excepcion(KeyError("x"), {}) is None


@pytest.mark.django_db
def test_errores_metodo_no_permitido_responde_detalle():
    respuesta = APIClient().get("/api/auth/registro")

    assert respuesta.status_code == 405
    assert set(respuesta.json()) == {"detalle"}
