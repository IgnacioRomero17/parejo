import ast
from pathlib import Path

import pytest

import motor

ARCHIVOS_MOTOR = sorted(Path(motor.__file__).parent.glob("*.py"))
PROHIBIDOS = ("django", "rest_framework", "apps")


def _modulos_importados(archivo: Path) -> set[str]:
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module)
    return modulos


@pytest.mark.parametrize("archivo", ARCHIVOS_MOTOR, ids=lambda archivo: archivo.name)
def test_motor_no_importa_django_ni_las_apps(archivo):
    raices = {modulo.split(".")[0] for modulo in _modulos_importados(archivo)}

    assert not raices & set(PROHIBIDOS)
