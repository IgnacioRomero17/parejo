from django.db.models import QuerySet

from apps.comun.errores import ErrorNegocio
from apps.localidades.models import Localidad

MENSAJE_LOCALIDAD_INVALIDA = "Elegí una opción del listado."
ID_MAXIMO = 2_147_483_647  # máximo de la columna integer de id_localidad


def listar_localidades() -> QuerySet[Localidad]:
    """Devuelve el catálogo cerrado de localidades en orden alfabético (HU-004, HU-006)."""
    return Localidad.objects.order_by("nombre", "id_localidad")


def obtener_localidad(id_localidad: int) -> Localidad:
    """Devuelve la localidad del catálogo con ese id.

    Lanza ErrorNegocio en el campo `localidad` si no existe.
    """
    # Un id fuera del rango de la columna haría fallar la consulta en PostgreSQL.
    if not 0 < id_localidad <= ID_MAXIMO:
        raise ErrorNegocio(MENSAJE_LOCALIDAD_INVALIDA, campo="localidad")
    localidad = Localidad.objects.filter(pk=id_localidad).first()
    if localidad is None:
        raise ErrorNegocio(MENSAJE_LOCALIDAD_INVALIDA, campo="localidad")
    return localidad
