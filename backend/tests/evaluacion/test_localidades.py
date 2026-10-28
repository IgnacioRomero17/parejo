"""La copia del catálogo de la evaluación coincide con el fixture de la app."""

import json
from pathlib import Path

from evaluacion.localidades import LOCALIDADES

FIXTURE = Path(__file__).resolve().parents[2] / "apps/localidades/fixtures/localidades.json"


def test_localidades_la_copia_coincide_con_el_fixture():
    registros = json.loads(FIXTURE.read_text(encoding="utf-8"))
    del_fixture = [
        (
            registro["pk"],
            registro["fields"]["nombre"],
            float(registro["fields"]["latitud"]),
            float(registro["fields"]["longitud"]),
        )
        for registro in registros
    ]

    assert [(loc.id, loc.nombre, loc.lat, loc.lon) for loc in LOCALIDADES] == del_fixture
