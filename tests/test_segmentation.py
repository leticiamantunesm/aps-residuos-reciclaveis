"""Testes de segmentação e morfologia."""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from residuos_aps.morphology import refine_mask
from residuos_aps.segmentation import segment, threshold_otsu, to_gray


def test_to_gray_and_otsu_on_bimodal():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :] = (240, 240, 240)
    cv2.rectangle(img, (25, 25), (75, 75), (20, 20, 20), -1)
    gray = to_gray(img)
    binary, t = threshold_otsu(gray)
    assert 0 < t < 255
    assert binary.shape == gray.shape
    # objeto escuro deve virar 0 ou 1 dependendo da polaridade; há massa nos dois lados
    assert binary.min() == 0 and binary.max() == 255


def test_segment_and_refine():
    img = np.full((120, 120, 3), 220, dtype=np.uint8)
    cv2.circle(img, (60, 60), 35, (30, 30, 30), -1)
    # buraco interno
    cv2.circle(img, (60, 60), 8, (220, 220, 220), -1)
    seg = segment(img, method="otsu")
    refined = refine_mask(seg["binary"])
    assert refined.shape == seg["binary"].shape
