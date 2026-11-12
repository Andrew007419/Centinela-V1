"""Utilidades comunes del ETL: normalización de texto, clave de municipio y lectura de originales."""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

for _f in (sys.stdout, sys.stderr):
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"

CLAVE_JALISCO = "14"  # clave INEGI de la entidad


class ArchivoFaltante(Exception):
    """El archivo original no está en data/raw/."""


class ColumnaFaltante(Exception):
    """El archivo original no trae una columna necesaria."""


def normalizar_texto(valor) -> str:
    """Minúsculas, sin acentos y con espacios colapsados. Vacío si es nulo."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().lower()


def normalizar_municipio(valor) -> str:
    return normalizar_texto(valor)


def construir_clave_mun(cve_ent, cve_mun) -> str:
    """Clave de 5 dígitos: entidad (2) + municipio (3). Ej.: Jalisco=14, Tequila=094 -> '14094'.

    Devuelve '' si alguna parte no es numérica.
    """
    try:
        ent = f"{int(float(cve_ent)):02d}"
        mun = f"{int(float(cve_mun)):03d}"
    except (TypeError, ValueError):
        return ""
    return ent + mun


def clave_desde_completa(valor) -> str:
    """Normaliza una clave que ya viene completa (p. ej. 14094 o 14094.0) a 5 dígitos."""
    try:
        return f"{int(float(valor)):05d}"
    except (TypeError, ValueError):
        return ""


def buscar_original(prefijos: list[str], descarga: str) -> Path:
    """Busca en data/raw/ un .csv cuyo nombre empiece con algún prefijo. Falla con instrucciones si no hay."""
    if DIR_RAW.exists():
        for ruta in sorted(DIR_RAW.iterdir()):
            nombre = ruta.name.lower()
            if ruta.is_file() and nombre.endswith(".csv") and any(nombre.startswith(p) for p in prefijos):
                return ruta
    raise ArchivoFaltante(
        f"No encontré el archivo original en {DIR_RAW}.\n"
        f"Esperado: un .csv cuyo nombre empiece con {' o '.join(prefijos)}\n"
        f"Qué descargar y de dónde:\n{descarga}\n"
        "Los originales no se suben a Git (viven en Drive, ver docs/ENLACES.md)."
    )


def leer_csv(ruta: Path) -> pd.DataFrame:
    """Lee un CSV probando codificaciones comunes de INEGI/DataMéxico. Todo como texto."""
    ultimo = None
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(ruta, dtype=str, encoding=enc, sep=None, engine="python")
        except UnicodeDecodeError as e:
            ultimo = e
    raise ultimo  # pragma: no cover


def _clave_col(nombre: str) -> str:
    return re.sub(r"[^a-z0-9]", "", normalizar_texto(nombre))


def columna(df: pd.DataFrame, alias: list[str], obligatoria: bool = True, que: str = "") -> str | None:
    """Devuelve el nombre real de la primera columna que coincida con algún alias."""
    por_clave = {_clave_col(c): c for c in df.columns}
    for a in alias:
        if _clave_col(a) in por_clave:
            return por_clave[_clave_col(a)]
    if obligatoria:
        raise ColumnaFaltante(
            f"No encontré la columna de {que or alias[0]}. Alias buscados: {alias}.\n"
            f"Columnas del archivo: {list(df.columns)}"
        )
    return None


def a_numero(serie: pd.Series) -> pd.Series:
    """Convierte texto a número quitando comas de miles, $ y espacios."""
    limpio = serie.astype(str).str.replace(r"[,$\s]", "", regex=True)
    return pd.to_numeric(limpio, errors="coerce")


def escribir(df: pd.DataFrame, nombre: str) -> Path:
    DIR_PROCESSED.mkdir(parents=True, exist_ok=True)
    destino = DIR_PROCESSED / nombre
    df.to_csv(destino, index=False, encoding="utf-8")
    print(f"OK: {len(df)} filas -> {destino}")
    return destino


def ejecutar(func) -> None:
    """Corre un ETL mostrando errores claros (sin traceback) para fallas esperadas."""
    try:
        func()
    except (ArchivoFaltante, ColumnaFaltante) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
