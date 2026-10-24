from django.contrib import admin

from apps.encuentros.models import Encuentro, Participante


class ParticipanteEnLinea(admin.TabularInline):
    model = Participante
    extra = 0
    raw_id_fields = ["usuario"]


@admin.register(Encuentro)
class EncuentroAdmin(admin.ModelAdmin):
    list_display = ["id_encuentro", "fecha", "hora_inicio", "localidad", "estado", "organizador"]
    list_filter = ["estado"]
    ordering = ["fecha", "hora_inicio"]
    raw_id_fields = ["organizador"]
    inlines = [ParticipanteEnLinea]
