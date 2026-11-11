# 04 · Plan de 4 días

Cada día termina con una **integración**: lo que cada rol tenga se sube en un Pull Request, aunque no esté perfecto. Una pieza imperfecta pero integrada vale más que una perfecta pero aislada.

## Resumen por día

| Día | Meta del equipo |
|---|---|
| **Día 1** | Alcance cerrado, dataset y datos listos, esqueleto del panel funcionando, bocetos del robot |
| **Día 2** | Visión e IPO funcionando por separado, CAD del chasis y mástil, borrador del reporte |
| **Día 3** | Todo integrado en el panel, vistas y BOM del robot, clips del modelo grabados |
| **Día 4** | Video, pitch y reporte cerrados, ensayo completo y respuestas a preguntas difíciles |

## Detalle por rol

| Rol | Día 1 | Día 2 | Día 3 | Día 4 |
|---|---|---|---|---|
| **Asesor mecatrónica** | Bocetos con medidas y lista de componentes preliminar | CAD de chasis oruga y mástil | Brazo plegado, vistas y explosionada, BOM final, animación de 10 s (o vistas estáticas si se atrasa) | Sección de limitaciones y plan por fases, entrega de clips y renders |
| **Integrante 1 · Visión** | Reunir y anotar el dataset, definir la división entrenamiento/validación/prueba | Primer entrenamiento y evaluación, iterar con más datos | Métricas finales en test no visto, `inferencia.py` listo, clip real corriendo | Apoyo en demo, `RESUMEN.md` y respaldo de la demo grabada |
| **Integrante 2 · IPO** | Reunir cifras, definir y documentar supuestos (cohortes, factor, demanda) | Modelo de cohortes con 3 escenarios | Endpoint `/ipo`, pruebas y análisis de sensibilidad | Documentación de supuestos, `RESUMEN.md`, apoyo en preguntas del IPO |
| **Integrante 3 · Software y datos** | Esqueleto del panel con datos de ejemplo, ETL de DENUE, comercio y Censo | Panel con sus 3 secciones y filtros por municipio | Integración con visión e IPO, Drive abierto, código reproducible | Pruebas desde cero en otra computadora, pulido final |
| **Integrante 4 · Entregables** | Esquemas del reporte, pitch y video | Borradores del reporte y la infografía | Manual de uso, guion del video, grabación de capturas | Video final, pitch, ensayo de 15 min y simulacro de preguntas |

## Puntos de control

- **Fin del día 1:** reunión de 15 minutos. ¿Hay bloqueos? ¿Los contratos de `docs/03` siguen bien?
- **Fin del día 2:** primera integración. Se prueba que el panel llama a visión e IPO.
- **Mediodía del día 3:** decisión del asesor sobre la animación. Si el render va atrasado, se entregan vistas estáticas y se sigue.
- **Fin del día 3:** congelación de funciones. A partir de aquí solo se corrigen errores.
- **Día 4, tarde:** ensayo completo cronometrado.

## Si algo se atrasa

| Problema | Qué hacer |
|---|---|
| Pocas imágenes de agave | Grabar un video propio caminando entre plantas y extraer cuadros; dividir el entrenamiento y la prueba **por video** |
| El modelo de visión da malas métricas | Reportarlas con honestidad y mostrar un clip con buenos y malos casos |
| El render del robot se atrasa | Entregar vistas estáticas y la animación mínima en baja resolución |
| Faltan datos para el IPO | Usar el supuesto declarado con banda y marcarlo en pantalla |
| Falla la demo en vivo | Tener un video de respaldo de la demo |
