"""Extração de características geométricas a partir de contornos."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np

from .config import MIN_CONTOUR_AREA
from .utils.errors import ValidationError


@dataclass
class ContourFeatures:
    area: float
    perimeter: float
    circularity: float
    aspect_ratio: float
    extent: float
    solidity: float

    def to_dict(self) -> dict:
        return asdict(self)


def find_main_contour(
    binary: np.ndarray,
    min_area: float = MIN_CONTOUR_AREA,
) -> np.ndarray | None:
    """Retorna o maior contorno acima de `min_area`, ou None."""
    if binary is None or binary.size == 0:
        raise ValidationError("Máscara vazia em find_main_contour.")
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    main = max(contours, key=cv2.contourArea)
    if cv2.contourArea(main) < min_area:
        return None
    return main


def extract_features(contour: np.ndarray) -> ContourFeatures:
    """Calcula descritores geométricos clássicos do contorno."""
    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    circularity = 0.0 if perimeter == 0 else float(4.0 * np.pi * area / (perimeter**2))

    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = float(w) / float(h) if h > 0 else 0.0
    rect_area = float(w * h)
    extent = float(area / rect_area) if rect_area > 0 else 0.0

    hull = cv2.convexHull(contour)
    hull_area = float(cv2.contourArea(hull))
    solidity = float(area / hull_area) if hull_area > 0 else 0.0

    return ContourFeatures(
        area=area,
        perimeter=perimeter,
        circularity=circularity,
        aspect_ratio=aspect_ratio,
        extent=extent,
        solidity=solidity,
    )
