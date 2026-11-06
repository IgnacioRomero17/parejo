import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.comun.errores import ErrorNegocio
from apps.localidades import servicios as servicios_localidades
from apps.usuarios import servicios as servicios_usuarios
from apps.usuarios.models import Usuario
from apps.usuarios.serializers import ActualizarPerfilSerializer

RUTA_DATASET = settings.BASE_DIR / "evaluacion" / "datasets" / "demo.json"


def _nombre(jugador: dict) -> str:
    return f"{jugador['nombre']} {jugador['apellido']}"


def _secciones(jugador: dict, ids_localidades: dict[str, int]) -> dict:
    """Valida un jugador del dataset como un `PATCH perfil` y devuelve sus secciones."""
    if jugador["localidad"] not in ids_localidades:
        raise CommandError(
            f"La localidad «{jugador['localidad']}» no está en el catálogo. Cargá primero las "
            "localidades con `python manage.py loaddata localidades`."
        )
    serializer = ActualizarPerfilSerializer(
        data={
            "datos_personales": {"nombre": jugador["nombre"], "apellido": jugador["apellido"]},
            "perfil_deportivo": {
                "edad": jugador["edad"],
                "genero": jugador["genero"],
                "localidad": ids_localidades[jugador["localidad"]],
                "frecuencia_juego": jugador["frecuencia_juego"],
                "nivel_estimado": jugador["nivel_estimado"],
            },
            "disponibilidad": {
                "franjas": jugador["franjas"],
                "tipo_encuentro": jugador["tipo_encuentro"],
                "lado_preferido": jugador["lado_preferido"],
                "disponible_para_invitaciones": jugador["disponible"],
            },
        }
    )
    if not serializer.is_valid():
        raise CommandError(f"Datos inválidos de {_nombre(jugador)}: {serializer.errors}")
    return serializer.validated_data


def leer_dataset() -> dict:
    """Lee el dataset de demostración (`demo.json`)."""
    return json.loads(RUTA_DATASET.read_text(encoding="utf-8"))


def cargar_dataset(reemplazar: bool) -> tuple[int, int]:
    """Carga los jugadores del dataset, identificados por su correo.

    Con `reemplazar`, restaura los que ya existen a los datos del archivo (sin cambiar la
    contraseña) y crea los que falten; los demás usuarios nunca se tocan. Devuelve la cantidad
    de jugadores creados y de actualizados. Lanza CommandError si el dataset ya está cargado
    y no se pidió reemplazar, si falta una localidad o si un jugador tiene datos inválidos.
    """
    dataset = leer_dataset()
    ids_localidades = {
        localidad.nombre: localidad.pk for localidad in servicios_localidades.listar_localidades()
    }
    jugadores = [
        (jugador, _secciones(jugador, ids_localidades)) for jugador in dataset["jugadores"]
    ]
    correos = [servicios_usuarios.normalizar_correo(j["email"]) for j, _ in jugadores]
    existentes = {u.email: u for u in Usuario.objects.filter(email__in=correos)}
    if existentes and not reemplazar:
        raise CommandError(
            f"El dataset de demostración ya está cargado ({len(existentes)} jugadores). "
            "Usá --reemplazar para restaurarlos; los demás usuarios no se tocan."
        )
    try:
        with transaction.atomic():
            for (jugador, secciones), correo in zip(jugadores, correos, strict=True):
                usuario = existentes.get(correo) or servicios_usuarios.registrar_usuario(
                    jugador["nombre"], jugador["apellido"], correo, dataset["contrasena"]
                )
                servicios_usuarios.actualizar_perfil(usuario, **secciones)
    except ErrorNegocio as error:
        raise CommandError(f"No se pudo cargar el dataset: {error.mensaje}") from error
    return len(jugadores) - len(existentes), len(existentes)


class Command(BaseCommand):
    help = (
        "Carga el dataset de demostración (evaluacion/datasets/demo.json). Los jugadores se "
        "identifican por su correo; los demás usuarios nunca se tocan y no se borra nada."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reemplazar",
            action="store_true",
            help="Si el dataset ya está cargado, restaura sus jugadores a los datos del archivo "
            "(sin cambiar la contraseña) y crea los que falten.",
        )

    def handle(self, *args, reemplazar=False, **opciones):
        creados, actualizados = cargar_dataset(reemplazar)
        self.stdout.write(
            self.style.SUCCESS(
                f"Dataset de demostración cargado: {creados} jugadores creados y "
                f"{actualizados} actualizados."
            )
        )
