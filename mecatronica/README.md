# Mecatrónica · Dueño del robot

**Responsable:** Asesor mecatrónica
**Ramas:** `mecatronica/...` (solo si quiere subir archivos ligeros; si no, entrega por Drive)
**No toca el código del panel.**

## Tu objetivo

Mostrar que el robot es un diseño creíble, con componentes reales y un camino claro hacia un prototipo. Nada se construye en estos 4 días.

## Entregables y prioridad

| Prioridad | Entregable | Ruta o lugar de entrega |
|---|---|---|
| 1 | CAD del chasis oruga + mástil + brazo plegado | Drive (STEP y GLB) |
| 1 | Vistas (frontal, lateral, superior, 3/4) y vista explosionada | `mecatronica/renders/` (PNG ligeros) |
| 2 | Lista de componentes con precios y justificación | `mecatronica/BOM.csv` |
| 3 | Animación mínima de 10 s: recorrer una hilera y extender el sensor | Drive (MP4) |
| 4 | Sección de limitaciones físicas y plan de prototipo por fases | `mecatronica/LIMITACIONES_Y_FASES.md` |
| 4 | Resumen de 10 líneas | `mecatronica/RESUMEN.md` |

> **Regla de recorte:** si el render o la animación se atrasan, entrega **vistas estáticas** y se sigue. La decisión se toma a mediodía del día 3.

## Especificaciones propuestas (a validar en el prototipo)

| Parámetro | Valor |
|---|---|
| Largo total | 1,100 mm |
| Ancho total (con orugas) | 700 mm |
| Distancia libre al suelo | 150 mm |
| Altura de la cubierta | 400 mm |
| Altura con mástil plegado / extendido | 1,100 mm / 1,800 mm |
| Peso estimado | 35-45 kg |
| Velocidad de trabajo (para animar) | 0.5 m/s |

### Orugas
- Una oruga de goma por lado (tracción diferencial), de 150 mm de ancho y 800 mm de apoyo.
- Rueda motriz trasera de 160 mm, rueda tensora delantera de 160 mm, 4 rodillos de 100 mm por lado en brazos oscilantes con resorte.
- Punta delantera levantada unos 25°, banda con tacos en V, guardafangos y faldón lateral contra espinas y tierra.
- Presión estimada sobre el suelo: unos 1.6 kPa (40 kg sobre 0.24 m²). Es una estimación de diseño.
- **Por qué orugas:** suelo volcánico irregular y con lodo, mejor reparto del peso, giro sobre el eje y agarre en pendientes.

### Mástil y cabezal
- Mástil telescópico de 2 tramos. Cabezal con altura ajustable de 0.9 a 1.5 m y riel horizontal de 400 mm.
- Antena GNSS-RTK en lo más alto, antena LoRa pequeña y luces LED.
- El cabezal lleva cámara estéreo y LiDAR. El espectrómetro NIR se muestra como **módulo de fase 2**.

### Brazo (solo plegado en el MVP)
- Se modela **plegado** sobre la cubierta, sin sobresalir de los 700 mm de ancho.
- Diseño de referencia para fase 2: 3 articulaciones (J1 giro 0°-90°, J2 hombro -20° a 70°, J3 codo 0° a 130°) y aguja lineal de 80 mm de carrera.

## Lista de componentes (BOM) de partida

Los costos son aproximados y **hay que cotizarlos**. Pon el rango y la fecha de consulta.

| Componente | Fase | Costo aprox. (USD) | Justificación |
|---|---|---|---|
| Computadora de borde tipo Jetson Orin en carcasa IP65 | 1 | 600-900 | Corre la visión en el campo sin depender de internet |
| Cámara estéreo | 1 | 450-550 | Detección y conteo de plantas, profundidad básica |
| GNSS-RTK con antena | 1 | 250-350 | Un ID geolocalizado por planta |
| Batería LiFePO4 24 V, 20-30 Ah | 1 | 250-400 | Autonomía de una jornada |
| Motorreductores y orugas | 1 | 600-1,000 | Movimiento en suelo difícil |
| Paro de emergencia, bumpers, LED y antena LoRa | 1 | 80-150 | Seguridad y comunicación |
| Panel solar de apoyo | 1 | 60-100 | Extiende la autonomía |
| LiDAR 3D compacto | 2 | 700-800 | Geometría 3D de la roseta (diámetro, altura, pencas) |
| Espectrómetro NIR | 2 | 300-2,000 | Firma espectral para estimar azúcares |
| Brazo con aguja, sensor de fuerza y refractómetro | 2 | 500-1,000 | Biopsia de calibración: da la verdad de campo al modelo |

