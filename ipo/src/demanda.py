"""Demanda absorbible y tendencia de exportaciones.

La demanda base es el consumo industrial de agave de 2025 (2.18 millones de t).
Los escenarios aplican un crecimiento anual explícito. Las exportaciones de
tequila se usan como contexto/tendencia, no como conversión directa a toneladas.
"""

from __future__ import annotations

import csv
from pathlib import Path

from ipo.src.escenarios import obtener_escenario

ANIO_BASE_DEMANDA = 2025
BASE_DEMANDA_T = 2_180_000.0
ANIO_MIN = 2026
ANIO_MAX = 2040


def cargar_comercio(path: Path) -> list[dict]:
    """Carga la serie anual de comercio (fila Mundo, es_total=1)."""
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo de comercio: {path}")
    filas = []
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if str(row.get("es_total", "")).strip() != "1":
                continue
            try:
                anio = int(row["anio"])
                valor = float(row["valor_usd"])
                volumen = float(row["volumen"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Fila de comercio inválida: {row}") from exc
            filas.append(
                {
                    "anio": anio,
                    "valor_usd": valor,
                    "volumen_kg": volumen,
                    "unidad": row.get("unidad", "kg"),
                    "fuente": row.get("fuente", ""),
                }
            )
    if not filas:
        raise ValueError("El archivo de comercio no contiene filas de total mundial")
    filas.sort(key=lambda f: f["anio"])
    return filas


def tendencia_exportaciones(filas: list[dict]) -> dict:
    """Calcula CAGR y cambio del último año; es contexto, no demanda."""
    if len(filas) < 2:
        return {
            "anio_inicial": filas[0]["anio"] if filas else None,
            "anio_final": filas[-1]["anio"] if filas else None,
            "cagr": None,
            "cambio_ultimo": None,
            "nota": "Insuficientes años para calcular tendencia",
        }
    primero, ultimo = filas[0], filas[-1]
    anios = ultimo["anio"] - primero["anio"]
    cagr = (ultimo["valor_usd"] / primero["valor_usd"]) ** (1 / anios) - 1
    previo = filas[-2]
    cambio_ultimo = ultimo["valor_usd"] / previo["valor_usd"] - 1
    return {
        "anio_inicial": primero["anio"],
        "anio_final": ultimo["anio"],
        "valor_inicial_usd": round(primero["valor_usd"], 2),
        "valor_final_usd": round(ultimo["valor_usd"], 2),
        "cagr": round(cagr, 4),
        "cambio_ultimo": round(cambio_ultimo, 4),
        "nota": "Tendencia de exportaciones HS 220890; no se usa como conversión a toneladas de agave.",
    }


def demanda_anual(anio_inicio: int, anio_fin: int, escenario: str = "base") -> dict[int, float]:
    """Serie anual de demanda en toneladas para un escenario."""
    if anio_inicio < ANIO_MIN or anio_fin > ANIO_MAX:
        raise ValueError(f"El horizonte de demanda debe estar entre {ANIO_MIN} y {ANIO_MAX}")
    if anio_inicio > anio_fin:
        raise ValueError("anio_inicio no puede ser mayor que anio_fin")
    config = obtener_escenario(escenario)
    tasa = config["crecimiento_demanda"]
    serie = {}
    for anio in range(anio_inicio, anio_fin + 1):
        serie[anio] = BASE_DEMANDA_T * ((1 + tasa) ** (anio - ANIO_BASE_DEMANDA))
    return serie
