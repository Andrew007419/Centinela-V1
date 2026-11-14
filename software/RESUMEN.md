# Software y datos · Resumen (Integrante 3)
**Qué entrega:** un panel web en Streamlit con 3 secciones: conteo de plantas con el modelo de visión real (imagen o video), calendario de madurez con el IPO y su banda de incertidumbre, y contexto con exportaciones, DENUE y Censo, con filtro por municipio.
**Datos:** DENUE de mayo 2026 (clase 312144, tequila: 175 establecimientos en Jalisco), exportaciones mensuales de tequila de Banxico (2002-04 a 2026-09), UN Comtrade del Integrante 2 como apoyo (HS 220890, con destinos y volumen, 2020-2025) y Censo Económico 2024 (rama 3121 y clase 312144, año 2023); descritos en `data/README.md`, con ETL en `software/etl/`.
**Cómo correrlo:** `pip install -r software/requirements.txt -r ipo/requirements.txt -r vision/requirements.txt`, luego `uvicorn ipo.src.api:app --reload` y `streamlit run software/src/app.py`.
**Si algo falta:** sin la API del IPO el panel usa datos de ejemplo marcados como tales; sin los CSV avisa en lugar de romperse.
**Limitación (visión):** el modelo se entrenó con imágenes aéreas y no se ha validado con la cámara del robot; en video, los IDs de seguimiento no son plantas únicas.
**Limitación (IPO):** es un modelo, no una medición: sus supuestos están en `ipo/SUPUESTOS.md` y su sensibilidad en `ipo/SENSIBILIDAD.md`; es regional, así que los filtros por municipio no lo afectan.
**Limitaciones (datos):** Banxico es nacional y preliminar (2026 parcial); Comtrade agrupa todos los destilados de HS 220890, no solo tequila; el DENUE cuenta establecimientos, no productores agrícolas; el Censo describe 2023 y sus celdas vacías son confidenciales (no son cero ni se suman).
**Si preguntan:** cada cifra del panel viene de un archivo con fuente en `data/README.md` o de un supuesto escrito; lo marcado como "ejemplo" no es un resultado.
**Uso de IA:** el código y la documentación de software se desarrollaron con apoyo de Claude Code (Anthropic), bajo la dirección del Integrante 3.
