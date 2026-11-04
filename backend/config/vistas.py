from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe


@require_safe
@never_cache  # El index.html apunta a archivos con hash: tras publicar, tiene que pedirse de nuevo.
def servir_frontend(request):
    """Devuelve el index.html compilado, para que React Router resuelva la ruta en el navegador."""
    try:
        contenido = (settings.DIR_FRONTEND_COMPILADO / "index.html").read_bytes()
    except FileNotFoundError as error:
        raise Http404("El frontend no está compilado.") from error
    return HttpResponse(contenido, content_type="text/html; charset=utf-8")
