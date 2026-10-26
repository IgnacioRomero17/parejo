from django.urls import path

from apps.encuentros.vistas import EncuentrosVista, EncuentroVista, RecomendadosVista

urlpatterns = [
    path("encuentros", EncuentrosVista.as_view(), name="encuentros"),
    path("encuentros/<int:id_encuentro>", EncuentroVista.as_view(), name="encuentro"),
    path(
        "encuentros/<int:id_encuentro>/recomendados",
        RecomendadosVista.as_view(),
        name="recomendados",
    ),
]
