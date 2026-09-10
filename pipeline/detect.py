import json
from pathlib import Path
from ultralytics import YOLO

from pipeline.types import Detection
def load_gt(image_path) -> list[Detection]:
    p = Path(image_path)
    image_json = p.parent.parent / "labels" / p.with_suffix(".json").name
    detections = []
    data = json.loads(image_json.read_text())
    for detection in data:
        detections.append(
            Detection(
                quad=normalize_quad(detection["quad"]),
                symbology=detection["symbology"],
                confidence=1.0,
                source="gt",
            )
        )
    return detections

def detect(image_path, weights) -> list[Detection]:
    detections = []
    model = YOLO(weights)
    result = model.predict(image_path, verbose=False)[0]
    for quad, cls, conf in zip(
        result.obb.xyxyxyxy.tolist(),
        result.obb.cls.tolist(),
        result.obb.conf.tolist()
    ):
        detections.append(
            Detection(
                quad=normalize_quad(quad),
                symbology=model.names[int(cls)],
                confidence=conf,
                source="model",
            )
        )
    return detections

def normalize_quad(quad):
    if winding(quad) < 0:
        quad = quad[::-1]
    start = min(range(4), key=lambda i: quad[i][0] + quad[i][1])
    return quad[start:] + quad[:start]

def winding(quad):
    total = 0
    for i in range(4):
        x1, y1 = quad[i]
        x2, y2 = quad[(i + 1) % 4]
        total += x1 * y2 - x2 * y1
    return total
    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--source", choices=["gt", "model"], default="gt")
    parser.add_argument("--weights", default="models/best.pt")
    args = parser.parse_args()

    if args.source == "gt":
        results = load_gt(args.image)
    else:
        results = detect(args.image, args.weights)

    for d in results:
        print(d.source, d.symbology, round(d.confidence, 3), [[round(v, 1) for v in p] for p in d.quad])