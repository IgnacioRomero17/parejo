from rest_framework.permissions import BasePermission

from apps.comun.errores import OnboardingIncompleto
from apps.usuarios import servicios


class OnboardingCompleto(BasePermission):
    """Exige el perfil completo y la preferencia cargada; si falta, 403 con el paso pendiente."""

    def has_permission(self, request, view):
        paso = servicios.paso_onboarding_pendiente(request.user)
        if paso is not None:
            raise OnboardingIncompleto(paso)
        return True
