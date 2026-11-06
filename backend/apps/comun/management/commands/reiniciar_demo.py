from django.core.management.base import BaseCommand
from django.db import connection, transaction

from apps.comun.management.commands.cargar_datos import cargar_dataset, leer_dataset
from apps.encuentros import servicios as servicios_encuentros
from apps.usuarios import servicios as servicios_usuarios

RESPUESTA_CONFIRMACION = "si"


class Command(BaseCommand):
    help = (
        "Deja la demostración como recién cargada: borra todos los encuentros (con sus "
        "invitaciones, participaciones y propuestas) y restaura los jugadores del dataset, "
        "incluida su contraseña. No toca localidades, superusuarios ni otras cuentas."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--sin-confirmar",
            action="store_true",
            help="No pide confirmación antes de borrar (solo para tests).",
        )

    def handle(self, *args, sin_confirmar=False, **opciones):
        base = connection.settings_dict
        conteo = servicios_encuentros.contar_encuentros()
        self.stdout.write(f"Base: {base['HOST'] or 'localhost'} / {base['NAME']}")
        self.stdout.write(
            f"Se van a borrar {conteo.encuentros} encuentros, {conteo.invitaciones} "
            f"invitaciones y {conteo.propuestas} propuestas, y se restauran los jugadores "
            "del dataset."
        )
        # Se confirma antes de abrir la transacción para no dejarla abierta mientras se espera.
        if not sin_confirmar and not self._confirmado():
            self.stdout.write("Cancelado: no se borró nada.")
            return
        dataset = leer_dataset()
        correos = [jugador["email"] for jugador in dataset["jugadores"]]
        with transaction.atomic():
            borrado = servicios_encuentros.borrar_todos_los_encuentros()
            creados, actualizados = cargar_dataset(reemplazar=True)
            servicios_usuarios.restaurar_contrasena(correos, dataset["contrasena"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Demostración reiniciada: {borrado.encuentros} encuentros, "
                f"{borrado.invitaciones} invitaciones y {borrado.propuestas} propuestas "
                f"borrados; {actualizados} jugadores restaurados y {creados} creados."
            )
        )

    def _confirmado(self) -> bool:
        respuesta = input(f'Escribí "{RESPUESTA_CONFIRMACION}" para confirmar: ')
        return respuesta.strip().lower() == RESPUESTA_CONFIRMACION
