"""Modelo de oferta madura por cohortes y cálculo del IPO.

El modelo es deliberadamente simple y auditable:
- La serie de inventario se construye en `serie_inventario.py`.
- Cada aumento anual de inventario se interpreta como una cohorte sembrada.
- Cada cohorte madura a los 6, 7 y 8 años con pesos declarados.
- La oferta se convierte a toneladas con una banda de factor.
- La demanda se toma de `demanda.py`.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from ipo.src.demanda import (
    ANIO_BASE_DEMANDA,
    BASE_DEMANDA_T,
    cargar_comercio,
    demanda_anual,
    tendencia_exportaciones,
)
from ipo.src.escenarios import ESCENARIOS, obtener_escenario

REPO = Path(__file__).resolve().parents[2]
INVENTARIO = REPO / "data" / "processed" / "inventario_agave.csv"
COMERCIO = REPO / "data" / "processed" / "comercio_2208_90.csv"

VENTANA = (6, 7, 8)
PESOS_BASE = (0.25, 0.50, 0.25)
FACTOR_BANDA = {
    "min": 0.020,
    "base": 0.032,
    "max": 0.055,
    "unidad": "t/planta",
}

SUPUESTOS = [
    "La serie de inventario 2017-2026 es interpolada linealmente; los años intermedios no son observados.",
    "Cada aumento anual de inventario se interpreta como una cohorte sembrada; es una aproximación, no siembra bruta.",
    "La siembra futura se mantiene en el último valor observado (2026) solo para las cohortes que alcanzan a madurar dentro del horizonte.",
    "La ventana de maduración es 6-8 años, con pesos declarados por escenario.",
    "El factor plantas→toneladas es una banda calibrada con literatura, no una medición.",
    "La demanda base es 2.18 millones de t en 2025; los escenarios aplican crecimiento explícito.",
    "Las exportaciones 220890 se usan como tendencia, no como conversión directa a toneladas de agave.",
    "El IPO es un índice de presión relativa; no es una predicción de precio.",
]

FUENTES = [
    "DENUE 2026-05, INEGI, SCIAN 312144 (Elaboración de tequila).",
    "UN Comtrade, HS 220890, reporter México, exportaciones 2020-2025.",
    "SIAP, monografía del agave tequilero 2023 (ventana 6-8 años).",
    "Ficha de problemática Agave Altos Sur/Valles (CRT, CNIT, SADER).",
]


def cargar_inventario(path: Path | None = None) -> list[dict]:
    """Carga la serie anual generada por `serie_inventario.py`."""
    path = path or INVENTARIO
    if not path.exists():
        raise FileNotFoundError(f"No existe la serie de inventario: {path}")
    filas = []
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            filas.append(
                {
                    "anio": int(row["anio"]),
                    "plantas": int(row["plantas"]),
                    "hectareas": int(row["hectareas"]) if row.get("hectareas") else None,
                    "fuente": row.get("fuente", ""),
                    "definicion": row.get("definicion", ""),
                }
            )
    if len(filas) < 2:
        raise ValueError("La serie de inventario necesita al menos dos años")
    if any(b["anio"] <= a["anio"] for a, b in zip(filas, filas[1:])):
        raise ValueError("La serie de inventario debe estar ordenada y sin duplicados")
    return filas


def construir_cohortes(filas: Iterable[dict]) -> list[dict]:
    """Convierte incrementos anuales de inventario en cohortes.

    La primera fila es el stock inicial, no una cohorte. Cada fila siguiente
    aporta la diferencia contra el año anterior.
    """
    filas = list(filas)
    cohortes = []
    for anterior, actual in zip(filas, filas[1:]):
        plantas = actual["plantas"] - anterior["plantas"]
        if plantas < 0:
            raise ValueError(f"Inventario negativo entre {anterior['anio']} y {actual['anio']}")
        cohortes.append(
            {
                "anio_siembra": actual["anio"],
                "plantas": plantas,
                "tipo": "derivado",
                "origen": "ancla" if "ancla" in actual["definicion"] else "interpolado",
                "fuente": actual["fuente"],
            }
        )
    return cohortes


def proyectar_cohortes(cohortes: list[dict], anio_fin: int) -> list[dict]:
    """Completa cohortes futuras con el último valor observado.

    Solo se proyectan los años que aún pueden madurar dentro del horizonte:
    hasta `anio_fin - min(VENTANA)`.
    """
    if not cohortes:
        raise ValueError("No hay cohortes para proyectar")
    ultimo = cohortes[-1]
    ultimo_anio = ultimo["anio_siembra"]
    limite = anio_fin - min(VENTANA)
    proyectadas = list(cohortes)
    for anio in range(ultimo_anio + 1, limite + 1):
        proyectadas.append(
            {
                "anio_siembra": anio,
                "plantas": ultimo["plantas"],
                "tipo": "proyectado",
                "fuente": "Supuesto: se mantiene la siembra neta de 2026",
            }
        )
    return proyectadas


def oferta_madura_por_anio(
    cohortes: list[dict],
    anio_inicio: int,
    anio_fin: int,
    pesos: tuple[float, float, float] = PESOS_BASE,
) -> list[dict]:
    """Calcula plantas maduras por año según la ventana 6-8."""
    if len(pesos) != len(VENTANA):
        raise ValueError("Debe haber un peso por cada año de la ventana")
    if abs(sum(pesos) - 1.0) > 1e-9:
        raise ValueError("Los pesos de la ventana deben sumar 1")
    if anio_inicio > anio_fin:
        raise ValueError("anio_inicio no puede ser mayor que anio_fin")

    por_anio = {c["anio_siembra"]: c["plantas"] for c in cohortes}
    filas = []
    for anio in range(anio_inicio, anio_fin + 1):
        total = 0.0
        detalle = []
        for offset, peso in zip(VENTANA, pesos):
            anio_siembra = anio - offset
            plantas = por_anio.get(anio_siembra, 0)
            aporte = plantas * peso
            total += aporte
            if plantas:
                detalle.append(
                    {
                        "anio_siembra": anio_siembra,
                        "plantas_cohorte": plantas,
                        "peso": peso,
                        "aporte_plantas": round(aporte),
                    }
                )
        filas.append(
            {
                "anio": anio,
                "oferta_madura_plantas": round(total),
                "cohortes": detalle,
            }
        )
    return filas


def verificar_cohortes(cohortes: list[dict], filas_inventario: list[dict]) -> None:
    """Verifica que las cohortes observadas expliquen el cambio de inventario."""
    observadas = sum(c["plantas"] for c in cohortes if c["tipo"] != "proyectado")
    esperado = filas_inventario[-1]["plantas"] - filas_inventario[0]["plantas"]
    if observadas != esperado:
        raise ValueError(
            f"Las cohortes suman {observadas:,} y el cambio de inventario es {esperado:,}"
        )


def _toneladas(plantas: float, factor: float) -> float:
    return round(plantas * factor, 2)


def calcular_ipo(
    escenario: str = "base",
    anio_inicio: int = 2026,
    anio_fin: int = 2034,
    inventario_path: Path | None = None,
    comercio_path: Path | None = None,
) -> dict:
    """Devuelve la serie de oferta, demanda e IPO para un escenario."""
    config = obtener_escenario(escenario)
    if anio_inicio < 2026 or anio_fin > 2040:
        raise ValueError("El horizonte debe estar entre 2026 y 2040")
    if anio_inicio > anio_fin:
        raise ValueError("anio_inicio no puede ser mayor que anio_fin")

    filas_inv = cargar_inventario(inventario_path)
    cohortes = construir_cohortes(filas_inv)
    verificar_cohortes(cohortes, filas_inv)
    cohortes = proyectar_cohortes(cohortes, anio_fin)

    oferta = oferta_madura_por_anio(
        cohortes, anio_inicio, anio_fin, pesos=config["pesos_ventana"]
    )
    demanda = demanda_anual(anio_inicio, anio_fin, escenario)

    comercio = cargar_comercio(comercio_path or COMERCIO)
    tendencia = tendencia_exportaciones(comercio)

    serie = []
    for fila in oferta:
        anio = fila["anio"]
        plantas = fila["oferta_madura_plantas"]
        t_base = _toneladas(plantas, FACTOR_BANDA["base"])
        t_min = _toneladas(plantas, FACTOR_BANDA["min"])
        t_max = _toneladas(plantas, FACTOR_BANDA["max"])
        dem = demanda[anio]
        serie.append(
            {
                "anio": anio,
                "oferta_madura_plantas": plantas,
                "oferta_madura_t": t_base,
                "oferta_madura_t_min": t_min,
                "oferta_madura_t_max": t_max,
                "demanda_t": round(dem, 2),
                "ipo": round(t_base / dem, 3) if dem else None,
                "ipo_min": round(t_min / dem, 3) if dem else None,
                "ipo_max": round(t_max / dem, 3) if dem else None,
                "cohortes": fila["cohortes"],
            }
        )

    return {
        "escenario": escenario,
        "descripcion_escenario": config["descripcion"],
        "factor_plantas_a_toneladas": FACTOR_BANDA,
        "ventana_maduracion_anios": list(VENTANA),
        "pesos_ventana": list(config["pesos_ventana"]),
        "anio_inicio": anio_inicio,
        "anio_fin": anio_fin,
        "serie": serie,
        "tendencia_exportaciones": tendencia,
        "supuestos": SUPUESTOS
        + [
            f"Escenario {escenario}: crecimiento de demanda {config['crecimiento_demanda']:.1%} anual.",
            f"Pesos de ventana del escenario: {config['pesos_ventana']}.",
            f"Demanda base {BASE_DEMANDA_T:,} t en {ANIO_BASE_DEMANDA}.",
        ],
        "fuentes": FUENTES,
    }
