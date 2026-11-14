# Software y datos · Integrante 3

**Rama:** `software/...`
**Meta:** un panel web de 3 secciones que integra la visión, el IPO y los datos oficiales (DENUE, comercio exterior y Censo Económico), con código reproducible y datos abiertos en Drive.

## Entregables

| # | Entregable | Ruta |
|---|---|---|
| 1 | Panel web (Streamlit) con 3 secciones | `software/src/app.py` |
| 2 | ETL de DENUE 312144 (tequila), comercio (Banxico y Comtrade) y Censo 3121 | `software/etl/` |
| 3 | Datos procesados con los formatos del contrato | `data/processed/` |
| 4 | Carpeta de Drive abierta con datos y enlaces | `docs/ENLACES.md` |
| 5 | Código reproducible desde cero | este README + `requirements.txt` |
| 6 | Resumen de 10 líneas | `software/RESUMEN.md` |

## Las 3 secciones del panel

| Sección | Qué muestra | Viene de |
|---|---|---|
| **1. Conteo de plantas** | Sube una imagen o video, muestra las cajas y el conteo | `vision/src/inferencia.py` |
| **2. Calendario de madurez** | Oferta madura por año, con la banda del factor plantas→toneladas | Endpoint `/ipo` |
| **3. IPO y contexto** | IPO por escenario, tequileras por municipio, exportaciones y datos del Censo, con filtros por municipio | Endpoint `/ipo` + `data/processed/` |

Elementos que debe tener:
- Selector de **escenario** (optimista, base, pesimista).
- Filtro por **municipio** para DENUE y Censo.
- Un recuadro visible de **supuestos y fuentes** que lee del endpoint.
- Aviso claro de que el **IPO es regional** y los filtros municipales aplican al contexto (DENUE y Censo), no al IPO.
- Opcional: botón "¿Y si el productor escalona su cosecha?" que mueve la oferta y recalcula el IPO.

## Datos oficiales

| Dataset | Filtro | Archivo de salida |
|---|---|---|
| DENUE (INEGI) | Clase SCIAN **312144** (Elaboración de tequila), estado de Jalisco | `data/processed/denue_312142_jalisco.csv` (nombre legado del contrato) |
| Comercio exterior (Banxico, Cubo de Comercio Exterior) | Solo tequila (fracción 22089003 y subfracciones), serie mensual nacional, solo valor en USD | `data/processed/comercio_tequila_banxico.csv` |
| Comercio exterior (DataMéxico; respaldo UN Comtrade) | HS **220890** (2208.90), México | `data/processed/comercio_2208_90.csv` |
| Censo Económico 2024 (INEGI, SAIC) | Rama **3121**, por municipio. Las celdas vacías son confidenciales (no son cero) | `data/processed/censo_3121_municipal.csv` |
| Censo Económico 2024 (INEGI, SAIC) | Clase **312144** (tequila), por municipio. Las celdas vacías son confidenciales (no son cero) | `data/processed/censo_312144_tequila_municipal.csv` |

Enlaces oficiales en `docs/ENLACES.md`. Para cada dataset anota en `data/README.md`: fecha de descarga, filtros aplicados y columnas usadas.

### Reglas de datos
- Los archivos originales pesados se guardan en Drive, no en Git.
- Los CSV procesados deben ser pequeños y venir de un script en `software/etl/`, no de pasos manuales sin registrar.
- Normaliza los nombres de municipio y conserva la **clave de municipio** para poder cruzar fuentes.
- Anota las limitaciones: el DENUE es de establecimientos, no de productores agrícolas.

## Cómo correr el panel (esto debe funcionar en una computadora limpia)
```bash
python -m venv .venv
source .venv/bin/activate            # En Windows: .venv\Scripts\activate
pip install -r software/requirements.txt
pip install -r ipo/requirements.txt
pip install -r vision/requirements.txt

# Terminal 1: API del IPO
uvicorn ipo.src.api:app --reload

# Terminal 2: panel
streamlit run software/src/app.py
```
Si todavía no existen el endpoint o los pesos de visión, el panel debe usar **datos de ejemplo** marcados como tales, para poder avanzar en paralelo.

## Drive abierto
1. Crea una carpeta en Drive con subcarpetas `datos_originales`, `datos_procesados`, `dataset_vision`, `entregables`.
2. Compártela con **"Cualquier persona con el enlace puede ver"**.
3. Pega los enlaces en `docs/ENLACES.md`.

## Reproducibilidad
- Versiones fijas en `requirements.txt` cuando todo funcione (`pip freeze` de lo que usas).
- Semillas fijas (`seed=42`).
- Prueba **desde cero** en otra computadora o en un entorno nuevo el día 4.

## Criterio de terminado
- [ ] Las 3 secciones funcionan con visión e IPO reales
- [ ] Filtros por municipio operan con DENUE y Censo
- [ ] Datos procesados generados por scripts y descritos en `data/README.md`
- [ ] Drive abierto con enlaces en `docs/ENLACES.md`
- [ ] Una persona que no escribió el código lo corrió siguiendo este README
- [ ] `RESUMEN.md` escrito
