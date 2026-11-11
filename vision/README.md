# Visión · Integrante 1

**Rama:** `vision/...`
**Meta:** un modelo YOLOv8 que detecta y cuenta plantas de agave, con métricas honestas y un clip real corriendo.

## Entregables

| # | Entregable | Ruta |
|---|---|---|
| 1 | Dataset de 200 a 500 imágenes anotadas | Drive (enlace en `docs/ENLACES.md`) |
| 2 | Descripción del dataset: fuentes, licencias, cantidades y división | `vision/DATASET.md` |
| 3 | Script de entrenamiento reproducible | `vision/src/entrenar.py` |
| 4 | Métricas en datos de prueba no vistos | `vision/METRICAS.md` |
| 5 | Función de inferencia (ver contrato) | `vision/src/inferencia.py` |
| 6 | Pesos del modelo | `vision/models/best.pt` (o Drive) |
| 7 | Clip real del modelo corriendo | Drive |
| 8 | Resumen de 10 líneas | `vision/RESUMEN.md` |

## Paso a paso

### 1. Dataset (día 1)
- Fuentes: fotos y videos propios (lo ideal), imágenes de dron si hay acceso y datasets públicos de agave (Roboflow Universe, Kaggle). **Anota la licencia de cada fuente.**
- Si usas video: extrae un cuadro cada 1-2 segundos para no repetir imágenes casi idénticas.
- Clase única: `agave`.
- Herramientas de anotación: Roboflow, CVAT o LabelImg. Formato de salida: YOLO.
- Variedad: distintas horas, ángulos, distancias, parcelas y fondos.

### 2. División de datos (importante)
Divide en entrenamiento (70%), validación (20%) y prueba (10%).
**La división debe hacerse por video o por parcela, no por imagen.** Si cuadros casi idénticos del mismo video quedan en entrenamiento y en prueba, las métricas salen infladas y no valen. El conjunto de prueba **no se toca** hasta el final.

### 3. Entrenamiento (día 2)
```bash
pip install -r vision/requirements.txt
```
```python
from ultralytics import YOLO
modelo = YOLO("yolov8n.pt")        # empezar con el modelo pequeño (rápido en laptop)
modelo.train(data="vision/data/agave.yaml", epochs=60, imgsz=640, seed=42)
```
Si tu computadora es lenta, usa Google Colab con GPU. Prueba también `yolov8s.pt` y compara.

### 4. Evaluación (día 3)
Evalúa **solo una vez** en el conjunto de prueba y reporta:
- Precisión, recall, mAP@0.5 y mAP@0.5:0.95.
- Matriz de confusión o ejemplos de aciertos y errores.
- Casos donde falla (sombras, plantas juntas, maleza, plantas pequeñas) y por qué.

Reporta las cifras **tal como salgan**. No hay que presumir métricas altas: el jurado valora más una evaluación honesta.

### 5. Inferencia y conteo (día 3)
Implementa `detectar()` y `procesar_video()` con el formato de `docs/03_CONTRATOS_ENTRE_ROLES.md`. Prueba con imágenes que no estén en el dataset.

### 6. Clip real (día 3-4)
Graba la pantalla del modelo corriendo sobre un video real, con las cajas y el conteo. Graba **dos versiones** y guarda la mejor como respaldo.

### 7. Edge computing
Mide el tiempo de inferencia por imagen en tu laptop (en milisegundos) y reporta el dato. Es la evidencia de que el modelo ligero corre en el borde. Documenta cómo se pasaría a un Jetson.

## Límites del MVP
- Solo detecta y cuenta plantas. **No** estima masa, azúcares ni madurez.
- Un conteo por imagen no es un inventario de parcela. Dilo tal cual.

## Criterio de terminado
- [ ] Métricas en test no visto, con la división por video o parcela explicada
- [ ] `detectar()` devuelve exactamente el formato del contrato
- [ ] Un colega pudo reproducir el entrenamiento siguiendo este README
- [ ] Clip real y respaldo guardados en Drive
- [ ] `DATASET.md`, `METRICAS.md` y `RESUMEN.md` escritos
