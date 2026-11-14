# Datos

Aquí solo van **CSV pequeños ya procesados**. Los archivos originales y los pesados se guardan en Drive (ver `docs/ENLACES.md`).

## Registro de datasets

Llena una fila por cada archivo de `data/processed/`.

| Archivo | Fuente | Fecha de descarga | Filtros aplicados | Columnas | Limitaciones |
|---|---|---|---|---|---|
| `denue_312144_jalisco.csv` | DENUE (INEGI) | 2026-05 (corte DENUE) | SCIAN 312144 (Elaboración de tequila), Jalisco | `id`, `clee`, `nombre`, `municipio`, `clave_mun`, `lat`, `lon`, `estrato_personal`, `codigo_act`, `actividad`, `fecha_alta_denue` | 175 establecimientos; el código 312142 no existe en DENUE 2026-05. No incluye producción agrícola primaria. |
| `comercio_2208_90.csv` | UN Comtrade (respaldo de DataMéxico) | 2020-2025 | HS 220890, reporter México, exportaciones | `periodo`, `anio`, `flujo`, `partida`, `destino`, `partner_code`, `es_total`, `valor_usd`, `volumen`, `unidad`, `fuente` | DataMéxico no respondió (API 502); HS 220890 agrupa tequila y otros destilados. Valor FOB y peso neto en kg. `es_total=1` es la fila Mundo y no debe sumarse con los destinos. |
| `censo_3121_municipal.csv` | Censo Económico 2024 (INEGI) | Pendiente | Rama 3121 | Pendiente | Levantamiento de 2023 |
| `inventario_agave.csv` | CRT y prensa (ver ficha) | Generado 2026-11-13 | Interpolación lineal 2017-2022-2026 | `anio`, `plantas`, `hectareas`, `siembra_neta_plantas`, `fuente`, `definicion` | 10 filas; 2018-2021 y 2023-2025 son `interpolado`. `siembra_neta_plantas` es derivada, no observada. Las cifras pueden no medir lo mismo, ver `ipo/SUPUESTOS.md`. |

Las columnas mínimas esperadas están en `docs/03_CONTRATOS_ENTRE_ROLES.md`.

### Notas de esta descarga

- **DENUE:** el código correcto para “Elaboración de tequila” es **312144**, no 312142. El archivo se generó del corte DENUE 2026-05 para Jalisco.
- **Comercio:** DataMéxico (`api.datamexico.org` y su reemplazo) no respondió; se usó **UN Comtrade** como respaldo oficial. Si DataMéxico vuelve, se reemplaza el archivo y se conserva esta nota.
- **Totales:** las filas con `es_total=1` son el total mundial; no deben sumarse con las filas de destino.
- **Volumen:** UN Comtrade reporta peso neto en kg, no litros. No convertir a litros sin un factor documentado.

## Fuentes de esta descarga

- DENUE, INEGI: https://www.inegi.org.mx/app/descarga/default.html (corte 2026-05).
- UN Comtrade, HS 220890, reporter México: https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2024&cmdCode=220890&flowCode=X
- DataMéxico (fuente prevista original): https://www.economia.gob.mx/datamexico/
