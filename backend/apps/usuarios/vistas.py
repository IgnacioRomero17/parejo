from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.usuarios import servicios
from apps.usuarios.serializers import (
    ActualizarPerfilSerializer,
    ConfirmarRecuperacionSerializer,
    CuentaRecuperacionSerializer,
    IngresoSerializer,
    PerfilSerializer,
    RecuperacionSerializer,
    RegistroSerializer,
    UsuarioActualSerializer,
)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfVista(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


# DRF solo exige CSRF a usuarios con sesión; el registro lo exige también sin sesión.
@method_decorator(csrf_protect, name="dispatch")
class RegistroVista(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = servicios.registrar_usuario(**serializer.validated_data)
        login(request, usuario)
        return Response(UsuarioActualSerializer(usuario).data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_protect, name="dispatch")
class IngresoVista(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = IngresoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = servicios.autenticar_usuario(**serializer.validated_data)
        login(request, usuario)
        return Response(UsuarioActualSerializer(usuario).data)


class SalirVista(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsuarioActualVista(APIView):
    def get(self, request):
        return Response(UsuarioActualSerializer(request.user).data)


@method_decorator(csrf_protect, name="dispatch")
class RecuperacionVista(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RecuperacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicios.solicitar_recuperacion(**serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnlaceRecuperacionVista(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uid, token):
        usuario = servicios.usuario_por_enlace(uid, token)
        return Response(CuentaRecuperacionSerializer(usuario).data)


@method_decorator(csrf_protect, name="dispatch")
class ConfirmarRecuperacionVista(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConfirmarRecuperacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = servicios.restablecer_contrasena(**serializer.validated_data)
        login(request, usuario)
        return Response(UsuarioActualSerializer(usuario).data)


class PerfilVista(APIView):
    def get(self, request):
        return Response(PerfilSerializer(request.user).data)

    def patch(self, request):
        serializer = ActualizarPerfilSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = servicios.actualizar_perfil(request.user, **serializer.validated_data)
        return Response(PerfilSerializer(usuario).data)
