from django.urls import path

from apps.usuarios.vistas import CsrfVista, RegistroVista, UsuarioActualVista

urlpatterns = [
    path("auth/csrf", CsrfVista.as_view(), name="auth-csrf"),
    path("auth/registro", RegistroVista.as_view(), name="auth-registro"),
    path("auth/yo", UsuarioActualVista.as_view(), name="auth-yo"),
]
