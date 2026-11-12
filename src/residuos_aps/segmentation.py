"""Segmentação: escala de cinza e binarização (Otsu / adaptativa).

Implementação completa na Fase Intermediária II (após fundamentação teórica).
"""

from __future__ import annotations

import cv2
import numpy as np

from .config import ADAPTIVE_BLOCK_SIZE, ADAPTIVE_C, DEFAULT_THRESHOLD_METHOD
from .utils.errors import ValidationError


def to_gray(image: np.ndarray) -> np.ndarray:
    """Converte BGR para escala de cinza; se já for 2D, devolve cópia."""
    if image is None or image.size == 0:
        raise ValidationError("Imagem vazia em to_gray.")
    if image.ndim == 2:
        return image.copy()
    if image.ndim == 3 and image.shape[2] >= 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    raise ValidationError("Formato de imagem não suportado em to_gray.")


def ensure_object_white(binary: np.ndarray) -> np.ndarray:
    """
    Garante que o objeto seja branco (255) para findContours.

    Heurística: cantos da imagem tendem a ser fundo. Se os cantos forem claros,
    o objeto está escuro na máscara e a imagem é invertida.
    """
    if binary.ndim != 2:
        raise ValidationError("ensure_object_white espera máscara 2D.")
    h, w = binary.shape
    corners = [binary[0, 0], binary[0, w - 1], binary[h - 1, 0], binary[h - 1, w - 1]]
    if float(np.mean(corners)) > 127.0:
        return cv2.bitwise_not(binary)
    return binary


def threshold_otsu(gray: np.ndarray) -> tuple[np.ndarray, float]:
    """Binarização global pelo método de Otsu. Retorna (máscara, limiar)."""
    if gray.ndim != 2:
        raise ValidationError("threshold_otsu espera imagem em cinza.")
    thresh_value, binary = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return ensure_object_white(binary), float(thresh_value)


def threshold_adaptive(
    gray: np.ndarray,
    block_size: int = ADAPTIVE_BLOCK_SIZE,
    c: float = ADAPTIVE_C,
) -> np.ndarray:
    """Binarização adaptativa (média da vizinhança − C)."""
    if gray.ndim != 2:
        raise ValidationError("threshold_adaptive espera imagem em cinza.")
    if block_size < 3 or block_size % 2 == 0:
        raise ValidationError("block_size deve ser ímpar e >= 3.")
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        c,
    )
    return ensure_object_white(binary)


def segment(
    image: np.ndarray,
    method: str = DEFAULT_THRESHOLD_METHOD,
) -> dict:
    """
    Pipeline curto de segmentação.

    Returns:
        dict com chaves: gray, binary, method, otsu_threshold (se aplicável).
    """
    gray = to_gray(image)
    method_norm = method.strip().lower()
    meta: dict = {"method": method_norm, "otsu_threshold": None}

    if method_norm == "otsu":
        binary, t = threshold_otsu(gray)
        meta["otsu_threshold"] = t
    elif method_norm == "adaptive":
        binary = threshold_adaptive(gray)
    else:
        raise ValidationError("method deve ser 'otsu' ou 'adaptive'.")

    meta["gray"] = gray
    meta["binary"] = binary
    return meta
