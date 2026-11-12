"""Operações morfológicas para refinar a máscara binária."""

from __future__ import annotations

import cv2
import numpy as np

from .config import MORPH_ITERATIONS, MORPH_KERNEL_SIZE
from .utils.errors import ValidationError


def _kernel(size: int = MORPH_KERNEL_SIZE) -> np.ndarray:
    if size < 1 or size % 2 == 0:
        raise ValidationError("Tamanho do kernel morfológico deve ser ímpar >= 1.")
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))


def dilate(
    binary: np.ndarray,
    ksize: int = MORPH_KERNEL_SIZE,
    iterations: int = MORPH_ITERATIONS,
) -> np.ndarray:
    """Dilatação: expande regiões brancas (fecha pequenos buracos externos)."""
    return cv2.dilate(binary, _kernel(ksize), iterations=iterations)


def erode(
    binary: np.ndarray,
    ksize: int = MORPH_KERNEL_SIZE,
    iterations: int = MORPH_ITERATIONS,
) -> np.ndarray:
    """Erosão: contrai regiões brancas (remove ruído pontual)."""
    return cv2.erode(binary, _kernel(ksize), iterations=iterations)


def close(
    binary: np.ndarray,
    ksize: int = MORPH_KERNEL_SIZE,
    iterations: int = MORPH_ITERATIONS,
) -> np.ndarray:
    """Fechamento = dilatação seguida de erosão (fecha buracos no objeto)."""
    return cv2.morphologyEx(
        binary, cv2.MORPH_CLOSE, _kernel(ksize), iterations=iterations
    )


def open_(
    binary: np.ndarray,
    ksize: int = MORPH_KERNEL_SIZE,
    iterations: int = MORPH_ITERATIONS,
) -> np.ndarray:
    """Abertura = erosão seguida de dilatação (remove pequenos artefatos)."""
    return cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, _kernel(ksize), iterations=iterations
    )


def refine_mask(
    binary: np.ndarray,
    ksize: int = MORPH_KERNEL_SIZE,
    iterations: int = MORPH_ITERATIONS,
) -> np.ndarray:
    """Sequência didática padrão: abertura (ruído) + fechamento (buracos)."""
    if binary is None or binary.size == 0:
        raise ValidationError("Máscara vazia em refine_mask.")
    cleaned = open_(binary, ksize=ksize, iterations=iterations)
    return close(cleaned, ksize=ksize, iterations=iterations)
