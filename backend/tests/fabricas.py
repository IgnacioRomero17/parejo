from datetime import date, time, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.encuentros.models import Encuentro, EstadoEncuentro, Participante
from apps.localidades.models import Localidad
from apps.usuarios.models import (
    DiaSemana,
    Disponibilidad,
    FrecuenciaJuego,
    Genero,
    LadoPreferido,
    Preferencia,
    TipoEncuentro,
    Usuario,
)


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


def crear_usuario_con_perfil(**campos) -> Usuario:
    """Usuario con el perfil deportivo completo (HU-004); crea la localidad si no se pasa."""
    datos = {
        "edad": 30,
        "genero": Genero.FEMENINO,
        "frecuencia_juego": FrecuenciaJuego.UNA_SEMANA,
        "nivel_estimado": Decimal("4.0"),
    }
    datos.update(campos)
    if "localidad" not in datos:
        datos["localidad"] = crear_localidad()
    return crear_usuario(**datos)


def crear_preferencia(usuario: Usuario, **campos) -> Preferencia:
    datos = {"tipo_encuentro": TipoEncuentro.RECREATIVO, "lado_preferido": LadoPreferido.DRIVE}
    datos.update(campos)
    return Preferencia.objects.create(usuario=usuario, **datos)


def crear_franja(usuario: Usuario, **campos) -> Disponibilidad:
    datos = {"dia_semana": DiaSemana.SABADO, "hora_inicio": time(17), "hora_fin": time(21)}
    datos.update(campos)
    return Disponibilidad.objects.create(usuario=usuario, **datos)


def crear_usuario_con_onboarding(**campos) -> Usuario:
    """Usuario con los dos pasos del onboarding hechos (HU-004 y HU-005), sin franjas."""
    usuario = crear_usuario_con_perfil(**campos)
    crear_preferencia(usuario)
    return usuario


def proximo_sabado() -> date:
    """El próximo sábado posterior a hoy (en la zona horaria del sistema)."""
    hoy = timezone.localdate()
    return hoy + timedelta(days=(5 - hoy.weekday()) % 7 or 7)


def crear_encuentro(organizador: Usuario, **campos) -> Encuentro:
    """Encuentro buscando participantes, con el organizador como participante 1."""
    datos = {
        "fecha": proximo_sabado(),
        "hora_inicio": time(18),
        "duracion_minutos": 90,
        "localidad": organizador.localidad,
        "ubicacion": "Av. San Martín 4500",
        "tipo_encuentro": TipoEncuentro.COMPETITIVO,
        "estado": EstadoEncuentro.BUSCANDO_PARTICIPANTES,
    }
    datos.update(campos)
    encuentro = Encuentro.objects.create(organizador=organizador, **datos)
    Participante.objects.create(encuentro=encuentro, usuario=organizador)
    return encuentro
