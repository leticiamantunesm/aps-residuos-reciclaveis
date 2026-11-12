"""Avalia o pipeline no dataset (sintético ou real) e exporta métricas/mosaicos."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from residuos_aps.config import RAW_DIR, RESULTS_DIR  # noqa: E402
from residuos_aps.pipeline import run_pipeline  # noqa: E402
from residuos_aps.utils.errors import PipelineError  # noqa: E402
from residuos_aps.visualization import save_mosaic  # noqa: E402

LABEL_FROM_FOLDER = {"pet": "PET", "lata": "Lata", "papelao": "Papelao"}


def discover_images() -> list[tuple[Path, str]]:
    items: list[tuple[Path, str]] = []
    for folder_name, label in LABEL_FROM_FOLDER.items():
        folder = RAW_DIR / folder_name
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*")):
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
                items.append((path, label))
    return items


def confusion_matrix(pairs: list[tuple[str, str]], labels: list[str]) -> dict[str, dict[str, int]]:
    matrix = {t: {p: 0 for p in labels} for t in labels}
    for true, pred in pairs:
        if true in matrix and pred in matrix[true]:
            matrix[true][pred] += 1
    return matrix


def main() -> int:
    parser = argparse.ArgumentParser(description="Avalia dataset APS")
    parser.add_argument("--denoise", default="gaussian", choices=["gaussian", "median"])
    parser.add_argument("--threshold", default="otsu", choices=["otsu", "adaptive"])
    parser.add_argument("--mosaic-per-class", type=int, default=2)
    args = parser.parse_args()

    images = discover_images()
    if not images:
        print("Nenhuma imagem em data/raw/{pet,lata,papelao}", file=sys.stderr)
        return 1

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = RESULTS_DIR / f"eval_{args.denoise}_{args.threshold}"
    out_dir.mkdir(parents=True, exist_ok=True)
    mosaic_dir = out_dir / "mosaicos"
    mosaic_dir.mkdir(exist_ok=True)

    rows: list[dict] = []
    pairs: list[tuple[str, str]] = []
    no_contour = 0
    mosaics_saved = Counter()

    for path, true_label in images:
        try:
            result = run_pipeline(
                path,
                denoise_method=args.denoise,
                threshold_method=args.threshold,
            )
        except PipelineError as exc:
            rows.append(
                {
                    "file": path.name,
                    "true": true_label,
                    "pred": "ERRO",
                    "confidence": 0.0,
                    "ok": False,
                    "error": str(exc),
                }
            )
            continue

        if result.prediction is None:
            no_contour += 1
            pred = "SEM_CONTORNO"
            conf = 0.0
            ok = False
        else:
            pred = result.prediction["label"]
            conf = float(result.prediction["confidence"])
            ok = pred == true_label
            pairs.append((true_label, pred))

        rows.append(
            {
                "file": path.name,
                "true": true_label,
                "pred": pred,
                "confidence": conf,
                "ok": ok,
                "error": "",
                **(result.feature_values or {}),
            }
        )

        if mosaics_saved[true_label] < args.mosaic_per_class:
            save_mosaic(
                result,
                mosaic_dir / f"{true_label}_{path.stem}.png",
                title=f"{true_label} → {pred}",
            )
            mosaics_saved[true_label] += 1

    labels = ["PET", "Lata", "Papelao"]
    matrix = confusion_matrix(pairs, labels)
    n_classifiable = len(pairs)
    n_correct = sum(1 for t, p in pairs if t == p)
    accuracy = (n_correct / n_classifiable) if n_classifiable else 0.0

    summary = {
        "denoise": args.denoise,
        "threshold": args.threshold,
        "total_images": len(images),
        "classifiable": n_classifiable,
        "no_contour": no_contour,
        "accuracy_among_classifiable": round(accuracy, 4),
        "confusion_matrix": matrix,
        "per_class_support": dict(Counter(label for _, label in images)),
    }

    csv_path = out_dir / "predictions.csv"
    fieldnames = sorted({k for row in rows for k in row.keys()})
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # também copia um resumo “latest” para o Cap. 4
    latest = RESULTS_DIR / "latest_summary.json"
    latest.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"CSV: {csv_path}")
    print(f"Mosaicos: {mosaic_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
