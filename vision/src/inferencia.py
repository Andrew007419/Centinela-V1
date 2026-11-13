from pathlib import Path
from functools import lru_cache
from time import perf_counter
import json
import uuid
import cv2
from ultralytics import YOLO

VISION = Path(__file__).resolve().parents[1]
PESOS = VISION / 'models' / 'best.pt'
SALIDAS = VISION / 'outputs'

@lru_cache(maxsize=1)
def _modelo():
    if not PESOS.is_file():
        raise FileNotFoundError(f'Faltan pesos entrenados: {PESOS}')
    modelo = YOLO(str(PESOS))
    nombres = modelo.names
    if nombres != {0: 'agave'}:
        raise ValueError(f'Se espera clase única 0: agave; recibido: {nombres}')
    return modelo

def detectar(ruta_imagen: str, conf: float = 0.25) -> dict:
    if not 0 < conf < 1:
        raise ValueError('conf debe estar entre 0 y 1')
    imagen = cv2.imread(str(ruta_imagen))
    if imagen is None:
        raise ValueError(f'Imagen ilegible: {ruta_imagen}')
    modelo = _modelo()
    inicio = perf_counter()
    r = modelo.predict(imagen, conf=conf, iou=0.5, imgsz=640, device='cpu', verbose=False)[0]
    tiempo = (perf_counter() - inicio) * 1000
    detecciones = []
    for i, caja in enumerate(r.boxes, 1):
        detecciones.append({'id': i, 'bbox': [round(float(v), 2) for v in caja.xyxy[0].tolist()],
                            'confianza': round(float(caja.conf[0]), 6)})
    SALIDAS.mkdir(parents=True, exist_ok=True)
    salida = SALIDAS / f'{uuid.uuid4().hex}.jpg'
    anotada = imagen.copy()
    for d in detecciones:
        x1, y1, x2, y2 = map(int, d['bbox'])
        cv2.rectangle(anotada, (x1, y1), (x2, y2), (0, 255, 0), 1)
        etiqueta = str(d['id'])
        cv2.putText(anotada, etiqueta, (x1, max(12, y1-3)), cv2.FONT_HERSHEY_SIMPLEX, .4, (0,0,0), 3)
        cv2.putText(anotada, etiqueta, (x1, max(12, y1-3)), cv2.FONT_HERSHEY_SIMPLEX, .4, (255,255,255), 1)
    if not cv2.imwrite(str(salida), anotada):
        raise OSError(f'No se pudo guardar {salida}')
    return {'conteo': len(detecciones), 'detecciones': detecciones,
            'imagen_anotada': str(salida), 'tiempo_ms': round(tiempo, 3)}

def procesar_video(ruta_video, salida) -> dict:
    # Modelo nuevo por video: evita reutilizar el estado de otro seguimiento.
    _modelo()  # valida pesos y clases
    modelo = YOLO(str(PESOS))
    cap = cv2.VideoCapture(str(ruta_video))
    if not cap.isOpened():
        raise ValueError(f'Video ilegible: {ruta_video}')
    destino = Path(salida).resolve()
    if destino == Path(ruta_video).resolve():
        cap.release()
        raise ValueError('La salida debe ser distinta del video original')
    destino.parent.mkdir(parents=True, exist_ok=True)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        cap.release()
        raise ValueError('FPS desconocido; recodifica el video primero')
    w, h = int(cap.get(3)), int(cap.get(4))
    escritor = cv2.VideoWriter(str(destino), cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    if not escritor.isOpened():
        cap.release()
        raise OSError('No se pudo abrir el escritor MP4')
    registros, ids = [], set()
    inicio = perf_counter()
    try:
        while True:
            ok, cuadro = cap.read()
            if not ok:
                break
            r = modelo.track(cuadro, persist=True, tracker='bytetrack.yaml', conf=0.25,
                             iou=0.5, imgsz=640, device='cpu', verbose=False)[0]
            actuales = [] if r.boxes.id is None else [int(x) for x in r.boxes.id.tolist()]
            ids.update(actuales)
            registros.append({'cuadro': len(registros), 'conteo': len(r.boxes), 'ids': actuales})
            anotado = r.plot(conf=False, labels=True, line_width=1)
            cv2.putText(anotado, f'Agaves visibles: {len(r.boxes)}', (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            escritor.write(anotado)
    finally:
        cap.release()
        escritor.release()
    if not registros:
        raise ValueError('Video sin cuadros decodificables')
    segundos = perf_counter() - inicio
    resumen = {'conteo_por_cuadro': registros, 'video_anotado': str(destino),
               'ids_observados': len(ids), 'maximo_simultaneo': max(x['conteo'] for x in registros),
               'fps_proceso': len(registros) / segundos,
               'advertencia': 'IDs temporales; no equivalen a plantas únicas de parcela.'}
    destino.with_suffix('.json').write_text(json.dumps(resumen, indent=2), encoding='utf-8')
    return resumen
