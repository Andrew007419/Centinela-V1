# Software y datos · Resumen (Integrante 3)
**Qué entrega:** un panel web en Streamlit con 3 secciones: conteo de plantas con el modelo de visión real (imagen o video), calendario de madurez con el IPO y su banda de incertidumbre, y contexto con exportaciones, DENUE y Censo, con filtro por municipio.
**Datos:** DENUE de mayo 2026 (clase 312144, tequila: 175 establecimientos en Jalisco), exportaciones mensuales de tequila de Banxico (2002-04 a 2026-09) y Censo Económico 2024 (rama 3121 y clase 312144, año 2023); todo sale de scripts en `software/etl/` y se describe en `data/README.md`.
**Cómo correrlo:** `pip install -r software/requirements.txt -r ipo/requirements.txt -r vision/requirements.txt`, luego `uvicorn ipo.src.api:app --reload` y `streamlit run software/src/app.py`.
**Si algo falta:** sin la API del IPO el panel usa datos de ejemplo marcados como tales; sin los CSV avisa en lugar de romperse.
**Limitación (visión):** el modelo se entrenó con imágenes aéreas y no se ha validado con la cámara del robot; en video, los IDs de seguimiento no son plantas únicas.
**Limitación (IPO):** es un modelo con supuestos declarados por el Integrante 2 y es regional: los filtros por municipio no lo afectan.
**Limitaciones (datos):** el comercio es nacional y preliminar (2026 parcial); el DENUE cuenta establecimientos de tequila, no productores agrícolas ni otros destilados; el Censo describe 2023 y sus celdas vacías son confidenciales (no son cero ni se suman).
**Si preguntan:** cada cifra del panel viene de un archivo con fuente en `data/README.md` o de un supuesto escrito; lo marcado como "ejemplo" no es un resultado.
**Uso de IA:** el código y la documentación de software se desarrollaron con apoyo de Claude Code (Anthropic), bajo la dirección del Integrante 3.
