# Supuestos del modelo IPO

> Documento vivo. Última actualización: 2026-11-11.
> Dueño: Ian Olave (IPO y demanda).
> Regla: cada cifra debe poder rastrearse a una fuente o a un supuesto escrito aquí.

## 0. Estado de la evidencia

- **Existencia del problema: confianza alta.** Hay múltiples fuentes que coinciden en el desplome y la volatilidad del precio del agave, y en el crecimiento del inventario.
- **Cifras exactas: confianza media-baja.** Las cifras de precio, inventario y consumo vienen de prensa y organismos; no existe una serie pública única, anual y municipal.
- **El IPO es un modelo con supuestos calibrables, no una medición.** No se presenta como predicción de precio.

## 1. Definiciones de inventario y demanda

| Cifra | Valor | Año | Fuente | Qué mide | Limitación |
|---|---:|---|---|---|---|
| Plantas disponibles | 29,000,000 | 2017 | The Logistics World, con datos de CRT (según ficha) | Plantas disponibles en ese corte | No es inventario total; puede excluir plantas jóvenes o no registradas |
| Plantas disponibles | 375,000,000 | 2022 | The Logistics World, con datos de CRT (según ficha) | Plantas disponibles en ese corte | Misma limitación; verificar definición antes de comparar |
| Inventario total | 1,704,000,000 | 2026 | Revista E&N, con datos de CRT (según ficha) | Inventario total en 511,492 ha | No es una serie; es un corte |
| Consumo industrial | 2,180,000 t | 2025 | CNIT (según ficha) | Agave consumido por la industria tequilera | No distingue región ni tipo de productor |
| Consumo industrial | 1,800,000 t | 2024 | CNIT (según ficha) | Agave consumido por la industria tequilera | Misma limitación |

**Regla:** no sumar 29M + 375M + 1,704M. Son **cortes** de distintos años y posiblemente distintas definiciones. Se usan como anclas para una serie, no como componentes de un total.

**Pendiente de verificar:** qué incluye exactamente cada cifra (plantas disponibles vs. inventario total; región; si incluye plantas de 1-3 años). Si no se puede verificar, se declara como supuesto y se mantiene la banda.

## 2. Interpolación de la serie de inventario

Solo hay tres anclas públicas: 2017, 2022 y 2026. Para construir una serie anual:

1. Unir 2017 con 2022 mediante interpolación lineal.
2. Unir 2022 con 2026 mediante interpolación lineal.
3. Marcar los años 2018-2021 y 2023-2025 como `interpolado`.
4. Guardar la serie en `data/processed/inventario_agave.csv` con columnas `anio`, `plantas`, `hectareas`, `fuente`, `definicion`.
5. Documentar el script que genera la serie en `ipo/src/serie_inventario.py`.

**Implementación:** `python ipo/src/serie_inventario.py` genera `data/processed/inventario_agave.csv` con 10 filas (2017-2026). Los años 2018-2021 y 2023-2025 quedan marcados como `interpolado`. La columna `siembra_neta_plantas` es una derivada de la serie, no un dato observado.

**Supuesto:** la interpolación lineal es una aproximación gruesa. No representa siembras reales año por año. Se usa solo para estimar tendencia y cohortes; no para afirmar que el inventario de un año específico fue exactamente ese.

**Si aparece una serie anual de CRT/SIAP:** reemplazar la interpolación y actualizar este documento. Si no aparece antes del 14 de noviembre, se entrega la interpolación declarada.

## 3. Ventana de maduración

- **Fuente oficial:** SIAP, monografía del agave tequilero 2023: la madurez tarda **6 a 8 años** después de plantado.
- **Pesos iniciales de la ventana:** 25% a los 6 años, 50% a los 7 años y 25% a los 8 años. Es un **supuesto del equipo**, no una medición.
- **Ajuste regional:** en la región de Tequila la cosecha puede iniciar a los 6-7 años; en Los Altos, a los 7-8. Si se consigue dato por municipio, se ajustan los pesos.
- **No usar 5-7 años** en la versión actual: contradice la monografía SIAP y el plan de 4 días.

## 4. Factor plantas → toneladas

No hay un factor oficial publicado. Se define una banda con literatura y se declara como supuesto calibrable:

