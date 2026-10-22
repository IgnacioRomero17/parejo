from django.contrib import admin

from apps.localidades.models import Localidad


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ["nombre", "latitud", "longitud"]
    ordering = ["nombre"]
