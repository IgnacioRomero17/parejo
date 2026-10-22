from decimal import Decimal

import pytest
from django.db import IntegrityError, connection

from apps.usuarios.models import Usuario
from tests.fabricas import crear_localidad, crear_usuario

pytestmark = pytest.mark.django_db


def test_usuario_normaliza_correo_a_minusculas():
    usuario = crear_usuario(email="  Ana.Perez@Example.COM ")

    assert usuario.email == "ana.perez@example.com"


def test_usuario_guarda_contrasena_hasheada():
    usuario = crear_usuario(password="clave1234")

    assert usuario.password != "clave1234"
    assert usuario.check_password("clave1234")


def test_usuario_superusuario_tiene_permisos_de_admin():
    usuario = Usuario.objects.create_superuser(
        email="Admin@Example.com", password="clave1234", nombre="Admin", apellido="Parejo"
    )

    assert usuario.email == "admin@example.com"
    assert usuario.is_staff
    assert usuario.is_superuser


def test_usuario_valores_por_defecto():
    usuario = crear_usuario()

    assert usuario.is_active
    assert not usuario.is_staff
    assert not usuario.disponible_para_invitaciones
    assert usuario.fecha_registro is not None


def test_usuario_perfil_incompleto_sin_nivel_o_localidad():
    localidad = crear_localidad()

    assert not crear_usuario(email="a@example.com").perfil_completo
    assert not crear_usuario(email="b@example.com", localidad=localidad).perfil_completo
    assert not crear_usuario(email="c@example.com", nivel_estimado=Decimal("3.5")).perfil_completo


def test_usuario_perfil_completo_con_nivel_y_localidad():
    usuario = crear_usuario(localidad=crear_localidad(), nivel_estimado=Decimal("3.5"))

    assert usuario.perfil_completo


def test_usuario_base_completa_valores_por_defecto():
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO usuario (email, password_hash, nombre, apellido, is_superuser, is_staff)"
            " VALUES ('sql@example.com', '', 'Ana', 'Pérez', false, false)"
            " RETURNING disponible_para_invitaciones, activo, fecha_registro"
        )
        disponible, activo, fecha_registro = cursor.fetchone()

    assert disponible is False
    assert activo is True
    assert fecha_registro is not None


@pytest.mark.parametrize("nivel", [Decimal("0.5"), Decimal("7.5"), Decimal("3.3")])
def test_usuario_base_rechaza_nivel_invalido(nivel):
    with pytest.raises(IntegrityError):
        crear_usuario(nivel_estimado=nivel)


@pytest.mark.parametrize("edad", [17, 100])
def test_usuario_base_rechaza_edad_fuera_de_rango(edad):
    with pytest.raises(IntegrityError):
        crear_usuario(edad=edad)


def test_usuario_base_rechaza_genero_desconocido():
    with pytest.raises(IntegrityError):
        crear_usuario(genero="OTRO")


def test_usuario_base_rechaza_correo_con_mayusculas():
    with pytest.raises(IntegrityError):
        Usuario.objects.create(email="Ana@example.com", nombre="Ana", apellido="Pérez")


def test_usuario_base_rechaza_correo_repetido():
    crear_usuario(email="ana@example.com")

    with pytest.raises(IntegrityError):
        crear_usuario(email="ANA@example.com")
