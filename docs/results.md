# Results

## Detection — YOLO11n-OBB, 60 epochs, imgsz 960

Fine-tuned from DOTA weights. 800 train / 150 val, synthetic.

| Class | Instances | P | R | mAP50 | mAP50-95 |
|---|---|---|---|---|---|
| all | 447 | 0.998 | 1.000 | 0.995 | 0.967 |
| code128 | 86 | 0.996 | 1.000 | 0.995 | 0.983 |
| code39 | 99 | 0.996 | 1.000 | 0.995 | 0.984 |
| datamatrix | 83 | 1.000 | 1.000 | 0.995 | 0.983 |
| qr | 95 | 1.000 | 1.000 | 0.995 | 0.985 |
| text | 84 | 0.999 | 1.000 | 0.995 | 0.898 |

16.5 ms/image on a T4 at 960px.

## Notes

Numbers are saturated because the test set is my own generator's output — clean
rendering, consistent scale, no camera. Degradation (glare, uneven light, JPEG) was
cut for time. That's the first thing to add.

`text` is the weak class at 0.898 mAP50-95. Recall is 1.0 so nothing is missed, the
boxes are just loose. Text blocks are thin, so a few pixels of vertical error eats a
lot of IoU; the same error on a square Data Matrix barely registers. Matters later —
Phase 3 crops these boxes for OCR and a loose crop on a thin box clips characters.

Classes are geometric, not semantic. Role assignment happens in Phase 3.
