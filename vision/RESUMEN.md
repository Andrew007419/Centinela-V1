# Resumen de visión
Se entrenó YOLOv8n para detectar agaves en imágenes aéreas públicas.
Se unificaron dos etiquetas de origen en una clase agave.
Se corrigieron 151 cruces por nombre de imagen entre splits.
Dataset final: 4143 train, 356 val y 147 test.
Se conservaron 302017 cajas; no representan plantas únicas.
Test comunicado: P=0.9674, R=0.9700, mAP50=0.9889, mAP50-95=0.5715.
Pesos guardados en Drive, corrida agave_v1-2.
Integración local, video y medición de laptop: pendientes de ejecutar.
Límite: no validado desde el robot ni para masa, azúcar o madurez.
