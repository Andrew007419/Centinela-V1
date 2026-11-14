"""Pruebas del modelo de cohortes, oferta e IPO."""

import pytest

from ipo.src.modelo import (
    FACTOR_BANDA,
    INVENTARIO,
    calcular_ipo,
    cargar_inventario,
    construir_cohortes,
    oferta_madura_por_anio,
    proyectar_cohortes,
    verificar_cohortes,
)


@pytest.fixture()
def inventario():
    return cargar_inventario(INVENTARIO)


@pytest.fixture()
def cohortes(inventario):
    return construir_cohortes(inventario)


def test_inventario_tiene_diez_anios(inventario):
    assert len(inventario) == 10
    assert inventario[0]["anio"] == 2017
    assert inventario[-1]["anio"] == 2026


def test_cohortes_cuadran_con_inventario(inventario, cohortes):
    verificar_cohortes(cohortes, inventario)
    assert sum(c["plantas"] for c in cohortes) == 1_675_000_000


def test_cohortes_marcadas_como_derivadas(cohortes):
    assert all(c["tipo"] == "derivado" for c in cohortes)
    assert all(c["origen"] in {"ancla", "interpolado"} for c in cohortes)


def test_oferta_2026_y_2031(inventario, cohortes):
    filas = oferta_madura_por_anio(cohortes, 2026, 2034)
    por_anio = {f["anio"]: f for f in filas}
    # 2026 recibe 2018 (8), 2019 (7) y 2020 (6): 69.2M
    assert por_anio[2026]["oferta_madura_plantas"] == 69_200_000
    # 2031 recibe 2023 (8), 2024 (7) y 2025 (6): 332.25M
    assert por_anio[2031]["oferta_madura_plantas"] == 332_250_000


def test_oferta_proyectada_2034(inventario, cohortes):
    proyectadas = proyectar_cohortes(cohortes, 2034)
    filas = oferta_madura_por_anio(proyectadas, 2026, 2034)
    por_anio = {f["anio"]: f for f in filas}
    # 2034 recibe 2026 (8), 2027 (7, proyectada) y 2028 (6, proyectada)
    assert por_anio[2034]["oferta_madura_plantas"] == 332_250_000
    assert any(c["tipo"] == "proyectado" for c in proyectadas)


def test_factor_banda_coherente():
    assert FACTOR_BANDA["min"] < FACTOR_BANDA["base"] < FACTOR_BANDA["max"]


def test_ipo_tiene_banda_y_serie():
    data = calcular_ipo("base", 2026, 2034)
    assert len(data["serie"]) == 9
    for fila in data["serie"]:
        assert fila["ipo_min"] <= fila["ipo"] <= fila["ipo_max"]
        assert fila["demanda_t"] > 0
        assert fila["oferta_madura_plantas"] >= 0


def test_escenarios_cambian_el_ipo():
    base = calcular_ipo("base", 2026, 2034)
    opt = calcular_ipo("optimista", 2026, 2034)
    pes = calcular_ipo("pesimista", 2026, 2034)
    # Más demanda (optimista) baja el IPO; menos demanda (pesimista) lo sube.
    assert opt["serie"][0]["ipo"] < base["serie"][0]["ipo"] < pes["serie"][0]["ipo"]


def test_escenario_invalido():
    with pytest.raises(ValueError):
        calcular_ipo("inventado", 2026, 2034)
