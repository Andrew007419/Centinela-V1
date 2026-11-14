"""Pruebas del endpoint FastAPI."""

from fastapi.testclient import TestClient

from ipo.src.api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ipo_base():
    r = client.get("/ipo", params={"escenario": "base", "anio_inicio": 2026, "anio_fin": 2034})
    assert r.status_code == 200
    data = r.json()
    assert data["escenario"] == "base"
    assert len(data["serie"]) == 9
    assert data["factor_plantas_a_toneladas"]["min"] < data["factor_plantas_a_toneladas"]["max"]
    for fila in data["serie"]:
        assert fila["ipo_min"] <= fila["ipo"] <= fila["ipo_max"]
        assert fila["demanda_t"] > 0


def test_ipo_escenario_invalido():
    r = client.get("/ipo", params={"escenario": "otro"})
    assert r.status_code == 400
    assert "Escenario inválido" in r.json()["detail"]


def test_ipo_anio_invalido():
    r = client.get("/ipo", params={"anio_inicio": 2025})
    assert r.status_code == 422
