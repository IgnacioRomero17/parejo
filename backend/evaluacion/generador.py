"""Jugadores y escenarios aleatorios sintéticos, reproducibles con la semilla."""

import math
import random
from dataclasses import dataclass
from datetime import date, time, timedelta

from evaluacion.localidades import LOCALIDADES, Localidad
from motor.tipos import (
    COMPETITIVO,
    DRIVE,
    INDIFERENTE,
    RECREATIVO,
    REVES,
    CandidatoEntrada,
    EncuentroEntrada,
    Franja,
)

SEMILLA = 2026
CANTIDAD_JUGADORES = 200
CANTIDAD_ESCENARIOS = 150

NIVEL_MEDIA = 4.0
NIVEL_DESVIO = 1.2
NIVEL_MINIMO = 1.0
NIVEL_MAXIMO = 7.0
TIPOS = (RECREATIVO, COMPETITIVO, INDIFERENTE)
PESOS_TIPO = (35, 35, 30)
LADOS = (DRIVE, REVES, INDIFERENTE)
PESOS_LADO = (40, 40, 20)
PROPORCION_DISPONIBLES = 0.85
FRANJAS_MINIMAS = 1
FRANJAS_MAXIMAS = 3
# 1 = lunes … 7 = domingo: el fin de semana pesa el doble.
PESO_POR_DIA = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2}

# Las horas se manejan como índices de media hora desde las 00:00 (16 = 08:00, 46 = 23:00).
MEDIA_HORA_MINUTOS = 30
PRIMERA_MEDIA_HORA = 16
ULTIMA_MEDIA_HORA_FRANJA = 46
ULTIMA_MEDIA_HORA_ENCUENTRO = 43
DURACION_FRANJA_MINIMA = 4
DURACION_FRANJA_MAXIMA = 8

FECHA_BASE = date(2026, 11, 2)
DIAS_HACIA_ADELANTE = 14
DURACIONES = (60, 90, 120)
LUGARES_LIBRES = 3


@dataclass(frozen=True)
class JugadorSintetico:
    """Jugador generado: su entrada para el motor, su localidad y su lado preferido."""

    candidato: CandidatoEntrada
    localidad: Localidad
    lado: str


@dataclass(frozen=True)
class EscenarioAleatorio:
    """Encuentro generado con solo el organizador confirmado."""

    numero: int
    encuentro: EncuentroEntrada
    organizador_id: int
    lugares_libres: int


