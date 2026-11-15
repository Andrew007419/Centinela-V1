# Backtest de los supuestos del IPO

> No es un backtest de la demanda de agave: no existe una serie histórica pública de consumo por año.
> Es una prueba de los **dos supuestos que más mueven el resultado**: la interpolación del inventario y la tendencia de exportaciones.

## 1. Interpolación del inventario

La serie usa tres anclas: 2017 (29M), 2022 (375M) y 2026 (1,704M). Para probar qué tan bien representa la interpolación lineal, se hace una prueba de dejar fuera un ancla.

### 1.1 Si 2022 no se conociera

Se interpola entre 2017 y 2026 para estimar 2022:

| Dato | Plantas |
|---|---:|
| Predicción lineal 2017-2026 para 2022 | 959,555,556 |
| Valor real 2022 | 375,000,000 |
| Error | **+155.9%** |

**Lectura:** la interpolación lineal sobreestima 2022 porque el crecimiento no fue lineal. El ancla de 2022 es indispensable; sin ella, la serie no sirve.

### 1.2 Si 2026 no se conociera

Se extrapola la pendiente 2017-2022 hacia 2026:

| Dato | Plantas |
|---|---:|
| Predicción con pendiente 2017-2022 para 2026 | 651,800,000 |
| Valor real 2026 | 1,704,000,000 |
| Error | **-61.7%** |

**Lectura:** el inventario se aceleró después de 2022. Extrapolar el tramo viejo subestima casi dos terceras partes. Por eso la serie se marca como **interpolada** y el salto alrededor de 2030 se declara como consecuencia del método, no como un hecho observado.

## 2. Tendencia de exportaciones

Se usa el valor anual de Comtrade HS 220890 (fila Mundo) para probar tres formas simples de pronosticar 2025 con datos hasta 2024.

| Año | Valor exportado (USD) |
|---:|---:|
| 2020 | 2,397,631,737 |
| 2021 | 3,115,328,937 |
| 2022 | 4,229,883,695 |
| 2023 | 4,329,935,259 |
| 2024 | 4,123,214,628 |
| 2025 | 3,663,207,982 |

| Método para pronosticar 2025 | Predicción (USD) | Error vs. real |
|---|---:|---:|
| Repetir 2024 | 4,123,214,628 | **+12.6%** |
| CAGR 2020-2024 (14.52%) | 4,721,709,977 | **+28.9%** |
| Tendencia lineal 2020-2024 | 5,038,930,482 | **+37.6%** |

**Lectura:** la exportación de 2025 cayó **-11.16%** frente a 2024. Extrapolar el crecimiento 2020-2024 habría fallado por 29-38%. Por eso el modelo no usa una tasa alta: los escenarios de demanda son +3%, 0% y -3%, más conservadores y declarados.

## 3. Qué implica para el IPO

- La serie de inventario es una **aproximación**, no una medición. El salto de oferta alrededor de 2030 depende de la interpolación.
- La demanda no se deriva de una conversión litros→toneladas; las exportaciones se usan como tendencia y el escenario base mantiene la demanda en 2.18M t.
- El volumen 2021 de Comtrade cae a 329.2M kg mientras el valor sube; no se usa como conversión.
- La conclusión de presión de oferta desde 2031 es robusta a la banda del factor y a los tres escenarios, pero **no es una predicción de precio**.

## 4. Qué faltaría para un backtest completo

1. Serie anual de inventario por año de siembra (CRT/SIAP).
2. Serie histórica de consumo industrial de agave en toneladas (CNIT/CRT).
3. Precio pagado al productor por municipio y por año.
4. Serie mensual de Banxico 22089003 integrada al cálculo, no solo como contexto.

Con esos datos se podría comparar `demanda_t` contra consumo observado y `oferta_madura_t` contra sacrificio real. Hoy no existen públicos y se declaran como limitación.

## 5. Cómo reproducir

```bash
python ipo/src/serie_inventario.py
.venv/bin/python -m pytest -q ipo/tests
.venv/bin/uvicorn ipo.src.api:app --reload
```

Los valores de las tablas salen de `data/processed/inventario_agave.csv` y `data/processed/comercio_2208_90.csv`.
