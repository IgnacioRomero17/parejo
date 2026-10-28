from django.urls import path

from apps.encuentros.vistas import (
    AceptarInvitacionVista,
    EncuentrosVista,
    EncuentroVista,
    FormarParejasVista,
    InvitacionesEncuentroVista,
    InvitacionesVista,
    PropuestaVista,
    RechazarInvitacionVista,
    RecomendadosVista,
)

urlpatterns = [
    path("encuentros", EncuentrosVista.as_view(), name="encuentros"),
    path("encuentros/<int:id_encuentro>", EncuentroVista.as_view(), name="encuentro"),
    path(
        "encuentros/<int:id_encuentro>/recomendados",
        RecomendadosVista.as_view(),
        name="recomendados",
    ),
    path(
        "encuentros/<int:id_encuentro>/invitaciones",
        InvitacionesEncuentroVista.as_view(),
        name="encuentro-invitaciones",
    ),
    path(
        "encuentros/<int:id_encuentro>/formar-parejas",
        FormarParejasVista.as_view(),
        name="formar-parejas",
    ),
    path(
        "encuentros/<int:id_encuentro>/propuesta",
        PropuestaVista.as_view(),
        name="propuesta",
    ),
    path("invitaciones", InvitacionesVista.as_view(), name="invitaciones"),
    path(
        "invitaciones/<int:id_invitacion>/aceptar",
        AceptarInvitacionVista.as_view(),
        name="invitacion-aceptar",
    ),
    path(
        "invitaciones/<int:id_invitacion>/rechazar",
        RechazarInvitacionVista.as_view(),
        name="invitacion-rechazar",
    ),
]
