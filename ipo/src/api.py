"""API mínima del IPO para el panel y el video."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from ipo.src.modelo import calcular_ipo

app = FastAPI(
    title="Centinela·Agave · IPO",
    description="Índice de Presión de Oferta de agave con banda de factor y 3 escenarios.",
    version="0.1.0",
)


@app.get("/")
def raiz() -> dict:
    return {
        "nombre": "Centinela·Agave IPO",
        "endpoint": "/ipo?escenario=base&anio_inicio=2026&anio_fin=2034",
        "escenarios": ["optimista", "base", "pesimista"],
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ipo")
def ipo(
    escenario: str = Query("base", description="optimista, base o pesimista"),
    anio_inicio: int = Query(2026, ge=2026, le=2040),
    anio_fin: int = Query(2034, ge=2026, le=2040),
) -> dict:
    try:
        return calcular_ipo(
            escenario=escenario,
            anio_inicio=anio_inicio,
            anio_fin=anio_fin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
