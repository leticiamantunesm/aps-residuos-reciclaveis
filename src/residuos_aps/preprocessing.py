"""Pré-processamento: redução de ruído (Gaussiano e Mediana)."""

from __future__ import annotations

import cv2
import numpy as np

from .config import GAUSSIAN_KSIZE, GAUSSIAN_SIGMA, MEDIAN_KSIZE
from .utils.errors import ValidationError


def _validate_odd_ksize(ksize: int, name: str) -> None:
    if ksize < 1 or ksize % 2 == 0:
        raise ValidationError(f"{name} deve ser ímpar e >= 1 (recebido: {ksize}).")


def apply_gaussian(
    image: np.ndarray,
    ksize: tuple[int, int] = GAUSSIAN_KSIZE,
    sigma: float = GAUSSIAN_SIGMA,
) -> np.ndarray:
    """
    Filtro Gaussiano (suavização linear).

    Aproxima a convolução com um kernel gaussiano 2D, atenuando ruído de alta
    frequência e preservando melhor bordas suaves do que uma média simples.
    """
    if image is None or image.size == 0:
        raise ValidationError("Imagem vazia em apply_gaussian.")
    kx, ky = ksize
    _validate_odd_ksize(kx, "ksize[0]")
    _validate_odd_ksize(ky, "ksize[1]")
    if sigma < 0:
        raise ValidationError("sigma deve ser >= 0.")
    return cv2.GaussianBlur(image, ksize, sigmaX=sigma)


def apply_median(image: np.ndarray, ksize: int = MEDIAN_KSIZE) -> np.ndarray:
    """
    Filtro da mediana (não linear).

    Eficaz contra ruído impulsivo ("sal e pimenta"), substituindo cada pixel
    pela mediana da vizinhança, o que preserva bordas melhor que o Gaussiano
    em muitos casos de ruído esparso.
    """
    if image is None or image.size == 0:
        raise ValidationError("Imagem vazia em apply_median.")
    _validate_odd_ksize(ksize, "ksize")
    return cv2.medianBlur(image, ksize)


def denoise(
    image: np.ndarray,
    method: str = "gaussian",
    *,
    gaussian_ksize: tuple[int, int] = GAUSSIAN_KSIZE,
    gaussian_sigma: float = GAUSSIAN_SIGMA,
    median_ksize: int = MEDIAN_KSIZE,
) -> np.ndarray:
    """Aplica o filtro escolhido: 'gaussian' ou 'median'."""
    method_norm = method.strip().lower()
    if method_norm == "gaussian":
        return apply_gaussian(image, ksize=gaussian_ksize, sigma=gaussian_sigma)
    if method_norm == "median":
        return apply_median(image, ksize=median_ksize)
    raise ValidationError("method deve ser 'gaussian' ou 'median'.")
