from django.db import models


class Localidad(models.Model):
    id_localidad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80, unique=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        db_table = "localidad"
        verbose_name_plural = "localidades"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(latitud__gte=-90, latitud__lte=90),
                name="localidad_latitud_rango",
            ),
            models.CheckConstraint(
                condition=models.Q(longitud__gte=-180, longitud__lte=180),
                name="localidad_longitud_rango",
            ),
        ]

    def __str__(self):
        return self.nombre
