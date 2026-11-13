"""Ejecutar desde la raíz: python -m vision.src.usar_modelo --help."""
import argparse
import json
from pathlib import Path
from vision.src.inferencia import detectar, procesar_video

def main():
    p = argparse.ArgumentParser(description='Detector local de agaves (CPU)')
    sub = p.add_subparsers(dest='modo', required=True)
    foto = sub.add_parser('imagen')
    foto.add_argument('--entrada', required=True)
    foto.add_argument('--conf', type=float, default=0.25)
    foto.add_argument('--json', default='vision/outputs/resultado_imagen.json')
    video = sub.add_parser('video')
    video.add_argument('--entrada', required=True)
    video.add_argument('--salida', default='vision/outputs/demo.mp4')
    a = p.parse_args()
    try:
        if a.modo == 'imagen':
            destino = Path(a.json).resolve()
            if destino == Path(a.entrada).resolve():
                raise ValueError('JSON y entrada deben ser distintos')
            r = detectar(a.entrada, conf=a.conf)
            assert r['conteo'] == len(r['detecciones'])
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding='utf-8')
            print(json.dumps(r, indent=2, ensure_ascii=False))
            print('JSON:', destino)
        else:
            r = procesar_video(a.entrada, a.salida)
            print(json.dumps({k:v for k,v in r.items() if k != 'conteo_por_cuadro'},
                             indent=2, ensure_ascii=False))
    except (ValueError, OSError) as error:
        p.exit(1, f'Error: {error}\n')

if __name__ == '__main__':
    main()
