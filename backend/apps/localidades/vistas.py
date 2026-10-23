from rest_framework.response import Response
from rest_framework.views import APIView

from apps.localidades import servicios
from apps.localidades.serializers import LocalidadSerializer


class LocalidadesVista(APIView):
    def get(self, request):
        localidades = servicios.listar_localidades()
        return Response(LocalidadSerializer(localidades, many=True).data)
