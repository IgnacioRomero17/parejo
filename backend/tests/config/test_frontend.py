import pytest

INDEX = b"<!doctype html><title>parejo</title>"


@pytest.fixture
def frontend_compilado(settings, tmp_path):
    (tmp_path / "index.html").write_bytes(INDEX)
    settings.DIR_FRONTEND_COMPILADO = tmp_path


@pytest.mark.parametrize("ruta", ["/", "/ingresar", "/encuentros/5/propuesta"])
def test_frontend_devuelve_index_en_rutas_de_la_spa(client, frontend_compilado, ruta):
    respuesta = client.get(ruta)

    assert respuesta.status_code == 200
    assert respuesta.content == INDEX
    assert respuesta["Content-Type"] == "text/html; charset=utf-8"


def test_frontend_no_deja_cachear_el_index(client, frontend_compilado):
    assert "no-cache" in client.get("/")["Cache-Control"]


@pytest.mark.parametrize("ruta", ["/api/noexiste", "/api", "/static/noexiste.js"])
def test_frontend_no_atiende_rutas_de_api_ni_estaticos(client, frontend_compilado, ruta):
    respuesta = client.get(ruta)

    assert respuesta.status_code == 404
    assert respuesta.content != INDEX


def test_frontend_no_atiende_admin_sin_barra_final(client, frontend_compilado):
    respuesta = client.get("/admin")

    assert respuesta.status_code == 301
    assert respuesta["Location"] == "/admin/"


def test_frontend_sin_compilar_responde_404(client, settings, tmp_path):
    settings.DIR_FRONTEND_COMPILADO = tmp_path

    assert client.get("/").status_code == 404


def test_frontend_rechaza_metodos_que_escriben(client, frontend_compilado):
    assert client.post("/ingresar").status_code == 405
