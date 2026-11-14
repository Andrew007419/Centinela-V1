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
    "censo": "censo_3121_municipal.csv",  # rama 3121, industria de las bebidas
    "censo_tequila": "censo_312144_tequila_municipal.csv",  # clase 312144, elaboración de tequila
}
COMANDOS_ETL = {
    "denue": "python software/etl/denue_312142.py",
    "comercio": "python software/etl/comercio_2208_90.py",
    "censo": "python software/etl/censo_3121.py",
    "censo_tequila": "python software/etl/censo_3121.py",
}

AVISO_CONFIDENCIAL = "Las celdas vacías son datos confidenciales de INEGI; no son cero y no se suman a totales."
VARIABLES_CENSO = ["personal_ocupado", "produccion_bruta", "valor_agregado"]


def resumen_censo(df: pd.DataFrame) -> dict:
    """Totales del Censo sobre los municipios dados, sumando solo valores no vacíos.

    Los vacíos son datos confidenciales (no son cero). `n_con_dato` indica en cuántos municipios
    se apoya cada suma; por eso la suma de municipios NO es el total estatal.
    """
    resumen = {"municipios": len(df), "unidades_economicas": int(df["unidades_economicas"].sum())}
    for col in VARIABLES_CENSO:
        validos = df[col].dropna()
        resumen[col] = {"suma": float(validos.sum()) if len(validos) else None, "n_con_dato": int(len(validos))}
    return resumen


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
