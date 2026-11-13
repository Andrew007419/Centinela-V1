import argparse
import json
import math
import platform
import statistics
from pathlib import Path
from importlib.metadata import version
from vision.src.inferencia import detectar

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--carpeta', default='vision/samples')
    a = p.parse_args()
    fotos = sorted(x for x in Path(a.carpeta).rglob('*')
                   if x.suffix.lower() in ['.jpg', '.jpeg', '.png'])
    if not fotos:
        raise ValueError('No hay imágenes para medir')
    for i in range(5):
        detectar(str(fotos[i % len(fotos)]))
    tiempos = [detectar(str(fotos[i % len(fotos)]))['tiempo_ms'] for i in range(max(30, len(fotos)))]
    r = {'mediana_ms': statistics.median(tiempos),
         'p95_ms': sorted(tiempos)[math.ceil(.95*len(tiempos))-1],
         'muestras': len(tiempos), 'imagenes_distintas': len(fotos),
         'device': 'cpu', 'sistema': platform.platform(), 'cpu': platform.processor(),
         'python': platform.python_version(), 'ultralytics': version('ultralytics'),
         'conf': .25, 'imgsz': 640,
         'alcance': 'predict; excluye carga de pesos, lectura y escritura; repite si hay menos de 30 fotos'}
    salida = Path('vision/evidencias/latencia_local.json')
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(r, indent=2), encoding='utf-8')
    print(json.dumps(r, indent=2))

if __name__ == '__main__':
    main()
