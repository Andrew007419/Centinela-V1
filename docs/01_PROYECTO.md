# 01 · El proyecto

## El problema (según la ficha de problemática)

En Altos Sur y Valles de Jalisco, los pequeños productores de agave azul sin contrato con una tequilera enfrentan un desplome y una alta volatilidad del precio de su cosecha. Se sembró durante el auge sin ninguna señal de cuánta agave madura absorbería la industria.

| Dato | Valor | Periodo | Fuente (según la ficha) |
|---|---|---|---|
| Precio máximo del agave | 32 pesos/kg | 2022 | Crónica |
| Rango de operaciones recientes | 0.8 a 8 pesos/kg | 2025-2026 | Vinetur |
| Caída del precio reportada por SADER | -8.1% en Jalisco | 2024 | Plano Informativo |
| Ingreso que dejaron de recibir los productores de Jalisco | 3,743 millones de pesos | 2024 | Plano Informativo |
| Plantas disponibles | de 29 a 375 millones | 2017-2022 | The Logistics World (datos CRT) |
| Inventario actual | más de 1,704 millones de plantas en 511,492 ha | 2026 | Revista E&N (datos CRT) |
| Consumo industrial de agave | 2.18 millones de toneladas (1.8 en 2024) | 2025 | Líder Empresarial (datos CNIT) |
| Producción de tequila vs. consumo de agave | -1.7% producción, +3% consumo de agave | 1.er semestre 2026 | Swissinfo/EFE (datos CRT) |

**Causa raíz que atacamos:** no hay una señal anticipada del choque entre la oferta madura y la demanda. El inventario se cuenta en plantas autodeclaradas, la industria consume toneladas y nadie publica el factor de conversión ni una serie de precios.

## La solución en una línea

Un robot de campo que mide la madurez de cada planta, más un sistema que pronostica la oferta madura y la compara con la demanda de la industria mediante el **Índice de Presión de Oferta (IPO)**.

```
IPO = oferta madura pronosticada / demanda absorbible
IPO > 1  ->  presión de oferta: conviene escalonar cosechas, diversificar o frenar siembras
```

## Alcance del MVP de 4 días

| Se hace | No se hace en esta fase |
|---|---|
| Detección y conteo de plantas con YOLOv8 | Estimar masa y azúcares por planta (no hay datos para validarlo) |
| Modelo de cohortes de oferta madura + demanda + IPO con 3 escenarios | Predicción por planta de la fecha de cosecha |
| Panel web con 3 secciones y datos oficiales | App móvil, alertas, aprendizaje federado real |
| Diseño 3D del robot, BOM y animación de 10 s | Construir o probar el robot |
| Edge computing demostrado en laptop | Despliegue en Jetson y red LoRa (solo diagrama) |

Los tres pilares siguen presentes: **mecatrónica** (diseño), **Machine Learning** (visión + modelo de oferta) y **edge/IoT** (modelo ligero corriendo localmente y arquitectura documentada).

## Datasets oficiales del catálogo que usamos

| Dataset | Qué usamos | Para qué |
|---|---|---|
| DENUE (INEGI), clase SCIAN **312144** | Tequileras por municipio, ubicación y estrato de personal | Dónde está la demanda y qué tamaño tiene |
| Comercio exterior (DataMéxico), partida **2208.90** | Valor y volumen exportado de tequila, destino | Tendencia de la demanda final |
| Censo Económico 2024 (INEGI), rama **3121** | Producción bruta, valor agregado, personal ocupado | Tamaño y concentración de la industria compradora |

## Limitaciones que debemos decir con honestidad

- La ficha tiene **nivel de confianza bajo**. Las cifras de precio vienen de prensa y organizaciones de productores.
- No existe serie pública del precio de libre mercado ni datos de costos por hectárea.
- Las fuentes no coinciden en la producción de tequila de 2025 (CNIT: 496 millones de litros; CRT: 583 millones).
- El DENUE no incluye la producción agrícola primaria: los agaveros no aparecen.
- El factor plantas→toneladas no está publicado: se declara como supuesto con una banda.
- Las cifras de 29, 375 y 1,704 millones de plantas pueden no medir exactamente lo mismo. Hay que documentar la definición antes de usarlas juntas.

## Principio del proyecto

> El agave no se desplomó por falta de tequila, sino por falta de información anticipada.
