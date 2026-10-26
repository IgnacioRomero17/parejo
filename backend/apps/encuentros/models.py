from django.db import models
from django.db.models.functions import ExtractHour, ExtractMinute, Now
from django.db.models.lookups import LessThanOrEqual
from django.utils import timezone

from apps.localidades.models import Localidad
from apps.usuarios.models import TipoEncuentro, Usuario
from motor.parametros import PARAMETROS

DURACIONES_MINUTOS = (60, 90, 120)
MINUTOS_FIN_MAXIMO = 23 * 60 + 30  # el encuentro termina a las 23:30 como máximo


class EstadoEncuentro(models.TextChoices):
    CREADO = "CREADO", "Creado"
    BUSCANDO_PARTICIPANTES = "BUSCANDO_PARTICIPANTES", "Buscando participantes"
    COMPLETO = "COMPLETO", "Completo"
    PROPUESTA_GENERADA = "PROPUESTA_GENERADA", "Propuesta generada"


class EstadoInvitacion(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    ACEPTADA = "ACEPTADA", "Aceptada"
    RECHAZADA = "RECHAZADA", "Rechazada"


class Encuentro(models.Model):
    id_encuentro = models.AutoField(primary_key=True)
    organizador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        db_column="id_organizador",
        related_name="encuentros_organizados",
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    duracion_minutos = models.SmallIntegerField()
    localidad = models.ForeignKey(
        Localidad,
        on_delete=models.PROTECT,
        db_column="id_localidad",
        related_name="encuentros",
    )
    ubicacion = models.CharField(max_length=150)
    tipo_encuentro = models.CharField(max_length=12, choices=TipoEncuentro.choices)
    # default completa el objeto en Python; db_default replica el DEFAULT de esquema.sql.
    estado = models.CharField(
        max_length=25,
        choices=EstadoEncuentro.choices,
        default=EstadoEncuentro.CREADO,
        db_default=EstadoEncuentro.CREADO,
    )
    fecha_creacion = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "encuentro"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duracion_minutos__in=DURACIONES_MINUTOS),
                name="encuentro_duracion_valida",
            ),
            models.CheckConstraint(
                condition=models.Q(tipo_encuentro__in=TipoEncuentro.values),
                name="encuentro_tipo_encuentro_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(estado__in=EstadoEncuentro.values),
                name="encuentro_estado_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(hora_inicio__second=0, hora_inicio__minute__in=(0, 30)),
                name="encuentro_paso_30",
            ),
            models.CheckConstraint(
                condition=LessThanOrEqual(
                    ExtractHour("hora_inicio") * 60
                    + ExtractMinute("hora_inicio")
                    + models.F("duracion_minutos"),
                    MINUTOS_FIN_MAXIMO,
                ),
                name="encuentro_no_cruza_medianoche",
            ),
        ]

    def __str__(self):
        return f"Encuentro {self.id_encuentro} · {self.fecha} {self.hora_inicio:%H:%M}"

    def lugares_libres(self) -> int:
        """4 − participantes confirmados − invitaciones pendientes (única implementación)."""
        pendientes = self.invitaciones.filter(estado=EstadoInvitacion.PENDIENTE).count()
        return PARAMETROS.lugares_por_encuentro - self.participantes.count() - pendientes


class Invitacion(models.Model):
    id_invitacion = models.AutoField(primary_key=True)
    encuentro = models.ForeignKey(
        Encuentro,
        on_delete=models.CASCADE,
        db_column="id_encuentro",
        related_name="invitaciones",
    )
    usuario_invitado = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        db_column="id_usuario_invitado",
        related_name="invitaciones_recibidas",
    )
    # default completa el objeto en Python; db_default replica el DEFAULT de esquema.sql.
    estado = models.CharField(
        max_length=10,
        choices=EstadoInvitacion.choices,
        default=EstadoInvitacion.PENDIENTE,
        db_default=EstadoInvitacion.PENDIENTE,
    )
    fecha_envio = models.DateTimeField(default=timezone.now, db_default=Now())
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invitacion"
        verbose_name_plural = "invitaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["encuentro", "usuario_invitado"],
                name="invitacion_unica",
            ),
            models.CheckConstraint(
                condition=models.Q(estado__in=EstadoInvitacion.values),
                name="invitacion_estado_valido",
            ),
            # (estado = 'PENDIENTE') = (fecha_respuesta IS NULL)
            models.CheckConstraint(
                condition=models.Q(estado=EstadoInvitacion.PENDIENTE, fecha_respuesta__isnull=True)
                | (
                    ~models.Q(estado=EstadoInvitacion.PENDIENTE)
                    & models.Q(fecha_respuesta__isnull=False)
                ),
                name="invitacion_respuesta",
            ),
        ]

    def __str__(self):
        return f"Invitación de {self.usuario_invitado} al encuentro {self.encuentro_id}"


class Participante(models.Model):
    id_participante = models.AutoField(primary_key=True)
    encuentro = models.ForeignKey(
        Encuentro,
        on_delete=models.CASCADE,
        db_column="id_encuentro",
        related_name="participantes",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        db_column="id_usuario",
        related_name="participaciones",
    )
    fecha_confirmacion = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "participante"
        constraints = [
            models.UniqueConstraint(
                fields=["encuentro", "usuario"],
                name="participante_unico",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} en el encuentro {self.encuentro_id}"
