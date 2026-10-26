from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.encuentros import servicios
from apps.encuentros.permisos import EsOrganizador, EsParticipante
from apps.encuentros.serializers import (
    CrearEncuentroSerializer,
    EncuentroSerializer,
    RecomendadosSerializer,
)
from apps.usuarios.permisos import OnboardingCompleto


class EncuentrosVista(APIView):
    permission_classes = [IsAuthenticated, OnboardingCompleto]

    def post(self, request):
        serializer = CrearEncuentroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        encuentro = servicios.crear_encuentro(request.user, serializer.validated_data)
        return Response(EncuentroSerializer(encuentro).data, status=status.HTTP_201_CREATED)


# Versión reducida (HU-006): HU-008 agrega participantes, invitaciones y lugares libres.
class EncuentroVista(APIView):
    permission_classes = [IsAuthenticated, EsParticipante]

    def get(self, request, id_encuentro):
        encuentro = servicios.obtener_encuentro(id_encuentro)
        self.check_object_permissions(request, encuentro)
        return Response(EncuentroSerializer(encuentro).data)


class RecomendadosVista(APIView):
    permission_classes = [IsAuthenticated, EsOrganizador]

    def get(self, request, id_encuentro):
        encuentro = servicios.obtener_encuentro(id_encuentro)
        self.check_object_permissions(request, encuentro)
        recomendados = servicios.recomendar_jugadores(encuentro)
        return Response(RecomendadosSerializer(recomendados).data)
