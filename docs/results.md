# Results

## Detection — YOLO11n-OBB, 60 epochs, imgsz 960

Fine-tuned from DOTA-pretrained weights on 800 synthetic images, validated on 150 held-out.

| Class | Instances | P | R | mAP50 | mAP50-95 |
|---|---|---|---|---|---|
| all | 447 | 0.998 | 1.000 | 0.995 | 0.967 |
| code128 | 86 | 0.996 | 1.000 | 0.995 | 0.983 |
| code39 | 99 | 0.996 | 1.000 | 0.995 | 0.984 |
| datamatrix | 83 | 1.000 | 1.000 | 0.995 | 0.983 |
| qr | 95 | 1.000 | 1.000 | 0.995 | 0.985 |
| text | 84 | 0.999 | 1.000 | 0.995 | 0.898 |

Inference: 16.5 ms/image on a T4 at 960px.

### Reading these numbers honestly

These are saturated, and that is a statement about the dataset more than the model. The
generator produces five symbology types at consistent scales with clean rendering; a
detector that scores 0.995 on its own generator's output has not been tested against real
photographs, real lighting, or the degradation a camera on a production machine would
introduce. Deliberate image degradation (glare, uneven illumination, JPEG artifacts) was
scoped out for time and would be the first thing added.

The one class that is not saturated is `text` at mAP50-95 0.898 against 0.983–0.985 for
the code classes. Recall is 1.000, so nothing is missed — the boxes are just looser. Text
blocks are thin rectangles where a few pixels of vertical error costs a large share of the
box area, while the same error on a square Data Matrix barely moves IoU. This has a
downstream consequence: Phase 3 crops from these boxes for OCR, and a loose crop on a thin
region is more likely to clip a character than a loose crop on a 2D code.

Classes are geometric, not semantic — the detector identifies what kind of code it sees,
not what the code means. Role assignment is deliberately a separate problem.
