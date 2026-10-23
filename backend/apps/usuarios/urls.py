from django.urls import path

from apps.usuarios.vistas import (
    CsrfVista,
    IngresoVista,
    RegistroVista,
    SalirVista,
    UsuarioActualVista,
)

urlpatterns = [
    path("auth/csrf", CsrfVista.as_view(), name="auth-csrf"),
    path("auth/registro", RegistroVista.as_view(), name="auth-registro"),
    path("auth/ingresar", IngresoVista.as_view(), name="auth-ingresar"),
    path("auth/salir", SalirVista.as_view(), name="auth-salir"),
    path("auth/yo", UsuarioActualVista.as_view(), name="auth-yo"),
]
