"""Gera dataset sintético didático (PET / lata / papelão) para testes do APS.

As imagens simulam silhuetas contrastadas em fundo claro, com ruído leve e
opcionalmente highlights — suficientes para validar o pipeline de PDI e o
classificador geométrico até a coleta de fotos reais.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from residuos_aps.config import RAW_DIR  # noqa: E402


CLASS_DIRS = {
    "PET": RAW_DIR / "pet",
    "Lata": RAW_DIR / "lata",
    "Papelao": RAW_DIR / "papelao",
}


def _bg(h: int, w: int, rng: np.random.Generator) -> np.ndarray:
    base = int(rng.integers(210, 245))
    img = np.full((h, w, 3), base, dtype=np.uint8)
    noise = rng.normal(0, 6, size=img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def _draw_pet(img: np.ndarray, rng: np.random.Generator) -> None:
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2
    body_w = int(rng.integers(55, 75))
    body_h = int(rng.integers(180, 230))
    color = (int(rng.integers(20, 60)), int(rng.integers(90, 140)), int(rng.integers(40, 90)))
    top = cy - body_h // 2
    bottom = cy + body_h // 2
    cv2.ellipse(img, (cx, cy + 10), (body_w, body_h // 2), 0, 0, 360, color, -1)
    neck_w = body_w // 3
    cv2.rectangle(img, (cx - neck_w, top - 35), (cx + neck_w, top + 20), color, -1)
    cv2.rectangle(img, (cx - neck_w - 4, top - 50), (cx + neck_w + 4, top - 30), (30, 30, 30), -1)
    # highlight
    cv2.circle(img, (cx - body_w // 3, cy), 8, (240, 240, 240), -1)


def _draw_lata(img: np.ndarray, rng: np.random.Generator) -> None:
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2
    rw = int(rng.integers(70, 95))
    rh = int(rng.integers(100, 130))
    color = (int(rng.integers(140, 180)), int(rng.integers(140, 180)), int(rng.integers(140, 180)))
    cv2.ellipse(img, (cx, cy), (rw, rh), 0, 0, 360, color, -1)
    cv2.ellipse(img, (cx, cy - rh + 8), (rw - 4, 18), 0, 0, 360, (200, 200, 200), -1)
    cv2.circle(img, (cx + rw // 3, cy - 10), 10, (250, 250, 250), -1)


def _draw_papelao(img: np.ndarray, rng: np.random.Generator) -> None:
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2
    bw = int(rng.integers(160, 220))
    bh = int(rng.integers(110, 150))
    color = (int(rng.integers(40, 70)), int(rng.integers(90, 130)), int(rng.integers(150, 190)))
    angle = float(rng.uniform(-12, 12))
    rect = ((cx, cy), (bw, bh), angle)
    box = cv2.boxPoints(rect).astype(np.int32)
    cv2.fillPoly(img, [box], color)
    # textura leve
    for _ in range(40):
        x = int(rng.integers(cx - bw // 2, cx + bw // 2))
        y = int(rng.integers(cy - bh // 2, cy + bh // 2))
        img[y, x] = np.clip(img[y, x].astype(np.int16) + rng.integers(-20, 20), 0, 255)


DRAWERS = {"PET": _draw_pet, "Lata": _draw_lata, "Papelao": _draw_papelao}


def generate(n_per_class: int = 12, seed: int = 42, size: tuple[int, int] = (480, 640)) -> list[dict]:
    rng = np.random.default_rng(seed)
    h, w = size
    manifest: list[dict] = []

    for label, folder in CLASS_DIRS.items():
        folder.mkdir(parents=True, exist_ok=True)
        # remove antigas sintéticas
        for old in folder.glob("synth_*.png"):
            old.unlink()

        for i in range(n_per_class):
            img = _bg(h, w, rng)
            DRAWERS[label](img, rng)
            # ruído impulsivo leve em 30% das imagens
            if rng.random() < 0.3:
                n_imp = int(rng.integers(20, 60))
                ys = rng.integers(0, h, n_imp)
                xs = rng.integers(0, w, n_imp)
                img[ys, xs] = 255 if rng.random() < 0.5 else 0

            name = f"synth_{label.lower()}_{i:02d}.png"
            path = folder / name
            cv2.imwrite(str(path), img)
            manifest.append({"path": str(path.relative_to(ROOT)), "label": label})

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera dataset sintético APS")
    parser.add_argument("--n", type=int, default=12, help="Imagens por classe")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    manifest = generate(n_per_class=args.n, seed=args.seed)
    out = ROOT / "data" / "manifest_synthetic.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Geradas {len(manifest)} imagens. Manifesto: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
