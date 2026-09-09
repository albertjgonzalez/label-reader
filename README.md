# label-reader
<<<<<<< HEAD
Vision pipeline for industrial asset serialization. Detects and classifies barcodes, 2D codes, and text on asset labels at arbitrary orientations, producing oriented bounding boxes for downstream decoding and chain-of-custody records.

Built: seeded synthetic data generator (1000 labels, 5 symbologies, full 360° rotation and perspective warp with transform-tracked annotations), YOLO11n-OBB fine-tuned from DOTA weights. Results in docs/results.md.

In progress: decode ladder with escalating preprocessing, serial disambiguation and confidence scoring, C++ acceleration module, FastAPI service with SQLite audit log.
=======

<<<<<<< HEAD
Vision pipeline for industrial asset serialization: detects and classifies barcodes, 2D codes, and text on asset labels at arbitrary orientations, producing the oriented boxes and audit records that chain-of-custody compliance depends on.

Built so far: a seeded synthetic data generator (1000 labels, five symbologies, full 360° rotation and perspective warp with transform-tracked annotations) and a fine-tuned YOLO11n-OBB detector — [results and analysis](docs/results.md). In progress: decode ladder, serial disambiguation with confidence scoring, C++ acceleration, and a FastAPI service with an append-only decision log.
>>>>>>> 0e7701f (updated readme)
=======
A machine learning pipeline that reads label images, detecting and classifying barcodes, 2D codes, and printed text at various orientations.
>>>>>>> 41d50c5 (readme)
