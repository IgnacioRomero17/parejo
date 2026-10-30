from datetime import time
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.usuarios.models import DiaSemana, LadoPreferido, TipoEncuentro, Usuario
from tests.fabricas import crear_franja, crear_preferencia, crear_usuario_con_perfil

pytestmark = pytest.mark.django_db


@pytest.fixture
def cliente_admin(client):
    administrador = Usuario.objects.create_superuser(
        email="admin@example.com", password="clave1234", nombre="Admin", apellido="Parejo"
    )
    client.force_login(administrador)
    return client


def test_admin_usuario_muestra_preferencia_y_franjas_sin_contrasena(cliente_admin):
    jugador = crear_usuario_con_perfil()
    crear_preferencia(jugador)
    crear_franja(jugador)

    respuesta = cliente_admin.get(reverse("admin:usuarios_usuario_change", args=[jugador.pk]))

    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert "preferencia-TOTAL_FORMS" in contenido
    assert "disponibilidades-TOTAL_FORMS" in contenido
    assert 'name="password"' not in contenido


def test_admin_usuario_edita_perfil_y_franja(cliente_admin):
    jugador = crear_usuario_con_perfil(password="clave1234")
    preferencia = crear_preferencia(jugador)
    franja = crear_franja(jugador)
    datos = {
        "email": jugador.email,
        "nombre": jugador.nombre,
        "apellido": jugador.apellido,
        "edad": jugador.edad,
        "genero": jugador.genero,
        "frecuencia_juego": jugador.frecuencia_juego,
        "nivel_estimado": "5.5",
        "localidad": jugador.localidad_id,
        "disponible_para_invitaciones": "on",
        "is_active": "on",
        "preferencia-TOTAL_FORMS": "1",
        "preferencia-INITIAL_FORMS": "1",
        "preferencia-MIN_NUM_FORMS": "0",
        "preferencia-MAX_NUM_FORMS": "1",
        "preferencia-0-id_preferencia": preferencia.pk,
        "preferencia-0-usuario": jugador.pk,
        "preferencia-0-tipo_encuentro": TipoEncuentro.COMPETITIVO,
        "preferencia-0-lado_preferido": LadoPreferido.REVES,
        "disponibilidades-TOTAL_FORMS": "1",
        "disponibilidades-INITIAL_FORMS": "1",
        "disponibilidades-MIN_NUM_FORMS": "0",
        "disponibilidades-MAX_NUM_FORMS": "1000",
        "disponibilidades-0-id_disponibilidad": franja.pk,
        "disponibilidades-0-usuario": jugador.pk,
        "disponibilidades-0-dia_semana": DiaSemana.DOMINGO,
        "disponibilidades-0-hora_inicio": "09:00",
        "disponibilidades-0-hora_fin": "11:30",
    }

    respuesta = cliente_admin.post(
        reverse("admin:usuarios_usuario_change", args=[jugador.pk]), datos
    )

    assert respuesta.status_code == 302
    jugador.refresh_from_db()
    franja.refresh_from_db()
    preferencia.refresh_from_db()
    assert jugador.nivel_estimado == Decimal("5.5")
    assert jugador.disponible_para_invitaciones
    assert preferencia.lado_preferido == LadoPreferido.REVES
    assert franja.dia_semana == DiaSemana.DOMINGO
    assert (franja.hora_inicio, franja.hora_fin) == (time(9), time(11, 30))
    assert jugador.check_password("clave1234")


def test_admin_usuario_no_permite_alta_ni_borrado(cliente_admin):
    jugador = crear_usuario_con_perfil()

    alta = cliente_admin.get(reverse("admin:usuarios_usuario_add"))
    borrado = cliente_admin.get(reverse("admin:usuarios_usuario_delete", args=[jugador.pk]))

    assert alta.status_code == 403
    assert borrado.status_code == 403
