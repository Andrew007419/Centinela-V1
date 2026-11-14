# Sensibilidad del IPO

> Documento de apoyo para el jurado. No cambia el modelo: mueve una variable a la vez y muestra cuánto se mueve el resultado.
> Última actualización: 2026-11-13.
> Dueño: Integrante 2 (IPO y demanda).

## Qué se mueve y qué se deja fijo

Cada tabla mueve **una sola variable** y deja las demás en el escenario base:

- factor plantas→toneladas: 0.020 / 0.032 / 0.055 t/planta;
- ventana de maduración: pesos 25/50/25, 30/40/30 y 15/70/15;
- demanda: crecimiento +3%, 0% y -3% anual.

La oferta base usa las cohortes 6-8 años y la serie de inventario interpolada. El IPO se calcula como `oferta madura (t) / demanda (t)`.

## 1. Factor plantas → toneladas

Escenario base, demanda constante de 2.18 millones de t.

| Año | IPO con 0.020 | IPO con 0.032 | IPO con 0.055 |
|---:|---:|---:|---:|
| 2026 | 0.635 | 1.016 | 1.746 |
| 2029 | 1.238 | 1.981 | 3.405 |
| 2030 | 2.445 | 3.912 | 6.723 |
| 2031 | 3.048 | 4.877 | 8.382 |
| 2034 | 3.048 | 4.877 | 8.382 |

**Lectura:** en 2026 la banda cruza 1 (0.635 a 1.746), así que la conclusión es **incierta** para ese año. De 2031 en adelante, incluso el factor mínimo queda arriba de 3: la presión de oferta es **robusta** aunque el factor esté mal calibrado.

## 2. Ventana de maduración

Demanda base y factor base. Los pesos cambian el momento en que madura cada cohorte.

| Escenario | Pesos 6/7/8 | IPO 2029 | IPO 2030 | IPO 2031 |
|---|---|---:|---:|---:|
| Optimista | 30/40/30 | 2.174 | 3.719 | 4.877 |
| Base | 25/50/25 | 1.981 | 3.912 | 4.877 |
| Pesimista | 15/70/15 | 1.595 | 4.298 | 4.877 |

**Lectura:** la ventana mueve el IPO entre 2029 y 2030, pero no cambia la conclusión de 2031 en adelante. Concentrar la oferta en el año 7 adelanta la presión; repartirla la suaviza. En todos los casos, el IPO supera 1.5 desde 2029.

## 3. Demanda

Factor base y ventana base. Se aísla el efecto de la demanda.

| Escenario | Crecimiento anual | Demanda 2034 (t) | IPO 2029 | IPO 2031 | IPO 2034 |
|---|---:|---:|---:|---:|---:|
| Optimista | +3% | 2,844,406 | 1.760 | 4.084 | 3.738 |
| Base | 0% | 2,180,000 | 1.981 | 4.877 | 4.877 |
| Pesimista | -3% | 1,657,304 | 2.238 | 5.855 | 6.415 |

**Lectura:** si la demanda crece, el IPO baja; si cae, sube. Pero en los tres escenarios el IPO es mayor que 1 desde 2029 y mayor que 3.7 en 2034. La conclusión no depende de apostar por un crecimiento específico.

## Límites de esta sensibilidad

- No es una medición: el factor y la ventana son supuestos calibrados con literatura.
- No hay inventario por municipio; el IPO es regional.
- La siembra futura se mantiene constante solo para las cohortes que alcanzan a madurar en el horizonte.
- La demanda no se deriva de una conversión litros→toneladas; las exportaciones se usan como tendencia, no como demanda total.

## Cómo reproducirlo

```bash
python ipo/src/serie_inventario.py
.venv/bin/python -m pytest -q ipo/tests
.venv/bin/uvicorn ipo.src.api:app --reload
```

El endpoint entrega `ipo`, `ipo_min` e `ipo_max` por año. Las tablas de este documento se generan con los mismos valores del endpoint y sirven como respaldo para la defensa.
