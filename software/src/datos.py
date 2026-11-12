"""Carga de los CSV de data/processed/. Si no existen devuelve None (el panel avisa, no se rompe)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DIR_PROCESSED = RAIZ / "data" / "processed"

ARCHIVOS = {
    "denue": "denue_312142_jalisco.csv",
    "comercio": "comercio_2208_90.csv",
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
