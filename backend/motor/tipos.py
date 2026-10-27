from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal

RECREATIVO = "RECREATIVO"
COMPETITIVO = "COMPETITIVO"
INDIFERENTE = "INDIFERENTE"
DRIVE = "DRIVE"
REVES = "REVES"


@dataclass(frozen=True)
class Franja:
    """Franja de disponibilidad: `dia` 1 = lunes … 7 = domingo."""

    dia: int
    inicio: time
    fin: time


@dataclass(frozen=True)
class EncuentroEntrada:
    """Condiciones del encuentro para la etapa 1.

    `lat` y `lon` son los de su localidad; `tipo` es RECREATIVO, COMPETITIVO o INDIFERENTE;
    `niveles_confirmados` incluye al organizador (al menos 1); `ids_excluidos` tiene al
    organizador, los participantes y los invitados en cualquier estado.
    """

    fecha: date
    hora_inicio: time
    duracion_minutos: int
    lat: float
    lon: float
    tipo: str
    niveles_confirmados: tuple[float, ...]
    ids_excluidos: frozenset[int]


@dataclass(frozen=True)
class CandidatoEntrada:
    """Jugador a evaluar. `nivel`, `lat`, `lon` y `tipo_preferido` pueden faltar (None)."""

    id: int
    activo: bool
    disponible: bool
    nivel: float | None
    lat: float | None
    lon: float | None
    tipo_preferido: str | None
    franjas: tuple[Franja, ...]


@dataclass(frozen=True)
class Recomendacion:
    """Candidato recomendado, con su puntaje redondeado y los valores que lo explican."""

    id: int
    puntaje: Decimal
    c_nivel: float
    c_geo: float
    c_tipo: float
    distancia_km: float
    dif_nivel: float


@dataclass(frozen=True)
class ResultadoRecomendacion:
    """Recomendados en orden y si alcanzan para los lugares libres."""

    recomendados: tuple[Recomendacion, ...]
    suficientes: bool


@dataclass(frozen=True)
class JugadorEntrada:
    """Participante confirmado para la etapa 2. `lado` es DRIVE, REVES, INDIFERENTE o None."""

    id: int
    nivel: float
    lado: str | None


@dataclass(frozen=True)
class CombinacionResultado:
    """Una de las 3 combinaciones: cada pareja con sus 2 ids en orden, sus promedios, los
    equilibrios de nivel y de lado y el puntaje redondeado. La Pareja 1 contiene al menor id."""

    numero: int
    pareja1: tuple[int, int]
    pareja2: tuple[int, int]
    promedio1: float
    promedio2: float
    eq_nivel: float
    eq_lado: float
    puntaje: Decimal
