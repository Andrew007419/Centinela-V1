from pathlib import Path
import argparse
from ultralytics import YOLO

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', required=True)
    p.add_argument('--project', default='vision/runs')
    p.add_argument('--device', default='cpu')
    p.add_argument('--epochs', type=int, default=60)
    p.add_argument('--batch', type=int, default=8)
    a = p.parse_args()
    if not Path(a.data).is_file():
        raise FileNotFoundError(a.data)
    YOLO('yolov8n.pt').train(data=str(Path(a.data).resolve()), epochs=a.epochs,
        imgsz=640, batch=a.batch, device=a.device, seed=42, workers=0,
        patience=15, project=a.project, name='agave_v1', exist_ok=False)

if __name__ == '__main__':
    main()
