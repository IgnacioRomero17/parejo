from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower, Mod, Now
from django.db.models.lookups import Exact, GreaterThanOrEqual
from django.utils import timezone

from apps.localidades.models import Localidad


class Genero(models.TextChoices):
    MASCULINO = "MASCULINO", "Masculino"
    FEMENINO = "FEMENINO", "Femenino"
    NO_DECLARA = "NO_DECLARA", "Prefiero no decirlo"


class FrecuenciaJuego(models.TextChoices):
    MENOS_1_SEMANA = "MENOS_1_SEMANA", "Menos de 1 vez por semana"
    UNA_SEMANA = "1_SEMANA", "1 vez por semana"
    DOS_TRES_SEMANA = "2_3_SEMANA", "2 o 3 veces por semana"
    CUATRO_MAS_SEMANA = "4_MAS_SEMANA", "4 o más veces por semana"


class TipoEncuentro(models.TextChoices):
    RECREATIVO = "RECREATIVO", "Recreativo"
    COMPETITIVO = "COMPETITIVO", "Competitivo"
    INDIFERENTE = "INDIFERENTE", "Indiferente"


class LadoPreferido(models.TextChoices):
    DRIVE = "DRIVE", "Drive"
    REVES = "REVES", "Revés"
    INDIFERENTE = "INDIFERENTE", "Indiferente"


class DiaSemana(models.IntegerChoices):
    LUNES = 1, "Lunes"
    MARTES = 2, "Martes"
    MIERCOLES = 3, "Miércoles"
    JUEVES = 4, "Jueves"
    VIERNES = 5, "Viernes"
    SABADO = 6, "Sábado"
    DOMINGO = 7, "Domingo"


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **campos):
        if not email:
            raise ValueError("El correo es obligatorio.")
        usuario = self.model(email=email.strip().lower(), **campos)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **campos):
        campos.setdefault("is_staff", True)
        campos.setdefault("is_superuser", True)
        return self.create_user(email, password, **campos)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField("contraseña", max_length=128, db_column="password_hash")
    nombre = models.CharField(max_length=60)
    apellido = models.CharField(max_length=60)
    edad = models.SmallIntegerField(null=True, blank=True)
    genero = models.CharField(max_length=15, choices=Genero.choices, null=True, blank=True)
    frecuencia_juego = models.CharField(
        max_length=20, choices=FrecuenciaJuego.choices, null=True, blank=True
    )
    nivel_estimado = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    localidad = models.ForeignKey(
        Localidad,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="id_localidad",
        related_name="usuarios",
    )
    # default completa el objeto en Python; db_default replica el DEFAULT de esquema.sql.
    disponible_para_invitaciones = models.BooleanField(default=False, db_default=False)
    is_active = models.BooleanField(default=True, db_default=True, db_column="activo")
    is_staff = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(default=timezone.now, db_default=Now())

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["nombre", "apellido"]

    class Meta:
        db_table = "usuario"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(email=Lower("email")),
                name="usuario_email_minusculas",
            ),
            models.CheckConstraint(
                condition=models.Q(edad__gte=18, edad__lte=99),
                name="usuario_edad_rango",
            ),
            models.CheckConstraint(
                condition=models.Q(genero__in=Genero.values),
                name="usuario_genero_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(frecuencia_juego__in=FrecuenciaJuego.values),
                name="usuario_frecuencia_juego_valida",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        nivel_estimado__gte=Decimal("1.0"), nivel_estimado__lte=Decimal("7.0")
                    ),
                    Exact(Mod(models.F("nivel_estimado") * 10, 5), 0),
                ),
                name="usuario_nivel_estimado_valido",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def perfil_completo(self):
        return self.nivel_estimado is not None and self.localidad_id is not None


class Preferencia(models.Model):
    id_preferencia = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario",
        related_name="preferencia",
    )
    tipo_encuentro = models.CharField(max_length=12, choices=TipoEncuentro.choices)
    lado_preferido = models.CharField(max_length=12, choices=LadoPreferido.choices)

    class Meta:
        db_table = "preferencia"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(tipo_encuentro__in=TipoEncuentro.values),
                name="preferencia_tipo_encuentro_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(lado_preferido__in=LadoPreferido.values),
                name="preferencia_lado_preferido_valido",
            ),
        ]


class Disponibilidad(models.Model):
    id_disponibilidad = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario",
        related_name="disponibilidades",
    )
    dia_semana = models.SmallIntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        db_table = "disponibilidad"
        ordering = ["dia_semana", "hora_inicio"]
        indexes = [
            models.Index(fields=["usuario", "dia_semana"], name="disponibilidad_usuario_dia"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(dia_semana__gte=1, dia_semana__lte=7),
                name="disponibilidad_dia_semana_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F("hora_inicio")),
                name="disponibilidad_orden",
            ),
            models.CheckConstraint(
                condition=GreaterThanOrEqual(
                    models.ExpressionWrapper(
                        models.F("hora_fin") - models.F("hora_inicio"),
                        output_field=models.DurationField(),
                    ),
                    timedelta(minutes=60),
                ),
                name="disponibilidad_minimo",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    hora_inicio__second=0,
                    hora_fin__second=0,
                    hora_inicio__minute__in=(0, 30),
                    hora_fin__minute__in=(0, 30),
                ),
                name="disponibilidad_paso_30",
            ),
        ]

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_inicio:%H:%M}–{self.hora_fin:%H:%M}"
