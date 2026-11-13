from pathlib import Path
import hashlib
import argparse
import yaml
from PIL import Image

def main():
    p = argparse.ArgumentParser()
    p.add_argument('yaml')
    a = p.parse_args()
    archivo = Path(a.yaml).resolve()
    cfg = yaml.safe_load(archivo.read_text())
    assert cfg['names'] in ({0: 'agave'}, ['agave']), 'Clase incorrecta'
    raiz = Path(cfg.get('path', archivo.parent))
    if not raiz.is_absolute():
        raiz = archivo.parent / raiz
    hashes = {}
    for split in ['train', 'val', 'test']:
        carpeta = raiz / cfg[split]
        assert carpeta.is_dir(), f'Falta {carpeta}'
        imagenes = sorted(x for x in carpeta.rglob('*') if x.suffix.lower() in ['.jpg','.jpeg','.png'])
        assert imagenes, f'Split vacío: {split}'
        cajas = 0
        for im in imagenes:
            with Image.open(im) as img:
                img.verify()
            firma = hashlib.sha256(im.read_bytes()).hexdigest()
            assert firma not in hashes, f'Duplicado: {im} / {hashes.get(firma)}'
            hashes[firma] = str(im)
            rel = im.relative_to(carpeta).with_suffix('.txt')
            partes = list(carpeta.parts)
            assert 'images' in partes, f'Ruta sin images: {carpeta}'
            partes[len(partes)-1-partes[::-1].index('images')] = 'labels'
            etiqueta = Path(*partes) / rel
            assert etiqueta.is_file(), f'Falta etiqueta: {etiqueta}; usa TXT vacío si es negativo revisado'
            for linea in etiqueta.read_text().splitlines():
                v = [float(x) for x in linea.split()]
                assert len(v) == 5 and v[0] == 0, f'Etiqueta inválida: {etiqueta}'
                _, x, y, w, h = v
                assert 0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1
                assert x-w/2 >= -0.001 and x+w/2 <= 1.001 and y-h/2 >= -0.001 and y+h/2 <= 1.001
                cajas += 1
        print(split, 'imágenes:', len(imagenes), 'cajas:', cajas)
    print('OK estructural. Revisar manualmente grupos, licencias y duplicados visuales.')

if __name__ == '__main__':
    main()
