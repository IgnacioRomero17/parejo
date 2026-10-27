from django.contrib import admin

from apps.encuentros.models import (
    Combinacion,
    Encuentro,
    Invitacion,
    Participante,
    PropuestaEncuentro,
)


class ParticipanteEnLinea(admin.TabularInline):
    model = Participante
    extra = 0
    raw_id_fields = ["usuario"]


class InvitacionEnLinea(admin.TabularInline):
    model = Invitacion
    extra = 0
    raw_id_fields = ["usuario_invitado"]


@admin.register(Encuentro)
class EncuentroAdmin(admin.ModelAdmin):
    list_display = ["id_encuentro", "fecha", "hora_inicio", "localidad", "estado", "organizador"]
    list_filter = ["estado"]
    ordering = ["fecha", "hora_inicio"]
    raw_id_fields = ["organizador"]
    inlines = [ParticipanteEnLinea, InvitacionEnLinea]


class SoloLecturaAdmin(admin.ModelAdmin):
    """Las combinaciones y las propuestas las genera el sistema: en el admin solo se revisan."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Combinacion)
class CombinacionAdmin(SoloLecturaAdmin):
    list_display = ["id_combinacion", "encuentro", "puntaje_equilibrio", "fecha_evaluacion"]
    ordering = ["encuentro", "id_combinacion"]


@admin.register(PropuestaEncuentro)
class PropuestaEncuentroAdmin(SoloLecturaAdmin):
    list_display = ["id_propuesta", "encuentro", "combinacion", "fecha_generacion"]
    ordering = ["-fecha_generacion"]
