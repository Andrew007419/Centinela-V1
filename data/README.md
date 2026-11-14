# Datos

Aquí solo van **CSV pequeños ya procesados**. Los archivos originales y los pesados se guardan en Drive (ver `docs/ENLACES.md`).

## Registro de datasets

Llena una fila por cada archivo de `data/processed/`.

| Archivo | Fuente | Fecha de descarga | Filtros aplicados | Columnas | Limitaciones |
|---|---|---|---|---|---|
| `denue_312142_jalisco.csv` | DENUE (INEGI), versión mayo 2026 (periodo 05/2026) | 2026-11-13 | SCIAN 312144 (Elaboración de tequila), Jalisco | `nombre`, `municipio`, `clave_mun`, `lat`, `lon`, `estrato_personal` | Son establecimientos registrados en el DENUE, no productores agrícolas. Solo tequila, no otros destilados de agave. 3 filas con nombre vacío en el origen. La ficha original citaba 312142, de una versión anterior del SCIAN; el DENUE actual usa 312144. El nombre del archivo conserva 312142 por el contrato |
| `comercio_2208_90.csv` | DataMéxico (SE/SAT) | | Partida 2208.90 | | Estatal y por fracción, no por productor |
| `censo_3121_municipal.csv` | Censo Económico 2024 (INEGI) | | Rama 3121 | | Levantamiento de 2023 |
| `inventario_agave.csv` | CRT y prensa (ver ficha) | | | | Las cifras pueden no medir lo mismo, ver `ipo/SUPUESTOS.md` |

Las columnas mínimas esperadas están en `docs/03_CONTRATOS_ENTRE_ROLES.md`.
