# RESUMEN · IPO y demanda

**Dueño:** Integrante 2 · **Rama:** `ipo/resumen-final`

- Construí la serie anual de inventario 2017-2026 y el modelo de cohortes 6-8 años.
- La serie usa 29M plantas (2017), 375M (2022) y 1,704M (2026); los años intermedios son **interpolados** y están marcados.
- La oferta madura pasa de 69.2M plantas en 2026 a 332.25M en 2031, con los pesos base 25/50/25.
- La demanda base es 2.18M t (2025); los escenarios aplican +3%, 0% y -3% anual.
- El factor plantas→toneladas es una banda: 0.020 / 0.032 / 0.055 t/planta.
- Resultado base: IPO 1.016 en 2026, 4.877 en 2031 y 4.877 en 2034; `ipo_min` y `ipo_max` acompañan cada año.
- Entregué `GET /ipo` con escenarios, supuestos y fuentes; **33 pruebas pasan**.
- Limitación principal: el IPO es **regional**, no municipal; el salto alrededor de 2030 viene de la interpolación del inventario.
- Datos de contexto: DENUE 312144 (establecimientos), Banxico nacional/preliminar (solo valor; 2026 parcial), Comtrade HS 220890 (otros destilados) y Censo 2023 (celdas confidenciales); el cálculo usa demanda base y Comtrade solo como tendencia.
- El IPO no es una predicción de precio: es un índice de presión; en 2026 la banda cruza 1, desde 2031 la presión es robusta en los tres escenarios.
