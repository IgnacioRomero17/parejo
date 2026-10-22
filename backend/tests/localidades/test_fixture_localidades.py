import pytest
from django.core.management import call_command

from apps.localidades.models import Localidad

pytestmark = pytest.mark.django_db


def test_localidades_fixture_carga_catalogo_completo():
    call_command("loaddata", "localidades", verbosity=0)

    assert Localidad.objects.count() == 16
    assert Localidad.objects.filter(nombre="Córdoba – Argüello").exists()
