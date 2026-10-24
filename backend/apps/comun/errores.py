from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

MENSAJE_SIN_SESION = "Iniciá sesión para continuar."


class ErrorNegocio(Exception):
    """Error de una regla de negocio, lanzado por los servicios.

    Con `campo` se responde como error de ese campo; sin él, como error general.
    """

    def __init__(self, mensaje: str, campo: str | None = None, estado: int = 400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo
        self.estado = estado


class OnboardingIncompleto(PermissionDenied):
    """403 para un usuario al que le falta un paso del onboarding; `paso` le dice al frontend
    adónde llevarlo ("perfil" o "disponibilidad")."""

    default_detail = "Completá tu perfil para continuar."

    def __init__(self, paso: str):
        super().__init__()
        self.paso = paso


def manejar_excepcion(exc, contexto):
    """Convierte las excepciones de la API al formato único `errores` / `detalle`."""
    if isinstance(exc, ErrorNegocio):
        if exc.campo:
            return Response({"errores": {exc.campo: [exc.mensaje]}}, status=exc.estado)
        return Response({"detalle": exc.mensaje}, status=exc.estado)

    respuesta = exception_handler(exc, contexto)
    if respuesta is None:
        return None

    # SessionAuthentication no envía WWW-Authenticate y DRF respondería 403 sin sesión.
    if isinstance(exc, NotAuthenticated):
        respuesta.status_code = status.HTTP_401_UNAUTHORIZED
        respuesta.data = {"detalle": MENSAJE_SIN_SESION}
    elif isinstance(exc, ValidationError) and isinstance(respuesta.data, dict):
        respuesta.data = {"errores": respuesta.data}
    elif isinstance(exc, ValidationError):
        respuesta.data = {"detalle": " ".join(str(mensaje) for mensaje in respuesta.data)}
    else:
        respuesta.data = {"detalle": str(getattr(exc, "detail", exc))}
    if isinstance(exc, OnboardingIncompleto):
        respuesta.data["onboarding"] = exc.paso
    return respuesta
