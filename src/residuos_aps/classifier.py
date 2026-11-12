"""Classificador interpretável por regras sobre descritores geométricos.

Heurísticas calibradas no dataset sintético (Cap. 4) e ajustáveis com fotos reais:
- Lata: alta circularidade
- PET: silhueta alongada (max(w/h, h/w) elevado)
- Papelão: circularidade moderada/baixa e boa ocupação do bounding box
"""

from __future__ import annotations

from dataclasses import dataclass

from .features import ContourFeatures
from .utils.errors import ValidationError


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    rationale: str


def _elongation(aspect_ratio: float) -> float:
    """Razão do lado maior pelo menor (>= 1)."""
    if aspect_ratio <= 0:
        return 1.0
    return max(aspect_ratio, 1.0 / aspect_ratio)


def classify_rules(features: ContourFeatures) -> ClassificationResult:
    """Atribui PET | Lata | Papelao com base em limiares geométricos."""
    if features is None:
        raise ValidationError("Features ausentes para classificação.")

    circ = float(features.circularity)
    extent = float(features.extent)
    elong = _elongation(float(features.aspect_ratio))

    # Escores em [0, 1] — limiares iniciais documentados no Cap. 4
    score_lata = max(0.0, min(1.0, (circ - 0.75) / 0.25))
    score_pet = max(0.0, min(1.0, (elong - 1.35) / 0.90))
    score_papelao = max(0.0, min(1.0, (0.78 - circ) / 0.25)) * max(extent, 0.5)

    scores = {"PET": score_pet, "Lata": score_lata, "Papelao": score_papelao}
    label = max(scores, key=scores.get)
    confidence = float(scores[label])
    rationale = (
        f"circularidade={circ:.3f}, aspect_ratio={features.aspect_ratio:.3f}, "
        f"elongation={elong:.3f}, extent={extent:.3f} → {label} "
        f"(scores PET={score_pet:.2f}, Lata={score_lata:.2f}, Papelao={score_papelao:.2f})"
    )
    return ClassificationResult(label=label, confidence=confidence, rationale=rationale)