def _hora(media_hora: int) -> time:
    return time(media_hora // 2, MEDIA_HORA_MINUTOS * (media_hora % 2))


def _nivel(generador: random.Random) -> float:
    # Redondeo a 0,5 hacia arriba en el medio: round() redondea al par.
    nivel = math.floor(generador.gauss(NIVEL_MEDIA, NIVEL_DESVIO) * 2 + 0.5) / 2
    return min(max(nivel, NIVEL_MINIMO), NIVEL_MAXIMO)


def _dias(generador: random.Random, cantidad: int) -> list[int]:
    # Sin reposición: dos franjas nunca caen el mismo día, así no hay superposiciones.
    restantes = list(PESO_POR_DIA)
    dias = []
    for _ in range(cantidad):
        dia = generador.choices(restantes, weights=[PESO_POR_DIA[d] for d in restantes])[0]
        restantes.remove(dia)
        dias.append(dia)
    return dias


def _franja(generador: random.Random, dia: int) -> Franja:
    duracion = generador.randint(DURACION_FRANJA_MINIMA, DURACION_FRANJA_MAXIMA)
    inicio = generador.randint(PRIMERA_MEDIA_HORA, ULTIMA_MEDIA_HORA_FRANJA - duracion)
    return Franja(dia=dia, inicio=_hora(inicio), fin=_hora(inicio + duracion))


def _franjas(generador: random.Random) -> tuple[Franja, ...]:
    cantidad = generador.randint(FRANJAS_MINIMAS, FRANJAS_MAXIMAS)
    franjas = (_franja(generador, dia) for dia in _dias(generador, cantidad))
    return tuple(sorted(franjas, key=lambda franja: (franja.dia, franja.inicio)))


def _jugador(generador: random.Random, identificador: int) -> JugadorSintetico:
    nivel = _nivel(generador)
    localidad = generador.choice(LOCALIDADES)
    tipo_preferido = generador.choices(TIPOS, weights=PESOS_TIPO)[0]
    lado = generador.choices(LADOS, weights=PESOS_LADO)[0]
    disponible = generador.random() < PROPORCION_DISPONIBLES
    candidato = CandidatoEntrada(
        id=identificador,
        activo=True,
        disponible=disponible,
        nivel=nivel,
        lat=localidad.lat,
        lon=localidad.lon,
        tipo_preferido=tipo_preferido,
        franjas=_franjas(generador),
    )
    return JugadorSintetico(candidato=candidato, localidad=localidad, lado=lado)


def generar_jugadores(
    semilla: int = SEMILLA, cantidad: int = CANTIDAD_JUGADORES
) -> tuple[JugadorSintetico, ...]:
    """Genera jugadores sintéticos con ids de 1 a `cantidad`, todos con perfil completo.

    Nivel normal(4, 1,2) redondeado a 0,5 y acotado a 1–7; localidad uniforme sobre el
    catálogo; tipo Recreativo/Competitivo/Indiferente 35/35/30 %; lado Drive/Revés/Indiferente
    40/40/20 %; 85 % disponibles y todos activos; 1 a 3 franjas en días distintos (el fin de
    semana pesa el doble), de 2 a 4 horas en pasos de 30 min, entre las 08:00 y las 23:00.
    Usa su propio `random.Random(semilla)`: misma semilla, mismos jugadores.
    """
    generador = random.Random(semilla)
    return tuple(_jugador(generador, identificador) for identificador in range(1, cantidad + 1))


def _escenario(
    generador: random.Random, numero: int, jugadores: tuple[JugadorSintetico, ...]
) -> EscenarioAleatorio:
    organizador = generador.choice(jugadores).candidato
    fecha = FECHA_BASE + timedelta(days=generador.randint(1, DIAS_HACIA_ADELANTE))
    hora_inicio = _hora(generador.randint(PRIMERA_MEDIA_HORA, ULTIMA_MEDIA_HORA_ENCUENTRO))
    duracion_minutos = generador.choice(DURACIONES)
    localidad = generador.choice(LOCALIDADES)
    tipo = generador.choice(TIPOS)
    encuentro = EncuentroEntrada(
        fecha=fecha,
        hora_inicio=hora_inicio,
        duracion_minutos=duracion_minutos,
        lat=localidad.lat,
        lon=localidad.lon,
        tipo=tipo,
        niveles_confirmados=(organizador.nivel,),
        ids_excluidos=frozenset({organizador.id}),
    )
    return EscenarioAleatorio(
        numero=numero,
        encuentro=encuentro,
        organizador_id=organizador.id,
        lugares_libres=LUGARES_LIBRES,
    )


def generar_escenarios(
    jugadores: tuple[JugadorSintetico, ...],
    semilla: int = SEMILLA,
    cantidad: int = CANTIDAD_ESCENARIOS,
) -> tuple[EscenarioAleatorio, ...]:
    """Genera encuentros al azar organizados por alguno de `jugadores`.

    Fecha entre 1 y 14 días después de FECHA_BASE, hora de 08:00 a 21:30 en medias horas,
    duración 60/90/120, localidad del catálogo y tipo uniformes. Solo el organizador está
    confirmado, así que quedan 3 lugares libres. Usa su propio `random.Random(semilla)`.
    """
    generador = random.Random(semilla)
    return tuple(_escenario(generador, numero, jugadores) for numero in range(1, cantidad + 1))
