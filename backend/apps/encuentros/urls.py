from django.urls import path

from apps.encuentros.vistas import EncuentrosVista, EncuentroVista

urlpatterns = [
    path("encuentros", EncuentrosVista.as_view(), name="encuentros"),
    path("encuentros/<int:id_encuentro>", EncuentroVista.as_view(), name="encuentro"),
]
