from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

from apps.encuentros import servicios


class EsParticipante(BasePermission):
    """Solo los participantes confirmados del encuentro, organizador incluido.

    A quien no participa se le responde 404, como si el encuentro no existiera.
    """

    def has_object_permission(self, request, view, encuentro):
        if not servicios.es_participante(request.user, encuentro):
            raise NotFound(servicios.MENSAJE_ENCUENTRO_INEXISTENTE)
        return True
