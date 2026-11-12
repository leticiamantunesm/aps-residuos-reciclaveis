"""Exceções tipadas do pipeline (facilita mensagens claras na GUI)."""


class PipelineError(Exception):
    """Erro genérico em qualquer etapa do pipeline."""


class ImageLoadError(PipelineError):
    """Falha ao carregar ou validar uma imagem de entrada."""


class ValidationError(PipelineError):
    """Parâmetro inválido (kernel, caminho, método de limiar etc.)."""
