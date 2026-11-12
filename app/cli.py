"""CLI simples para rodar o pipeline sem GUI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from residuos_aps.pipeline import run_pipeline
from residuos_aps.utils.errors import PipelineError
from residuos_aps.visualization import save_mosaic


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline APS — resíduos recicláveis")
    parser.add_argument("--image", required=True, help="Caminho da imagem de entrada")
    parser.add_argument(
        "--out",
        default=str(ROOT / "data" / "results" / "mosaico.png"),
        help="Caminho do mosaico de saída",
    )
    parser.add_argument("--denoise", default="gaussian", choices=["gaussian", "median"])
    parser.add_argument("--threshold", default="otsu", choices=["otsu", "adaptive"])
    args = parser.parse_args()

    try:
        result = run_pipeline(
            args.image,
            denoise_method=args.denoise,
            threshold_method=args.threshold,
        )
    except PipelineError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    out = save_mosaic(result, args.out)
    print(json.dumps({"out": str(out), "prediction": result.prediction}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
