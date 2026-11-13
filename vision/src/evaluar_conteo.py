import argparse
import csv
import json
from pathlib import Path
from vision.src.inferencia import detectar

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', default='vision/samples/conteos.csv')
    a = p.parse_args()
    filas = []
    with open(a.csv, encoding='utf-8-sig', newline='') as f:
        for fila in csv.DictReader(f):
            real = int(fila['real'])
            if real < 0:
                raise ValueError('Conteo real negativo')
            pred = detectar(fila['ruta'])['conteo']
            filas.append({'ruta': fila['ruta'], 'real': real, 'predicho': pred, 'error': pred-real})
    if not filas:
        raise ValueError('CSV vacío')
    errores = [x['error'] for x in filas]
    r = {'n': len(filas), 'mae': sum(abs(x) for x in errores)/len(filas),
         'sesgo': sum(errores)/len(filas), 'error_maximo': max(abs(x) for x in errores),
         'imagenes_negativas': sum(x['real']==0 for x in filas), 'conf': .25, 'filas': filas}
    destino = Path('vision/evidencias/conteo.json')
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(r, indent=2), encoding='utf-8')
    print(json.dumps(r, indent=2))

if __name__ == '__main__':
    main()
