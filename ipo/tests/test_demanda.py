"""Pruebas de demanda y tendencia de exportaciones."""

import pytest

from ipo.src.demanda import (
    BASE_DEMANDA_T,
    cargar_comercio,
    demanda_anual,
    tendencia_exportaciones,
)
from ipo.src.modelo import COMERCIO


@pytest.fixture()
def comercio():
    return cargar_comercio(COMERCIO)


def test_comercio_tiene_seis_anios(comercio):
    assert [f["anio"] for f in comercio] == [2020, 2021, 2022, 2023, 2024, 2025]
    assert all(f["valor_usd"] > 0 for f in comercio)


def test_comercio_2024(comercio):
    fila = next(f for f in comercio if f["anio"] == 2024)
    assert fila["valor_usd"] == pytest.approx(4_123_214_628, rel=1e-6)
    assert fila["volumen_kg"] == pytest.approx(518_888_582, rel=1e-6)


def test_tendencia_exportaciones(comercio):
    tendencia = tendencia_exportaciones(comercio)
    assert tendencia["anio_inicial"] == 2020
    assert tendencia["anio_final"] == 2025
    assert tendencia["cagr"] is not None
    assert tendencia["cambio_ultimo"] < 0  # 2025 cayó frente a 2024


def test_demanda_base_constante():
    serie = demanda_anual(2026, 2034, "base")
    assert all(valor == pytest.approx(BASE_DEMANDA_T) for valor in serie.values())


def test_optimista_mayor_demanda_que_pesimista():
    opt = demanda_anual(2026, 2034, "optimista")
    base = demanda_anual(2026, 2034, "base")
    pes = demanda_anual(2026, 2034, "pesimista")
    assert opt[2034] > base[2034] > pes[2034]


def test_horizonte_invalido():
    with pytest.raises(ValueError):
        demanda_anual(2025, 2034, "base")
    with pytest.raises(ValueError):
        demanda_anual(2034, 2026, "base")
