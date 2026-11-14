"""Genera la serie anual de inventario de agave por interpolación lineal.

Anclas públicas:
- 2017: 29,000,000 plantas disponibles (The Logistics World / CRT, según ficha)
- 2022: 375,000,000 plantas disponibles (The Logistics World / CRT, según ficha)
- 2026: 1,704,000,000 plantas de inventario total en 511,492 ha (E&N / CRT, según ficha)

Los años intermedios se interpolan y se marcan como `interpolado`.
No se presentan como datos medidos.
"""

from __future__ import annotations

import csv
from pathlib import Path

ANCLAS = [
    {
        "anio": 2017,
        "plantas": 29_000_000,
        "hectareas": None,
        "fuente": "The Logistics World vía CRT (según ficha)",
        "definicion": "plantas disponibles (ancla)",
    },
    {
        "anio": 2022,
        "plantas": 375_000_000,
        "hectareas": None,
        "fuente": "The Logistics World vía CRT (según ficha)",
        "definicion": "plantas disponibles (ancla)",
    },
    {
        "anio": 2026,
        "plantas": 1_704_000_000,
        "hectareas": 511_492,
        "fuente": "Revista E&N vía CRT (según ficha)",
        "definicion": "inventario total (ancla)",
    },
]

COLUMNAS = [
    "anio",
    "plantas",
    "hectareas",
    "siembra_neta_plantas",
    "fuente",
    "definicion",
]


def _interpolar(a: dict, b: dict) -> list[dict]:
    """Interpola linealmente entre dos anclas, sin incluir la segunda."""
    if b["anio"] <= a["anio"]:
        raise ValueError("Las anclas deben estar en orden creciente")
    paso = (b["plantas"] - a["plantas"]) / (b["anio"] - a["anio"])
    filas = []
    for anio in range(a["anio"], b["anio"]):
        if anio == a["anio"]:
            filas.append(dict(a))
        else:
            filas.append(
                {
                    "anio": anio,
                    "plantas": int(round(a["plantas"] + paso * (anio - a["anio"]))),
                    "hectareas": None,
                    "fuente": "Interpolación lineal entre anclas (equipo)",
                    "definicion": "interpolado",
                }
            )
    return filas


def generar_serie(anclas: list[dict] | None = None) -> list[dict]:
    """Devuelve una fila por año, con anclas e interpolados."""
    anclas = anclas or ANCLAS
    if len(anclas) < 2:
        raise ValueError("Se requieren al menos dos anclas")
    if any(b["anio"] <= a["anio"] for a, b in zip(anclas, anclas[1:])):
        raise ValueError("Las anclas deben tener años estrictamente crecientes")

    filas: list[dict] = []
    for a, b in zip(anclas, anclas[1:]):
        filas.extend(_interpolar(a, b))
    filas.append(dict(anclas[-1]))

    # Siembra neta = diferencia de inventario respecto al año anterior.
    # Es una derivada de la serie, no un dato observado.
    for i, fila in enumerate(filas):
        if i == 0:
            fila["siembra_neta_plantas"] = None
        else:
            fila["siembra_neta_plantas"] = fila["plantas"] - filas[i - 1]["plantas"]

    # Verificaciones de cordura.
    anios = [f["anio"] for f in filas]
    if anios != list(range(anios[0], anios[-1] + 1)):
        raise ValueError("La serie tiene años faltantes o duplicados")
    if any(f["plantas"] <= 0 for f in filas):
        raise ValueError("Hay valores de plantas no positivos")
    if any(b["plantas"] < a["plantas"] for a, b in zip(filas, filas[1:])):
        raise ValueError("La serie no es monotónica; revisar anclas")

    return filas


def guardar_csv(filas: list[dict], destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNAS)
        writer.writeheader()
        for fila in filas:
            writer.writerow({k: ("" if fila.get(k) is None else fila.get(k)) for k in COLUMNAS})


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    destino = repo / "data" / "processed" / "inventario_agave.csv"
    filas = generar_serie()
    guardar_csv(filas, destino)

    print(f"Archivo: {destino}")
    print(f"Filas: {len(filas)} ({filas[0]['anio']}-{filas[-1]['anio']})")
    for fila in filas:
        marca = "ANCLA" if "ancla" in fila["definicion"] else "interpolado"
        print(f"{fila['anio']}: {fila['plantas']:>13,} plantas  [{marca}]")


if __name__ == "__main__":
    main()
