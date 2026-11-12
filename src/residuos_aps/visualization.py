"""Visualizações Matplotlib (mosaicos antes/depois para o relatório)."""

from __future__ import annotations

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

from .pipeline import PipelineResult
from .utils.io import ensure_dir


def _bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def make_mosaic(result: PipelineResult, title: str | None = None) -> plt.Figure:
    """Monta figura 2×3 com as etapas principais do pipeline."""
    overlay = result.original.copy()
    if result.contour is not None:
        cv2.drawContours(overlay, [result.contour], -1, (0, 255, 0), 2)

    panels = [
        (_bgr_to_rgb(result.original), "Original"),
        (_bgr_to_rgb(result.filtered), "Filtrada"),
        (result.gray, "Cinza"),
        (result.binary, "Binária"),
        (result.refined, "Morfologia"),
        (_bgr_to_rgb(overlay), "Contorno / classe"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    for ax, (img, label) in zip(axes.ravel(), panels):
        cmap = "gray" if img.ndim == 2 else None
        ax.imshow(img, cmap=cmap)
        ax.set_title(label)
        ax.axis("off")

    pred = result.prediction or {}
    subtitle = title or "Pipeline PDI — resíduos recicláveis"
    if pred:
        subtitle += f" | {pred.get('label')} ({pred.get('confidence', 0):.2f})"
    fig.suptitle(subtitle)
    fig.tight_layout()
    return fig


def save_mosaic(result: PipelineResult, path: str | Path, **kwargs) -> Path:
    """Salva o mosaico em disco (PNG recomendado para o Cap. 4)."""
    out = Path(path)
    ensure_dir(out.parent)
    fig = make_mosaic(result, **kwargs)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out
