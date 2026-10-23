from django.urls import path

from apps.localidades.vistas import LocalidadesVista

urlpatterns = [
    path("localidades", LocalidadesVista.as_view(), name="localidades"),
]
