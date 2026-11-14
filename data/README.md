# Datos

Aquí solo van **CSV pequeños ya procesados**. Los archivos originales y los pesados se guardan en Drive (ver `docs/ENLACES.md`).

## Registro de datasets

Llena una fila por cada archivo de `data/processed/`.

| Archivo | Fuente | Fecha de descarga | Filtros aplicados | Columnas | Limitaciones |
|---|---|---|---|---|---|
| `denue_312142_jalisco.csv` | DENUE (INEGI), versión mayo 2026 (periodo 05/2026) | 2026-11-13 | SCIAN 312144 (Elaboración de tequila), Jalisco | `nombre`, `municipio`, `clave_mun`, `lat`, `lon`, `estrato_personal` | Son establecimientos registrados en el DENUE, no productores agrícolas. Solo tequila, no otros destilados de agave. 3 filas con nombre vacío en el origen. La ficha original citaba 312142, de una versión anterior del SCIAN; el DENUE actual usa 312144. El nombre del archivo conserva 312142 por el contrato |
| `comercio_2208_90.csv` | UN Comtrade (respaldo de DataMéxico) | 2020-2025 | HS 220890, reporter México, exportaciones | `periodo`, `anio`, `flujo`, `partida`, `destino`, `partner_code`, `es_total`, `valor_usd`, `volumen`, `unidad`, `fuente` | DataMéxico no respondió (API 502); HS 220890 agrupa tequila y otros destilados. Valor FOB y peso neto en kg. `es_total=1` es la fila Mundo y no debe sumarse con los destinos. **Volumen 2021 anómalo:** cae a 329.2M kg mientras el valor sube a US$3,115M; valor/kg = 9.46. Revisar antes de usar el volumen como tendencia. |
| `comercio_tequila_banxico.csv` | Banxico, fracción 22089003 (tequila), serie mensual | Pendiente de merge (compañero 3) | Solo tequila; 2002-2026; USD | Pendiente | Es valor, no volumen; confirmar si es nacional o Jalisco. Sirve para tendencia de valor y complementa a Comtrade. |
| `censo_3121_municipal.csv` | Censo Económico 2024 (INEGI) | Pendiente | Rama 3121 | Pendiente | Levantamiento de 2023 |
| `inventario_agave.csv` | CRT y prensa (ver ficha) | Generado 2026-11-13 | Interpolación lineal 2017-2022-2026 | `anio`, `plantas`, `hectareas`, `siembra_neta_plantas`, `fuente`, `definicion` | 10 filas; 2018-2021 y 2023-2025 son `interpolado`. `siembra_neta_plantas` es derivada, no observada. Las cifras pueden no medir lo mismo, ver `ipo/SUPUESTOS.md`. |

Las columnas mínimas esperadas están en `docs/03_CONTRATOS_ENTRE_ROLES.md`.

### Notas de esta descarga

- **DENUE:** el código correcto para “Elaboración de tequila” es **312144**, no 312142. El nombre del archivo conserva 312142 por el contrato del panel. El archivo se generó del corte DENUE 2026-05 para Jalisco.
- **Comercio:** DataMéxico (`api.datamexico.org` y su reemplazo) no respondió; se usó **UN Comtrade** como respaldo oficial. Si DataMéxico vuelve, se reemplaza el archivo y se conserva esta nota.
- **Banxico:** la serie mensual de la fracción 22089003 es más específica que Comtrade porque separa tequila. Se integra como **valor**; no reemplaza el volumen en kg de Comtrade.
- **Totales:** las filas con `es_total=1` son el total mundial; no deben sumarse con las filas de destino.
- **Volumen:** UN Comtrade reporta peso neto en kg, no litros. No convertir a litros sin un factor documentado.
- **2021:** el volumen de Comtrade cae a 329.2M kg mientras el valor sube a US$3,115M (9.46 USD/kg). Puede ser cambio de mix o revisión de la fuente; usar valor para tendencia y volumen con cautela hasta cruzar con Banxico.

## Fuentes de esta descarga

- DENUE, INEGI: https://www.inegi.org.mx/app/descarga/default.html (corte 2026-05).
- UN Comtrade, HS 220890, reporter México: https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2024&cmdCode=220890&flowCode=X
- DataMéxico (fuente prevista original): https://www.economia.gob.mx/datamexico/
