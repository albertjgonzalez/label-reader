# label-reader
Vision pipeline for industrial asset serialization. Detects and classifies barcodes, 2D codes, and text on asset labels at arbitrary orientations, producing oriented bounding boxes for downstream decoding and chain-of-custody records.

Built: seeded synthetic data generator (1000 labels, 5 symbologies, full 360° rotation and perspective warp with transform-tracked annotations), YOLO11n-OBB fine-tuned from DOTA weights. Results in docs/results.md.

In progress: decode ladder with escalating preprocessing, serial disambiguation and confidence scoring, C++ acceleration module, FastAPI service with SQLite audit log.
