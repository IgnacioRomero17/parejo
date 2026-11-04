from django.contrib import admin
from django.urls import include, path, re_path

from config.vistas import servir_frontend

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.usuarios.urls")),
    path("api/", include("apps.localidades.urls")),
    path("api/", include("apps.encuentros.urls")),
    # Va última y excluye estos prefijos: una ruta desconocida de la API sigue dando 404 y
    # /admin sigue redirigiendo a /admin/.
    re_path(r"^(?!(?:api|admin|static)(?:/|$)).*$", servir_frontend),
]
