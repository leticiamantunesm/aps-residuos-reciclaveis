"""Testes básicos de filtragem (úteis já na Fase Intermediária I)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from residuos_aps.preprocessing import apply_gaussian, apply_median, denoise
from residuos_aps.utils.errors import ValidationError


def _noise_image(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)


def test_gaussian_preserves_shape():
    img = _noise_image()
    out = apply_gaussian(img)
    assert out.shape == img.shape
    assert out.dtype == img.dtype


def test_median_preserves_shape():
    img = _noise_image(1)
    out = apply_median(img, ksize=3)
    assert out.shape == img.shape


def test_denoise_invalid_method():
    with pytest.raises(ValidationError):
        denoise(_noise_image(), method="bilateral")
