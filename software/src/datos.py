"""Carga de los CSV de data/processed/. Si no existen devuelve None (el panel avisa, no se rompe)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DIR_PROCESSED = RAIZ / "data" / "processed"

ARCHIVOS = {
    "denue": "denue_312142_jalisco.csv",
    "comercio": "comercio_tequila_banxico.csv",  # serie principal: Banxico, mensual, nacional, solo tequila
    "comtrade": "comercio_2208_90.csv",  # opcional, del Integrante 2: UN Comtrade, HS 220890 (todos los destilados)
    "censo": "censo_3121_municipal.csv",
}
COMANDOS_ETL = {
    "denue": "python software/etl/denue_312142.py",
    "comercio": "python software/etl/comercio_2208_90.py",
    "censo": "python software/etl/censo_3121.py",
}


def cargar(nombre: str) -> pd.DataFrame | None:
    ruta = DIR_PROCESSED / ARCHIVOS[nombre]
    if not ruta.exists():
        return None
    try:
        return pd.read_csv(ruta, dtype={"clave_mun": str}, encoding="utf-8")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        return None


def mensaje_faltante(nombre: str) -> str:
    return (
        f"Falta `data/processed/{ARCHIVOS[nombre]}` (o está vacío). "
        f"Descarga el original a `data/raw/` y corre `{COMANDOS_ETL[nombre]}`."
    )


def exportaciones_comtrade_anual(df: pd.DataFrame) -> pd.DataFrame | None:
    """Total anual (anio, valor_usd) del CSV de UN Comtrade; None si le faltan columnas.

    Si trae `es_total`, solo se usan las filas es_total == 1 (el total Mundo): las demás son destinos
    y sumarlas junto con el total duplicaría el valor.
    """
    if "valor_usd" not in df.columns or not ({"anio", "periodo"} & set(df.columns)):
        return None
    if "es_total" in df.columns:
        df = df[pd.to_numeric(df["es_total"], errors="coerce") == 1]
    if "anio" not in df.columns:
        df = df.assign(anio=df["periodo"].astype(str).str[:4])
    return df.groupby("anio", as_index=False)["valor_usd"].sum()
