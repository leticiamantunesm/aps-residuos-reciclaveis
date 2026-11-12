"""Orquestra o pipeline completo de PDI e classificação."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from . import acquisition, classifier, features, morphology, preprocessing, segmentation
from .utils.errors import PipelineError


@dataclass
class PipelineResult:
    original: np.ndarray
    filtered: np.ndarray
    gray: np.ndarray
    binary: np.ndarray
    refined: np.ndarray
    contour: np.ndarray | None
    feature_values: dict[str, float] | None
    prediction: dict[str, Any] | None
    meta: dict[str, Any] = field(default_factory=dict)


def run_pipeline(
    image_or_path: str | Path | np.ndarray,
    *,
    max_side: int = 640,
    denoise_method: str = "gaussian",
    threshold_method: str = "otsu",
    morph_ksize: int = 5,
    morph_iterations: int = 1,
) -> PipelineResult:
    """
    Executa: aquisição → filtragem → segmentação → morfologia → features → classe.

    `image_or_path` pode ser caminho de arquivo ou array BGR já carregado.
    """
    try:
        if isinstance(image_or_path, (str, Path)):
            original = acquisition.acquire(image_or_path, max_side=max_side)
        else:
            original = acquisition.resize_keep_aspect(image_or_path, max_side=max_side)

        filtered = preprocessing.denoise(original, method=denoise_method)
        seg = segmentation.segment(filtered, method=threshold_method)
        refined = morphology.refine_mask(
            seg["binary"], ksize=morph_ksize, iterations=morph_iterations
        )

        contour = features.find_main_contour(refined)
        feature_values = None
        prediction = None
        if contour is not None:
            feats = features.extract_features(contour)
            feature_values = feats.to_dict()
            pred = classifier.classify_rules(feats)
            prediction = {
                "label": pred.label,
                "confidence": pred.confidence,
                "rationale": pred.rationale,
            }

        return PipelineResult(
            original=original,
            filtered=filtered,
            gray=seg["gray"],
            binary=seg["binary"],
            refined=refined,
            contour=contour,
            feature_values=feature_values,
            prediction=prediction,
            meta={
                "denoise_method": denoise_method,
                "threshold_method": threshold_method,
                "otsu_threshold": seg.get("otsu_threshold"),
            },
        )
    except Exception as exc:  # noqa: BLE001 — encapsula para a GUI
        raise PipelineError(str(exc)) from exc
