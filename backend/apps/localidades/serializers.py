from rest_framework import serializers


class LocalidadSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="id_localidad")
    nombre = serializers.CharField()
