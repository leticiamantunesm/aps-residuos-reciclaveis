# APS UNIP — Classificação e Segmentação de Resíduos Sólidos

Aplicação de Processamento Digital de Imagens (OpenCV) e Visão Computacional para apoiar a automação da coleta seletiva (PET, lata de alumínio e papelão).

**Disciplina:** Atividades Práticas Supervisionadas (5º/6º CC)  
**Integrante:** Letícia Mateus Antunes de Melo  
**Orientador:** Mario Quinello  
**GUI:** Streamlit  

## Estrutura

- `src/residuos_aps/` — pipeline modular de PDI (aquisição → classificação)
- `app/` — interface Streamlit e CLI
- `docs/relatorio/` — rascunhos do trabalho escrito (ABNT / manual APS)
- `data/` — imagens brutas, processadas e resultados

## Ambiente

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execução

```bash
# dataset sintético + avaliação
python scripts/generate_synthetic_dataset.py --n 12
python scripts/evaluate_dataset.py --denoise gaussian --threshold otsu

# testes
python -m pytest tests -q

# GUI
streamlit run app/gui_streamlit.py

# CLI
python app/cli.py --image data/raw/pet/synth_pet_00.png
```

## Formatação do relatório (manual APS)

- Fonte: Arial 12  
- Espaçamento: 1,5  
- Papel: A4  
- Margens esquerda/direita: **2,5 cm** (conforme manual da disciplina)
