"""Cliente del endpoint /ipo (contrato en docs/03_CONTRATOS_ENTRE_ROLES.md).

Si la API no responde o devuelve algo inválido, usa ejemplo_ipo.json y lo marca con es_ejemplo=True.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import requests

URL_IPO = "http://127.0.0.1:8000/ipo"
RUTA_EJEMPLO = Path(__file__).with_name("ejemplo_ipo.json")
CLAVES_CONTRATO = {"escenario", "factor_plantas_a_toneladas", "ventana_maduracion_anios", "serie", "supuestos", "fuentes"}
CAMPOS_SERIE = {"anio", "oferta_madura_plantas", "oferta_madura_t", "demanda_t", "ipo", "ipo_min", "ipo_max"}


@dataclass
class RespuestaIPO:
    datos: dict
    es_ejemplo: bool
    motivo: str = ""  # por qué se usó el ejemplo


def _valida(datos: dict) -> None:
    faltan = CLAVES_CONTRATO - set(datos)
    if faltan:
        raise ValueError(f"faltan claves del contrato: {sorted(faltan)}")
    for fila in datos["serie"]:
        if CAMPOS_SERIE - set(fila):
            raise ValueError(f"fila de serie incompleta: {sorted(CAMPOS_SERIE - set(fila))}")


def cargar_ejemplo() -> dict:
    return json.loads(RUTA_EJEMPLO.read_text(encoding="utf-8"))


def obtener_ipo(escenario: str, anio_inicio: int = 2026, anio_fin: int = 2034, timeout: float = 3.0) -> RespuestaIPO:
    try:
        r = requests.get(
            URL_IPO,
            params={"escenario": escenario, "anio_inicio": anio_inicio, "anio_fin": anio_fin},
            timeout=timeout,
        )
        r.raise_for_status()
        datos = r.json()
        _valida(datos)
        return RespuestaIPO(datos, es_ejemplo=False)
    except (requests.RequestException, ValueError) as e:
        return RespuestaIPO(cargar_ejemplo(), es_ejemplo=True, motivo=f"{type(e).__name__}: {e}")
