from django.urls import path

from apps.usuarios.vistas import (
    ConfirmarRecuperacionVista,
    CsrfVista,
    EnlaceRecuperacionVista,
    IngresoVista,
    RecuperacionVista,
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
    path("auth/recuperar", RecuperacionVista.as_view(), name="auth-recuperar"),
    path(
        "auth/recuperar/confirmar",
        ConfirmarRecuperacionVista.as_view(),
        name="auth-recuperar-confirmar",
    ),
    path(
        "auth/recuperar/<str:uid>/<str:token>",
        EnlaceRecuperacionVista.as_view(),
        name="auth-recuperar-enlace",
    ),
]
