import pytest
from rest_framework.test import APIClient

from apps.comun.errores import ErrorNegocio
from apps.localidades.servicios import obtener_localidad
from tests.fabricas import crear_localidad, crear_usuario

pytestmark = pytest.mark.django_db

URL_LOCALIDADES = "/api/localidades"


def test_hu004_p5_lista_el_catalogo_en_orden_alfabetico():
    unquillo = crear_localidad(nombre="Unquillo")
    jesus_maria = crear_localidad(nombre="Jesús María")
    colonia_caroya = crear_localidad(nombre="Colonia Caroya")
    cliente = APIClient()
    cliente.force_login(crear_usuario())

    respuesta = cliente.get(URL_LOCALIDADES)

    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {"id": colonia_caroya.id_localidad, "nombre": "Colonia Caroya"},
        {"id": jesus_maria.id_localidad, "nombre": "Jesús María"},
        {"id": unquillo.id_localidad, "nombre": "Unquillo"},
    ]


def test_hu004_localidades_sin_sesion_responde_401():
    respuesta = APIClient().get(URL_LOCALIDADES)

    assert respuesta.status_code == 401


def test_hu004_p5_obtener_localidad_inexistente_lanza_error():
    with pytest.raises(ErrorNegocio) as error:
        obtener_localidad(12345)

    assert error.value.campo == "localidad"
    assert error.value.mensaje == "Elegí una opción del listado."
