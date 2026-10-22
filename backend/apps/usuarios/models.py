from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower, Mod, Now
from django.db.models.lookups import Exact
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
