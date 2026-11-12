"""Testes de integração com imagens sintéticas mínimas (sem depender do dataset)."""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from residuos_aps.pipeline import run_pipeline


def _synthetic_can() -> np.ndarray:
    img = np.full((320, 320, 3), 230, dtype=np.uint8)
    cv2.ellipse(img, (160, 160), (70, 95), 0, 0, 360, (160, 160, 160), -1)
    return img


def test_pipeline_finds_contour_and_label():
    result = run_pipeline(_synthetic_can(), denoise_method="gaussian", threshold_method="otsu")
    assert result.contour is not None
    assert result.feature_values is not None
    assert result.prediction is not None
    assert result.prediction["label"] in {"PET", "Lata", "Papelao"}


def test_pipeline_median_adaptive_runs():
    result = run_pipeline(_synthetic_can(), denoise_method="median", threshold_method="adaptive")
    assert result.binary is not None
    assert result.refined.shape == result.binary.shape