### Por qué LiDAR, NIR y biopsia son fase 2
Estimar la masa y los azúcares de la piña oculta a partir de lo que se ve por fuera es una **hipótesis**. Para validarla hacen falta mediciones reales contra cosechas pesadas (jima). El LiDAR y el NIR aportan variables indirectas y la biopsia ancla esas variables a una medición real. Sin datos reales de campo no se puede calibrar, por eso entran después de la fase 1, que genera esos datos.

## Animación mínima de 10 s

| Tiempo | Cámara | Qué ocurre |
|---|---|---|
| 0-4 s | Lateral, siguiendo al robot | Avanza por el surco a 0.5 m/s, con las orugas girando |
| 4-6 s | Tres cuartos | Se detiene frente a una planta, se encienden las luces |
| 6-9 s | Cabezal en primer plano | El mástil se extiende y el cabezal sale por el riel hacia la planta; opcional: cono de escaneo semitransparente |
| 9-10 s | Plano fijo | Se mantiene la posición |

Datos útiles para Blender, a 30 fps y 0.5 m/s: la rueda motriz de 80 mm de radio gira unos **12° por cuadro**; los rodillos de 50 mm de radio, unos **19° por cuadro**. Para la banda de la oruga basta una textura de tacos con el nodo *Mapping* animado.

Render: Eevee, 1920 × 1080 a 30 fps (baja a 720p si va lento).

## Limitaciones físicas (punto de partida para tu sección)

- Las pencas tienen espinas: el robot debe mantener distancia y llevar faldones de protección.
- Terreno volcánico, lodo y pendientes: la tracción real hay que probarla en parcela.
- La autonomía de 6-8 horas y los 5-10 ha por jornada son estimaciones sin validar.
- Polvo, humedad y vibración: carcasas IP65 y conectores sellados.
- El robot ve la planta por fuera; la masa y los azúcares de la piña son variables ocultas.
- El brazo de biopsia es la parte mecatrónica más difícil. Ruta realista: biopsia manual de un técnico en fase 2 y robotizada después.
- Señal celular poco confiable: de ahí el cómputo en el borde.

## Plan de prototipo real por fases (tiempos tentativos)

| Fase | Qué se construye | Resultado esperado |
|---|---|---|
| 0 (esta entrega) | Diseño 3D, BOM y animación | Concepto creíble y cotizado |
| 1 (aprox. 1-2 meses) | Carrito oruga con cámara, GNSS y cómputo en el borde | Recorre parcelas reales y genera el dataset propio |
| 2 (aprox. 2-3 meses) | Se suma LiDAR y NIR; biopsia manual de un técnico | Primeros pares de mediciones contra jima para calibrar el modelo |
| 3 (aprox. 3-4 meses) | Brazo de biopsia robotizado con aprendizaje activo | Menos biopsias para la misma calibración |
| 4 | Piloto en 2-3 municipios con cooperativas | Validar el IPO y la reducción de variabilidad de precio |

## Cómo entregar (flujo sin Git, recomendado)

1. Sube a Drive los archivos pesados (`.f3d`, `.blend`, STEP, GLB, MP4) y pon el enlace en `docs/ENLACES.md` (o pásalo al Integrante 3).
2. Los renders ligeros, el `BOM.csv` y los `.md` los puede subir el Integrante 3, o tú con una rama `mecatronica/...` si te agregan como colaborador.
3. Avisa en el chat cuando algo esté listo.

## Criterio de terminado

- [ ] Ancho total de 700 mm y largo de 1,100 mm confirmados
- [ ] Vistas y explosionada exportadas
- [ ] BOM con rangos de costo, fase y justificación
- [ ] Animación de 10 s, o vistas estáticas si se activó el plan de recorte
- [ ] `LIMITACIONES_Y_FASES.md` y `RESUMEN.md` escritos
