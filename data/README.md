# Datos

Aquí solo van **CSV pequeños ya procesados**. Los archivos originales y los pesados se guardan en Drive (ver `docs/ENLACES.md`).

## Registro de datasets

Llena una fila por cada archivo de `data/processed/`.

| Archivo | Fuente | Fecha de descarga | Filtros aplicados | Columnas | Limitaciones |
|---|---|---|---|---|---|
| `denue_312142_jalisco.csv` | DENUE (INEGI), versión mayo 2026 (periodo 05/2026) | 2026-11-13 | SCIAN 312144 (Elaboración de tequila), Jalisco | `nombre`, `municipio`, `clave_mun`, `lat`, `lon`, `estrato_personal` | Son establecimientos registrados en el DENUE, no productores agrícolas. Solo tequila, no otros destilados de agave. 3 filas con nombre vacío en el origen. La ficha original del reto citaba 312142, código que no existe en el DENUE ni en el SAIC (SCIAN 2023); el código vigente es 312144. El nombre del archivo conserva 312142 por el contrato |
| `comercio_2208_90.csv` | UN Comtrade (respaldo de DataMéxico) | 2020-2025 | HS 220890, reporter México, exportaciones | `periodo`, `anio`, `flujo`, `partida`, `destino`, `partner_code`, `es_total`, `valor_usd`, `volumen`, `unidad`, `fuente` | DataMéxico no respondió (API 502); HS 220890 agrupa tequila y otros destilados. Valor FOB y peso neto en kg. `es_total=1` es la fila Mundo y no debe sumarse con los destinos. **Volumen 2021 anómalo:** cae a 329.2M kg mientras el valor sube a US$3,115M; valor/kg = 9.46. Revisar antes de usar el volumen como tendencia. |
| `comercio_tequila_banxico.csv` | Banxico, Cubo de Comercio Exterior (Matriz Productos, exportaciones, valor en dólares) | 2026-11-13 | Solo tequila, 2002-04 a 2026-09: 2002-04 a 2020-12 = 22089003; 2021-01 a 2021-11 = 2208909901 + 2208909992; 2021-12 = 2208900301 + 2208900391 + 2208909901; desde 2022-01 = 2208900301 + 2208900391. Se ignoran NA y celdas vacías | `periodo` (AAAA-MM), `valor_usd`, `volumen` (vacío), `unidad` (vacío), `destino` ("todas las regiones") | Serie mensual **nacional** (no solo Jalisco), solo valor en USD (sin volumen ni destino). Cifras preliminares. La clasificación arancelaria cambió en 2021, por lo que se empalman fracciones distintas; 2021 posiblemente subestimado (~5%). 2208900300 (No identificado) excluido. **2026 es parcial** (hasta septiembre). A diferencia de `comercio_2208_90.csv` (UN Comtrade, HS 220890 completo, del Integrante 2), esta serie es solo tequila. Generado por `software/etl/comercio_2208_90.py` |
| `censo_3121_municipal.csv` | INEGI, Censos Económicos 2024, resultados definitivos (SAIC) | 2026-11-13 (consultado) | SCIAN 2023; Jalisco, nivel municipal, año censal 2023, **rama 3121** (Industria de las bebidas). Sin filas estatales ni "Total municipal" | `municipio`, `clave_mun`, `anio`, `produccion_bruta`, `valor_agregado`, `personal_ocupado`, `unidades_economicas`, `confidencial` | 115 municipios: 71 con las tres variables y 44 confidenciales. Ver limitaciones comunes del Censo abajo. Generado por `software/etl/censo_3121.py` |
| `censo_312144_tequila_municipal.csv` | INEGI, Censos Económicos 2024, resultados definitivos (SAIC) | 2026-11-13 (consultado) | SCIAN 2023; Jalisco, nivel municipal, año censal 2023, **clase 312144** (Elaboración de tequila). Sin filas estatales ni "Total municipal" | `municipio`, `clave_mun`, `anio`, `produccion_bruta`, `valor_agregado`, `personal_ocupado`, `unidades_economicas`, `confidencial` | 33 municipios: 8 con las tres variables y 25 confidenciales. Ver limitaciones comunes del Censo abajo. Generado por `software/etl/censo_3121.py` |
| `inventario_agave.csv` | CRT y prensa (ver ficha) | Generado 2026-11-13 | Interpolación lineal 2017-2022-2026 | `anio`, `plantas`, `hectareas`, `siembra_neta_plantas`, `fuente`, `definicion` | 10 filas; 2018-2021 y 2023-2025 son `interpolado`. `siembra_neta_plantas` es derivada, no observada. Las cifras pueden no medir lo mismo, ver `ipo/SUPUESTOS.md`. |

Las columnas mínimas esperadas están en `docs/03_CONTRATOS_ENTRE_ROLES.md`.

### Notas de esta descarga

- **DENUE:** el código correcto para “Elaboración de tequila” es **312144**, no 312142. El nombre del archivo conserva 312142 por el contrato del panel. El archivo se generó del corte DENUE 2026-05 para Jalisco.
- **Comercio:** DataMéxico (`api.datamexico.org` y su reemplazo) no respondió; se usó **UN Comtrade** como respaldo oficial. Si DataMéxico vuelve, se reemplaza el archivo y se conserva esta nota.
- **Banxico:** la serie mensual de la fracción 22089003 es más específica que Comtrade porque separa tequila. Se integra como **valor**; no reemplaza el volumen en kg de Comtrade.
- **Totales:** las filas con `es_total=1` son el total mundial; no deben sumarse con las filas de destino.
- **Volumen:** UN Comtrade reporta peso neto en kg, no litros. No convertir a litros sin un factor documentado.
- **2021:** el volumen de Comtrade cae a 329.2M kg mientras el valor sube a US$3,115M (9.46 USD/kg). Puede ser cambio de mix o revisión de la fuente; usar valor para tendencia y volumen con cautela hasta cruzar con Banxico.

## Notas sobre el Censo Económico 2024

**Limitaciones comunes de los dos CSV del Censo**
- El Censo 2024 describe el año 2023 (`anio` = 2023).
- Los valores monetarios (`produccion_bruta`, `valor_agregado`) están en millones de pesos a precios corrientes de 2023.
- Las celdas vacías son datos **confidenciales** de INEGI: no son cero y no se suman a totales. `confidencial` = 1 si falta alguna de `produccion_bruta`, `valor_agregado` o `personal_ocupado`. Los ceros y los valores negativos del origen (p. ej. `valor_agregado` negativo) se conservan tal cual.
- No se pueden sumar los municipios para obtener el total estatal: los municipios confidenciales no aportan a la suma.
- El personal ocupado del Censo no equivale a puestos de trabajo afiliados al IMSS.

**Totales estatales de Jalisco (fila estatal del SAIC, no incluida en los CSV)**
- Clase 312144 (Elaboración de tequila): 149 unidades económicas, 14,606 personas, producción bruta 70,712.484 y valor agregado 22,416.700 (millones de pesos).
- Rama 3121 (Industria de las bebidas): 2,634 unidades económicas; el resto de las variables es confidencial en el estado.

## Fuentes de esta descarga

- DENUE, INEGI: https://www.inegi.org.mx/app/descarga/default.html (corte 2026-05).
- UN Comtrade, HS 220890, reporter México: https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2024&cmdCode=220890&flowCode=X
- DataMéxico (fuente prevista original): https://www.economia.gob.mx/datamexico/
