# Preguntas difíciles y guía de respuesta

Esta es una guía de **cómo responder con honestidad**, no un guion. Cada respuesta debe apoyarse en los resultados reales del equipo. Completa los espacios `[...]` con lo que el proyecto realmente logró.

| # | Pregunta probable | Quién responde | Guía de respuesta |
|---|---|---|---|
| 1 | ¿El robot ya existe? | Asesor | No. Es un diseño 3D con componentes comerciales cotizados y un plan por fases. La fase 1 genera los primeros datos reales. |
| 2 | ¿Cuánto costaría? | Asesor | Es una estimación a cotizar, con rangos por componente, y se muestra la BOM. No prometer una cifra exacta. |
| 3 | ¿Cómo sabes que ver la planta por fuera dice algo de la piña oculta? | Asesor / Int. 1 | Es una hipótesis. Por eso la fase 2 incluye calibración contra cosechas reales y biopsia. En el MVP solo se detecta y cuenta. |
| 4 | ¿Qué tan bien detecta tu modelo? | Int. 1 | Dar las métricas de prueba tal cual: `[precisión, recall, mAP]`, explicar cómo se dividieron los datos y mostrar también los fallos. |
| 5 | ¿Contar plantas en una foto es un inventario? | Int. 1 | No. Demuestra la capacidad de detección. El inventario requiere recorrer la parcela con ID geolocalizado, que es la fase 1 del robot. |
| 6 | ¿De dónde sale el factor plantas→toneladas? | Int. 2 | No hay un valor publicado. Se declara como supuesto con una banda mínimo-base-máximo y el IPO se muestra con esa banda. `[fuente o nota]`. |
| 7 | Tu IPO, ¿no es solo supuestos? | Int. 2 | Parte de cifras oficiales (inventario, consumo industrial, exportaciones) y de supuestos explícitos, con escenarios y análisis de sensibilidad. El piloto sirve para calibrarlo. |
| 8 | ¿Por qué el IPO es regional y no por productor? | Int. 2 / Int. 3 | No hay datos públicos de inventario por municipio ni por productor. Los filtros municipales aplican al contexto (DENUE y Censo). |
| 9 | La ficha tiene confianza baja. ¿Por qué creerles a las cifras? | Int. 4 | Se reconoce: las cifras de precio vienen de prensa y organizaciones de productores. Se contrastaron con SADER y CRT, y la primera fase del piloto valida la línea base con datos oficiales. |
| 10 | ¿El CRT y el Gobierno ya hacen algo? | Int. 4 | Sí: plan federal, formalización y un visor del inventario. Atienden el precio después de la caída. No encontramos una herramienta pública que enfrente oferta madura y demanda para el pequeño productor. |
| 11 | ¿Quién lo pagaría o lo usaría? | Int. 4 | Cooperativas y organizaciones (Barzón Agavero, Grupo Cultural del Agave), tequileras micro y pequeñas, y SADER y CRT como indicador de alerta. |
| 12 | ¿Qué pasa con la privacidad de los productores? | Int. 3 | El diseño usa datos agregados, con anonimato y consentimiento. El aprendizaje federado queda documentado como arquitectura, no implementado en el MVP. |
| 13 | ¿Y el edge computing? | Int. 1 / Int. 3 | El modelo ligero corre en laptop con `[ms]` por imagen. El plan es pasarlo a un Jetson en la fase 1. |
| 14 | ¿Qué harían con 6 meses más? | Todos | Fase 1 y 2: carrito con cámara y GNSS en parcelas reales, dataset propio, calibración contra jima y piloto con 2-3 cooperativas. |
| 15 | ¿Se puede replicar en otros cultivos o regiones? | Int. 4 | Sí en la lógica: Guanajuato y Michoacán, agave mezcalero y cultivos de ciclo largo con auges y desplomes. Se dice como línea de crecimiento, no como resultado. |

## Reglas para responder
1. Si no se sabe, se dice: *"no lo medimos todavía, y así lo haríamos"*.
2. Nunca se afirma un resultado que no esté en los datos del proyecto.
3. Siempre se separa **lo que se demostró** de **lo que se propone**.
4. Respuestas de máximo 30 segundos y se pasa la palabra a quien más sabe.
