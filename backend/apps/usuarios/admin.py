from django.contrib import admin

from apps.usuarios.models import Disponibilidad, Preferencia, Usuario


class PreferenciaEnLinea(admin.TabularInline):
    model = Preferencia
    extra = 0


class DisponibilidadEnLinea(admin.TabularInline):
    model = Disponibilidad
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Los usuarios se crean al registrarse, con createsuperuser o con cargar_datos, y la baja
    de cuentas está fuera de alcance: en el admin solo se ven y se editan, sin la contraseña."""

    fieldsets = [
        (
            "Datos personales",
            {"fields": ["email", "nombre", "apellido", "edad", "genero", "frecuencia_juego"]},
        ),
        (
            "Perfil de juego",
            {"fields": ["nivel_estimado", "localidad", "disponible_para_invitaciones"]},
        ),
        (
            "Acceso",
            {"fields": ["is_active", "is_staff", "is_superuser", "last_login", "fecha_registro"]},
        ),
    ]
    readonly_fields = ["last_login", "fecha_registro"]
    list_display = [
        "id_usuario",
        "email",
        "nombre",
        "apellido",
        "nivel_estimado",
        "localidad",
        "is_active",
    ]
    search_fields = ["email", "nombre", "apellido"]
    ordering = ["id_usuario"]
    inlines = [PreferenciaEnLinea, DisponibilidadEnLinea]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
