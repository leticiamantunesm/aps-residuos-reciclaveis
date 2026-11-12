"""Leitura/escrita segura de imagens e listagem de datasets locais."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .errors import ImageLoadError, ValidationError

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def ensure_dir(path: Path | str) -> Path:
    """Cria o diretório (e pais) se não existir; retorna Path resolvido."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def list_images(folder: Path | str) -> list[Path]:
    """Lista imagens recursivamente em `folder`, ordenadas por nome."""
    root = Path(folder)
    if not root.exists():
        raise ValidationError(f"Pasta não encontrada: {root}")
    files = [
        p
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return files


def save_image(path: Path | str, image: np.ndarray) -> Path:
    """Salva imagem BGR/gray; levanta ImageLoadError se a gravação falhar."""
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValidationError("Imagem inválida para gravação.")
    out = Path(path)
    ensure_dir(out.parent)
    ok = cv2.imwrite(str(out), image)
    if not ok:
        raise ImageLoadError(f"Não foi possível salvar a imagem em: {out}")
    return out
