from decimal import Decimal

from apps.localidades.models import Localidad
from apps.usuarios.models import Usuario


def crear_localidad(**campos) -> Localidad:
    datos = {
        "nombre": "Río Ceballos",
        "latitud": Decimal("-31.166700"),
        "longitud": Decimal("-64.316700"),
    }
    datos.update(campos)
    return Localidad.objects.create(**datos)


def crear_usuario(**campos) -> Usuario:
    datos = {
        "email": "jugador@example.com",
        "password": "clave1234",
        "nombre": "Ana",
        "apellido": "Pérez",
    }
    datos.update(campos)
    return Usuario.objects.create_user(**datos)
