# Resultados de visión

Resultados comunicados por el responsable tras evaluación en test de 147 imágenes:

| Métrica | Valor |
|---|---:|
| Precisión | 0.9674 |
| Recall | 0.9700 |
| mAP50 | 0.9889 |
| mAP50-95 | 0.5715 |

Modelo base YOLOv8n, clase agave. Corrida: agave_v1-2.
Pesos Drive: CENTINELA_AGAVE/vision/runs/agave_v1-2/weights/best.pt.
Configuración solicitada: epochs=60, imgsz=640, batch=8, seed=42, patience=15. Verificar ejecución real y épocas alcanzadas en args.yaml/results.csv.
Inferencia local del código: CPU, imgsz=640, conf=0.25, iou=0.5.
P/R del evaluador no se interpretan automáticamente como P/R al umbral operativo.

Velocidad comunicada en Colab: preprocess 0.7 ms, inference 3.1 ms, postprocess 2.3 ms por imagen. Es un resumen de aquella ejecución; GPU exacta pendiente de registrar. No es latencia local ni FPS de video.

Limitaciones: vistas aéreas; agrupación por nombre, no por parcela completa; posible similitud entre splits. No se ha validado cámara terrestre, salud, masa, azúcar o madurez.

