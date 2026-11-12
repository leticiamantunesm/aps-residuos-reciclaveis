"""Interface Streamlit para demonstração didática do pipeline APS."""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

# Garante import do pacote local sem instalação editable obrigatória
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from residuos_aps.pipeline import run_pipeline  # noqa: E402
from residuos_aps.utils.errors import PipelineError  # noqa: E402
from residuos_aps.visualization import make_mosaic  # noqa: E402

st.set_page_config(
    page_title="APS Resíduos Recicláveis",
    page_icon="♻️",
    layout="wide",
)

st.title("Classificação e Segmentação de Resíduos Sólidos")
st.caption(
    "APS UNIP — PDI/Visão Computacional | Integrante: Letícia Mateus Antunes de Melo "
    "| Orientador: Mario Quinello"
)

with st.sidebar:
    st.header("Parâmetros do pipeline")
    denoise_method = st.selectbox("Filtro", ["gaussian", "median"], index=0)
    threshold_method = st.selectbox("Segmentação", ["otsu", "adaptive"], index=0)
    max_side = st.slider("Maior lado (px)", 256, 1280, 640, 64)
    morph_ksize = st.select_slider("Kernel morfológico", options=[3, 5, 7, 9], value=5)
    morph_iterations = st.slider("Iterações morfológicas", 1, 5, 1)

uploaded = st.file_uploader(
    "Carregar imagem (PET, lata ou papelão)",
    type=["jpg", "jpeg", "png", "bmp", "webp"],
)

if uploaded is None:
    st.info("Envie uma imagem para executar o pipeline passo a passo.")
    st.stop()

file_bytes = np.frombuffer(uploaded.read(), dtype=np.uint8)
bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
if bgr is None:
    st.error("Não foi possível decodificar a imagem enviada.")
    st.stop()

try:
    result = run_pipeline(
        bgr,
        max_side=max_side,
        denoise_method=denoise_method,
        threshold_method=threshold_method,
        morph_ksize=morph_ksize,
        morph_iterations=morph_iterations,
    )
except PipelineError as exc:
    st.error(f"Falha no pipeline: {exc}")
    st.stop()

col_a, col_b = st.columns([2, 1])
with col_a:
    st.subheader("Etapas do processamento")
    fig = make_mosaic(result)
    st.pyplot(fig, clear_figure=True)

with col_b:
    st.subheader("Diagnóstico")
    if result.prediction is None:
        st.warning("Nenhum contorno válido encontrado. Ajuste filtro/limiar/morfologia.")
    else:
        st.metric("Classe prevista", result.prediction["label"])
        st.metric("Confiança (heurística)", f"{result.prediction['confidence']:.2f}")
        st.write(result.prediction["rationale"])
    if result.feature_values:
        st.json(result.feature_values)
    st.caption(
        f"Método: {result.meta.get('threshold_method')} | "
        f"Otsu T={result.meta.get('otsu_threshold')}"
    )
