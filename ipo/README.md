# IPO y demanda · Integrante 2

**Rama:** `ipo/...`
**Meta:** un modelo de cohortes que estima cuánta agave madura cada año, lo compara con la demanda de la industria y entrega el Índice de Presión de Oferta (IPO) con 3 escenarios, mediante un endpoint.

```
IPO = oferta madura (t) / demanda absorbible (t)
```

## Entregables

| # | Entregable | Ruta |
|---|---|---|
| 1 | Modelo de cohortes (ventana de maduración de 6 a 8 años) | `ipo/src/modelo.py` |
| 2 | Modelo de demanda (2.18 M t más exportaciones) | `ipo/src/demanda.py` |
| 3 | Factor plantas→toneladas declarado, con banda | `ipo/SUPUESTOS.md` |
| 4 | 3 escenarios (optimista, base y pesimista) | `ipo/src/escenarios.py` |
| 5 | Endpoint `/ipo` según el contrato | `ipo/src/api.py` |
| 6 | Pruebas y análisis de sensibilidad | `ipo/tests/` y `ipo/SENSIBILIDAD.md` |
| 7 | Resumen de 10 líneas | `ipo/RESUMEN.md` |

## Datos de partida (de la ficha de problemática)

| Dato | Valor | Año |
|---|---|---|
| Plantas disponibles (CRT) | 29 millones | 2017 |
| Plantas disponibles (CRT) | 375 millones | 2022 |
| Inventario (CRT) | más de 1,704 millones de plantas | 2026 |
| Consumo industrial (CNIT) | 2.18 millones de toneladas | 2025 |
| Consumo industrial (CNIT) | 1.8 millones de toneladas | 2024 |
| Tequila vs. consumo de agave, 1.er semestre | -1.7% producción, +3% consumo de agave | 2026 |

> **Atención:** antes de combinarlas, escribe qué mide exactamente cada cifra (plantas "disponibles" frente a "inventario" total, qué región cubre cada una). Si no miden lo mismo, dilo en `SUPUESTOS.md` y elige un tratamiento explícito.

## Paso a paso

### 1. Serie de inventario por año (día 1)
Con los tres puntos (2017, 2022, 2026) arma una serie anual por interpolación documentada. De ella sale una **siembra neta por año** aproximada. Guarda la serie en `data/processed/inventario_agave.csv`, con columnas `anio`, `plantas`, `hectareas`, `siembra_neta_plantas`, `fuente`, `definicion`.

### 2. Cohortes de maduración (día 2)
- Cada cohorte es el conjunto de plantas sembradas en un año.
- Cada cohorte madura en una ventana de **6 a 8 años** después de la siembra, con pesos configurables (por ejemplo 25%, 50%, 25% como punto de partida, y se declara como supuesto).
- **Oferta madura del año Y** = suma de lo que aporta cada cohorte cuya ventana cae en Y.
- Verificación obligatoria: la suma de todas las cohortes debe cuadrar con el inventario de partida.

### 3. Factor plantas→toneladas, con banda
- Define tres valores en t/planta: **mínimo, base y máximo**, cada uno con su fuente o con la nota "supuesto del equipo" si no hay una.
- La banda se propaga a toda la salida: el IPO se entrega como `ipo`, `ipo_min` e `ipo_max`.
- Para el panel, muestra la banda como un área sombreada y no como una sola línea.

### 4. Demanda
- Base: consumo industrial de **2.18 millones de t (2025)**.
- Proyección: tendencia de las **exportaciones de tequila** (partida 2208.90) de `data/processed/comercio_2208_90.csv`, más el dato de que la producción de tequila bajó 1.7% en el primer semestre de 2026.
- Convierte la demanda a toneladas anuales y, si hace falta, a plantas equivalentes con el factor.

### 5. Escenarios
Cada escenario cambia cosas explícitas y documentadas:

| Escenario | Qué se mueve |
|---|---|
| Optimista | La demanda crece más rápido, ventana de maduración más amplia (la oferta se reparte mejor) |
| Base | Tendencia observada |
| Pesimista | La demanda se estanca o cae, la oferta madura se concentra |

Las cifras exactas las defines tú y las dejas escritas en `SUPUESTOS.md`.

### 6. Endpoint
Implementa `GET /ipo?escenario=base&anio_inicio=2026&anio_fin=2034` en FastAPI, con el formato de `docs/03_CONTRATOS_ENTRE_ROLES.md`. Prueba con:
```bash
pip install -r ipo/requirements.txt
uvicorn ipo.src.api:app --reload
```
y abre http://127.0.0.1:8000/docs.

### 7. Sensibilidad
En `SENSIBILIDAD.md` muestra qué tanto cambia el IPO al mover el factor, la ventana y el crecimiento de la demanda. Esto responde de antemano a la pregunta "¿y si tus supuestos están mal?".

## Reglas de honestidad
- Es un **modelo con supuestos calibrables**, no una medición.
- Cada número del panel debe poder rastrearse a una fuente o a un supuesto escrito.
- El IPO es **regional** (no hay datos por municipio de inventario); no lo presentes como si lo fuera.

## Criterio de terminado
- [ ] Las cohortes cuadran con el inventario
- [ ] Factor plantas→t con mínimo, base y máximo, y su justificación
- [ ] 3 escenarios que producen resultados distintos y explicables
- [ ] Endpoint que cumple el contrato y responde con `supuestos` y `fuentes`
- [ ] Pruebas que corren con `pytest`
- [ ] `SUPUESTOS.md`, `SENSIBILIDAD.md` y `RESUMEN.md` escritos
