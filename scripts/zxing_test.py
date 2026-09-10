import cv2
import zxingcpp
from pipeline.detect import load_gt
import math
import numpy as np

def crop_quad(quad):
    x_min = min(point[0] for point in quad)
    x_max = max(point[0] for point in quad)
    y_min = min(point[1] for point in quad)
    y_max = max(point[1] for point in quad)
    return (int(x_min), int(y_min), int(x_max), int(y_max))

def dewarp_quad(image, quad):
    w = int(math.hypot(quad[1][0] - quad[0][0], quad[1][1] - quad[0][1]))
    h = int(math.hypot(quad[2][0] - quad[1][0], quad[2][1] - quad[1][1]))
    dst_points = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(np.array(quad, dtype=np.float32), dst_points)
    dewarped_image = cv2.warpPerspective(image, M, (w, h))

    return dewarped_image

def read_barcode(image_path):
    image = cv2.imread(image_path)
    detection = load_gt(image_path)
    for detection in detection:
        # x1, y1, x2, y2 = dewarp_quad(image, detection.quad)
        # crop = dewarp_quad(image, detection.quad)
        #print(detection.symbology, (x1, y1, x2, y2), crop.shape)
        dewarp = dewarp_quad(image, detection.quad)
        if dewarp.size == 0:
            continue
        results = zxingcpp.read_barcodes(dewarp)
        print(detection.symbology, "->", results)
        for r in results:
            print("   ", r.text, r.format, r.valid, r.position)
    return

if __name__ == "__main__":
    for i in range(20):
        read_barcode(f"data/test/images/test_{i:05d}.png")