"""Parâmetros globais do pipeline (caminhos, kernels e limiares)."""

from __future__ import annotations

from pathlib import Path

# Raiz do repositório: .../aps-residuos-reciclaveis
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = DATA_DIR / "results"

# Classes-alvo do classificador interpretável
CLASSES = ("PET", "Lata", "Papelao")

# Aquisição
DEFAULT_MAX_SIDE = 640  # redimensiona o maior lado, preservando aspecto

# Pré-processamento
GAUSSIAN_KSIZE = (5, 5)
GAUSSIAN_SIGMA = 1.2
MEDIAN_KSIZE = 5

# Segmentação: "otsu" | "adaptive"
DEFAULT_THRESHOLD_METHOD = "otsu"
ADAPTIVE_BLOCK_SIZE = 35  # ímpar
ADAPTIVE_C = 5

# Morfologia
MORPH_KERNEL_SIZE = 5
MORPH_ITERATIONS = 1

# Classificação (heurísticas iniciais — calibrar no Cap. 4)
MIN_CONTOUR_AREA = 500.0
