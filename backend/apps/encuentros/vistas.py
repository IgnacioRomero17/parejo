from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.encuentros import servicios
from apps.encuentros.permisos import EsInvitado, EsOrganizador, EsParticipante
from apps.encuentros.serializers import (
    BandejaSerializer,
    CrearEncuentroSerializer,
    DetalleEncuentroSerializer,
    EncuentroSerializer,
    InvitacionEnviadaSerializer,
    InvitacionRecibidaSerializer,
    InvitarSerializer,
    PropuestaSerializer,
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


class EncuentroVista(APIView):
    permission_classes = [IsAuthenticated, EsParticipante]

    def get(self, request, id_encuentro):
        encuentro = servicios.obtener_encuentro(id_encuentro)
        self.check_object_permissions(request, encuentro)
        detalle = servicios.detalle_encuentro(encuentro, request.user)
        return Response(DetalleEncuentroSerializer(detalle).data)


class RecomendadosVista(APIView):
    permission_classes = [IsAuthenticated, EsOrganizador]

    def get(self, request, id_encuentro):
        encuentro = servicios.obtener_encuentro(id_encuentro)
        self.check_object_permissions(request, encuentro)
        recomendados = servicios.recomendar_jugadores(encuentro)
        return Response(RecomendadosSerializer(recomendados).data)


class InvitacionesEncuentroVista(APIView):
    permission_classes = [IsAuthenticated, EsOrganizador]

    def post(self, request, id_encuentro):
        encuentro = servicios.obtener_encuentro(id_encuentro)
        self.check_object_permissions(request, encuentro)
        serializer = InvitarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitaciones = servicios.invitar_jugadores(encuentro, serializer.validated_data["usuarios"])
        return Response(
            InvitacionEnviadaSerializer(invitaciones, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class FormarParejasVista(APIView):
    permission_classes = [IsAuthenticated, EsOrganizador]

    def post(self, request, id_encuentro):
        encuentro = servicios.obtener_encuentro(id_encuentro)
        self.check_object_permissions(request, encuentro)
        propuesta = servicios.formar_parejas(encuentro)
        return Response(PropuestaSerializer(propuesta).data, status=status.HTTP_201_CREATED)


class PropuestaVista(APIView):
    permission_classes = [IsAuthenticated, EsParticipante]

    def get(self, request, id_encuentro):
        encuentro = servicios.obtener_encuentro(id_encuentro)
        self.check_object_permissions(request, encuentro)
        propuesta = servicios.obtener_propuesta(encuentro)
        return Response(PropuestaSerializer(propuesta).data)


class InvitacionesVista(APIView):
    permission_classes = [IsAuthenticated, OnboardingCompleto]

    def get(self, request):
        bandeja = servicios.bandeja_invitaciones(request.user)
        return Response(BandejaSerializer(bandeja).data)


class AceptarInvitacionVista(APIView):
    permission_classes = [IsAuthenticated, EsInvitado]

    def post(self, request, id_invitacion):
        invitacion = servicios.obtener_invitacion(id_invitacion)
        self.check_object_permissions(request, invitacion)
        invitacion = servicios.aceptar_invitacion(invitacion)
        return Response(InvitacionRecibidaSerializer(invitacion).data)


class RechazarInvitacionVista(APIView):
    permission_classes = [IsAuthenticated, EsInvitado]

    def post(self, request, id_invitacion):
        invitacion = servicios.obtener_invitacion(id_invitacion)
        self.check_object_permissions(request, invitacion)
        invitacion = servicios.rechazar_invitacion(invitacion)
        return Response(InvitacionRecibidaSerializer(invitacion).data)
