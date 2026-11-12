"""Aquisição e redimensionamento de imagens de resíduos recicláveis."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .config import DEFAULT_MAX_SIDE
from .utils.errors import ImageLoadError, ValidationError


def load_image(path: Path | str) -> np.ndarray:
    """
    Carrega imagem em BGR (padrão OpenCV).

    Raises:
        ImageLoadError: caminho inexistente ou arquivo ilegível.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise ImageLoadError(f"Arquivo não encontrado: {file_path}")

    image = cv2.imread(str(file_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ImageLoadError(
            f"Falha ao decodificar a imagem (formato corrompido?): {file_path}"
        )
    return image


def resize_keep_aspect(image: np.ndarray, max_side: int = DEFAULT_MAX_SIDE) -> np.ndarray:
    """Redimensiona para que o maior lado seja `max_side`, preservando aspecto."""
    if image is None or image.size == 0:
        raise ValidationError("Imagem vazia em resize_keep_aspect.")
    if max_side < 16:
        raise ValidationError("max_side deve ser >= 16.")

    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_side:
        return image.copy()

    scale = max_side / float(longest)
    new_w = max(1, int(round(width * scale)))
    new_h = max(1, int(round(height * scale)))
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def acquire(path: Path | str, max_side: int = DEFAULT_MAX_SIDE) -> np.ndarray:
    """Atalho: carrega + redimensiona."""
    return resize_keep_aspect(load_image(path), max_side=max_side)
