# Datos

Aquí solo van **CSV pequeños ya procesados**. Los archivos originales y los pesados se guardan en Drive (ver `docs/ENLACES.md`).

## Registro de datasets

Llena una fila por cada archivo de `data/processed/`.

| Archivo | Fuente | Fecha de descarga | Filtros aplicados | Columnas | Limitaciones |
|---|---|---|---|---|---|
| `denue_312142_jalisco.csv` | DENUE (INEGI), versión mayo 2026 (periodo 05/2026) | 2026-11-13 | SCIAN 312144 (Elaboración de tequila), Jalisco | `nombre`, `municipio`, `clave_mun`, `lat`, `lon`, `estrato_personal` | Son establecimientos registrados en el DENUE, no productores agrícolas. Solo tequila, no otros destilados de agave. 3 filas con nombre vacío en el origen. La ficha original citaba 312142, de una versión anterior del SCIAN; el DENUE actual usa 312144. El nombre del archivo conserva 312142 por el contrato |
| `comercio_2208_90.csv` | DataMéxico (SE/SAT) | | Partida 2208.90 | | Estatal y por fracción, no por productor |
| `comercio_tequila_banxico.csv` | Banxico, Cubo de Comercio Exterior (Matriz Productos, exportaciones, valor en dólares) | 2026-11-13 | Solo tequila, 2002-04 a 2026-09: 2002-04 a 2020-12 = 22089003; 2021-01 a 2021-11 = 2208909901 + 2208909992; 2021-12 = 2208900301 + 2208900391 + 2208909901; desde 2022-01 = 2208900301 + 2208900391. Se ignoran NA y celdas vacías | `periodo` (AAAA-MM), `valor_usd`, `volumen` (vacío), `unidad` (vacío), `destino` ("todas las regiones") | Serie mensual **nacional** (no solo Jalisco), solo valor en USD (sin volumen ni destino). Cifras preliminares. La clasificación arancelaria cambió en 2021, por lo que se empalman fracciones distintas; 2021 posiblemente subestimado (~5%). 2208900300 (No identificado) excluido. **2026 es parcial** (hasta septiembre). A diferencia de `comercio_2208_90.csv` (UN Comtrade, HS 220890 completo, del Integrante 2), esta serie es solo tequila. Generado por `software/etl/comercio_2208_90.py` |
| `censo_3121_municipal.csv` | Censo Económico 2024 (INEGI) | | Rama 3121 | | Levantamiento de 2023 |
| `inventario_agave.csv` | CRT y prensa (ver ficha) | | | | Las cifras pueden no medir lo mismo, ver `ipo/SUPUESTOS.md` |

Las columnas mínimas esperadas están en `docs/03_CONTRATOS_ENTRE_ROLES.md`.
