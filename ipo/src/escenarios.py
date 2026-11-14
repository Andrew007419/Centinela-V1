"""Escenarios de demanda y pesos de la ventana de maduración.

Los escenarios no son pronósticos: son combinaciones explícitas de supuestos
para mostrar el rango de resultados.
"""

from __future__ import annotations

ESCENARIOS = {
    "optimista": {
        "descripcion": "Demanda crece 3% anual y la oferta se reparte más entre 6, 7 y 8 años.",
        "crecimiento_demanda": 0.03,
        "pesos_ventana": (0.30, 0.40, 0.30),
    },
    "base": {
        "descripcion": "Demanda constante en 2.18 millones de t y ventana centrada en 7 años.",
        "crecimiento_demanda": 0.00,
        "pesos_ventana": (0.25, 0.50, 0.25),
    },
    "pesimista": {
        "descripcion": "Demanda cae 3% anual y la oferta se concentra en el año 7.",
        "crecimiento_demanda": -0.03,
        "pesos_ventana": (0.15, 0.70, 0.15),
    },
}


def obtener_escenario(nombre: str) -> dict:
    """Devuelve la configuración de un escenario o falla con un mensaje claro."""
    clave = (nombre or "").strip().lower()
    if clave not in ESCENARIOS:
        validos = ", ".join(sorted(ESCENARIOS))
        raise ValueError(f"Escenario inválido: {nombre!r}. Válidos: {validos}")
    config = ESCENARIOS[clave]
    pesos = config["pesos_ventana"]
    if abs(sum(pesos) - 1.0) > 1e-9:
        raise ValueError(f"Los pesos del escenario {clave} no suman 1")
    if not (-1 < config["crecimiento_demanda"] < 1):
        raise ValueError(f"Crecimiento fuera de rango en el escenario {clave}")
    return {"nombre": clave, **config}