| Nivel | t/planta | Equivalente | Fuente / justificación |
|---|---:|---:|---|
| Mínimo | 0.020 | 20 kg/piña | CIESTAAM (2021), modelo con cosecha temprana a 5 años y 20 kg/piña |
| Base | 0.032 | 32 kg/piña | SIAP 1986-2015: promedio estatal de 31-35 kg/piña; Mundo Cuervo reporta 35 kg promedio |
| Máximo | 0.055 | 55 kg/piña | Los Altos y Atotonilco: 50-60 kg/piña en buenos años; rango de literatura 30-60 kg |

**Regla:** la banda se propaga a toda la salida. El endpoint devuelve `ipo`, `ipo_min` e `ipo_max`. En el panel se muestra como área sombreada, no como una línea única.

**Si el jurado pregunta por el factor:** responder que es un supuesto calibrado con literatura, que la banda cubre el rango 20-55 kg/piña y que la conclusión se mantiene si la banda completa queda del mismo lado de 1. Si la banda cruza 1, se declara incertidumbre.

## 5. Demanda absorbible

La demanda no es solo exportación. Se construye así:

1. **Base:** 2.18 millones de toneladas de consumo industrial en 2025 (CNIT).
2. **Tendencia:** exportaciones de tequila, partida 2208.90, desde `data/processed/comercio_2208_90.csv`.
3. **Contexto reciente:** producción de tequila -1.7% y consumo de agave +3% en el primer semestre de 2026 (Swissinfo/EFE, datos CRT).
4. **Conversión:** llevar exportaciones a toneladas anuales solo si existe un factor documentado; si no, usarlas como **índice de tendencia** y no como toneladas.
5. **Escenarios:** optimista, base y pesimista, con supuestos explícitos de crecimiento de demanda y de concentración de oferta.

**Advertencia:** las exportaciones son un proxy de la demanda final, no la demanda total. No igualar exportaciones con consumo industrial.

## 6. Fórmula del IPO

```text
IPO = oferta madura (t) / demanda absorbible (t)
```

- **IPO > 1:** presión de oferta; conviene escalonar cosechas, diversificar compradores o frenar nuevas siembras.
- **IPO = 1:** equilibrio.
- **IPO < 1:** demanda relativamente holgada.

El IPO es **regional**, no municipal, mientras no exista inventario por municipio. No se presenta como predicción de precio.

## 7. Reglas de honestidad

- Todo número del panel, reporte o pitch debe rastrearse a una fuente o a un supuesto de este documento.
- Lo simulado se marca como simulado; lo interpolado, como interpolado.
- No se afirma que el modelo mide la realidad; se afirma que estima con supuestos declarados.
- Si cambia un supuesto, se actualiza este documento y se anota la fecha.

## 8. Pendientes antes del 14 de noviembre

- [ ] Confirmar definición de 29M, 375M y 1,704M con CRT/SIAP o transparencia.
- [ ] Buscar serie anual de inventario por año de siembra.
- [ ] Buscar precio por municipio o por lo menos estatal con fuente oficial.
- [ ] Verificar si el consumo CNIT es nacional o de la zona DOT.
- [ ] Descargar y filtrar comercio 220890 y DENUE 312144.
- [ ] Documentar el factor de conversión de litros de tequila a toneladas de agave, si se usa.

## 9. Fuentes

- SIAP, *Agave tequilero*, monografía 2023: https://www.gob.mx/cms/uploads/attachment/file/838414/agave_tequilero_monografi_a_2023.pdf
- CIESTAAM, *Ingresos y costos de producción de productos con diferentes avances de integración a la cadena de valor*: https://ciestaam.edu.mx/-publicaciones-/libros/ingresos-y-costos-de-produccion_integracion-cadena-de-valor.pdf
- Colpos, *Generación de 3 medidas de ganancia para la producción de Agave tequilana Weber en Amatitán, Jalisco* (2017): http://colposdigital.colpos.mx:8080/jspui/bitstream/handle/10521/3599/Contreras_Cruz_AL_MC_Economia_2017.pdf
- Botanical Sciences, *La agroindustria del agave tequilero Agave tequilana Weber*: https://www.botanicalsciences.com.mx/index.php/botanicalSciences/article/download/1473/1127/8520
- Mundo Cuervo / Google Arts & Culture, *¿Cómo se elabora el tequila?*: https://artsandculture.google.com/story/%C2%BFc%C3%B3mo-se-elabora-el-tequila-jose-cuervo-foundation/oAUR1byvTT08eA
