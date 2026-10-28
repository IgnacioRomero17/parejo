"""Copia del catálogo de localidades, independiente del fixture de la app."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Localidad:
    """Localidad del catálogo con sus coordenadas en grados decimales."""

    id: int
    nombre: str
    lat: float
    lon: float


LOCALIDADES = (
    Localidad(1, "Río Ceballos", -31.1667, -64.3167),
    Localidad(2, "Salsipuedes", -31.137222, -64.295833),
    Localidad(3, "Unquillo", -31.2333, -64.3167),
    Localidad(4, "Mendiolaza", -31.265, -64.3031),
    Localidad(5, "Villa Allende", -31.2944, -64.2953),
    Localidad(6, "Saldán", -31.3169, -64.3086),
    Localidad(7, "La Calera", -31.3439, -64.3353),
    Localidad(8, "Colonia Caroya", -31.0213, -64.0613),
    Localidad(9, "Jesús María", -30.9817, -64.0942),
    Localidad(10, "Villa Carlos Paz", -31.415901, -64.489469),
    Localidad(11, "Malagueño", -31.4639, -64.3575),
    Localidad(12, "Córdoba – Nueva Córdoba", -31.426111, -64.185806),
    Localidad(13, "Córdoba – Centro", -31.4167, -64.1833),
    Localidad(14, "Córdoba – Alta Córdoba", -31.3892, -64.1842),
    Localidad(15, "Córdoba – Cerro de las Rosas", -31.368, -64.233),
    Localidad(16, "Córdoba – Argüello", -31.346944, -64.253333),
)

POR_NOMBRE = {localidad.nombre: localidad for localidad in LOCALIDADES}
