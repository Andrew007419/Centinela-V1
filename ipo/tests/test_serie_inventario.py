"""Pruebas de la serie anual de inventario."""

from pathlib import Path

import pytest

from ipo.src.serie_inventario import ANCLAS, COLUMNAS, generar_serie, guardar_csv


@pytest.fixture()
def serie():
    return generar_serie()


def test_tiene_una_fila_por_anio(serie):
    assert [f["anio"] for f in serie] == list(range(2017, 2027))


def test_anclas_exactas(serie):
    por_anio = {f["anio"]: f for f in serie}
    assert por_anio[2017]["plantas"] == 29_000_000
    assert por_anio[2022]["plantas"] == 375_000_000
    assert por_anio[2026]["plantas"] == 1_704_000_000


def test_interpolacion_lineal(serie):
    por_anio = {f["anio"]: f for f in serie}
    # 2018: 29M + (375M-29M)/5 = 98.2M
    assert por_anio[2018]["plantas"] == 98_200_000
    # 2023: 375M + (1704M-375M)/4 = 707.25M
    assert por_anio[2023]["plantas"] == 707_250_000
    # 2024: 1039.5M
    assert por_anio[2024]["plantas"] == 1_039_500_000
    # 2025: 1371.75M
    assert por_anio[2025]["plantas"] == 1_371_750_000


def test_anios_intermedios_marcados(serie):
    for fila in serie:
        if fila["anio"] in (2018, 2019, 2020, 2021, 2023, 2024, 2025):
            assert fila["definicion"] == "interpolado"
        else:
            assert "ancla" in fila["definicion"]


def test_hectareas_solo_en_ancla_2026(serie):
    por_anio = {f["anio"]: f for f in serie}
    assert por_anio[2026]["hectareas"] == 511_492
    assert all(por_anio[a]["hectareas"] is None for a in range(2017, 2026))


def test_siembra_neta_es_derivada_y_positiva(serie):
    assert serie[0]["siembra_neta_plantas"] is None
    assert all(f["siembra_neta_plantas"] > 0 for f in serie[1:])


def test_columnas_del_csv(serie, tmp_path):
    destino = tmp_path / "inventario.csv"
    guardar_csv(serie, destino)
    lineas = destino.read_text(encoding="utf-8").splitlines()
    assert lineas[0].split(",") == COLUMNAS
    assert len(lineas) == 11


def test_anclas_en_orden(ANCLAS=ANCLAS):
    anios = [a["anio"] for a in ANCLAS]
    assert anios == sorted(anios)
    assert len(anios) == len(set(anios))


def test_csv_no_contiene_nulos_como_texto(serie, tmp_path):
    destino = tmp_path / "inventario.csv"
    guardar_csv(serie, destino)
    texto = destino.read_text(encoding="utf-8")
    assert "None" not in texto
    assert "nan" not in texto.lower()
