from dataclasses import dataclass

@dataclass
class Detection:
    quad: list[tuple[float, float]]
    symbology: str
    confidence: float
    source: str