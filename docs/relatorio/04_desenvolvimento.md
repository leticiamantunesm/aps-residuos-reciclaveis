# 4 DESENVOLVIMENTO

**Identificação**  
Integrante: Letícia Mateus Antunes de Melo  
Orientador: Mario Quinello  

---

## 4.1 Ferramentas utilizadas

| Ferramenta | Função no projeto |
|------------|-------------------|
| Python 3.10+ (ambiente local 3.14) | Linguagem principal |
| OpenCV (`opencv-python`) | Aquisição, filtros, limiar, morfologia, contornos |
| NumPy | Arrays e operações numéricas |
| Matplotlib | Mosaicos “antes/depois” para o relatório |
| Streamlit | Interface gráfica de demonstração |
| pytest | Testes unitários e de integração |
| Git | Versionamento do código e da documentação |

Ambiente reproduzível via `requirements.txt` e *virtualenv* (`.venv`). A execução típica é:

```text
pip install -r requirements.txt
python scripts/generate_synthetic_dataset.py --n 12
python scripts/evaluate_dataset.py --denoise gaussian --threshold otsu
streamlit run app/gui_streamlit.py
```

## 4.2 Arquitetura do software

O sistema segue arquitetura modular em camadas:

1. **Núcleo científico** (`src/residuos_aps/`): `acquisition`, `preprocessing`, `segmentation`, `morphology`, `features`, `classifier`, orquestrados por `pipeline.py`.  
2. **Apresentação** (`app/gui_streamlit.py` e `app/cli.py`): apenas consomem o *pipeline*.  
3. **Dados** (`data/raw/{pet,lata,papelao}`, `data/results/`).  
4. **Documentação** (`docs/relatorio/`).

Essa separação permite testar cada etapa isoladamente e gerar figuras idênticas às exibidas na GUI, garantindo consistência entre demonstração e relatório.

## 4.3 Implementação das etapas do pipeline

### 4.3.1 Aquisição e redimensionamento

A função `acquire` carrega a imagem com `cv2.imread` (com tratamento de arquivo inexistente/corrompido) e redimensiona preservando aspecto até o maior lado de 640 px (`INTER_AREA`).

### 4.3.2 Filtragem

Implementaram-se Gaussiano (\(k=5\), \(\sigma=1{,}2\)) e mediana (\(k=5\)), selecionáveis na Streamlit e no script de avaliação. Não se empilham os dois filtros em série na versão didática, para isolar efeitos no Cap. 4.

### 4.3.3 Segmentação

Conversão BGR→cinza; Otsu (default) ou limiar adaptativo. Após a binarização, aplica-se a heurística `ensure_object_white`: se os cantos da máscara forem claros (fundo típico), inverte-se a polaridade para que o **objeto fique branco**, condição necessária ao `findContours` do OpenCV.

### 4.3.4 Morfologia

Sequência abertura + fechamento com elemento elíptico \(5\times 5\) e uma iteração (`refine_mask`).

### 4.3.5 Características e classificação

Extrai-se o maior contorno com área \(\ge 500\) px e calculam-se área, perímetro, circularidade, *aspect ratio*, *extent* e *solidity*. O classificador por regras usa elongação \(\varepsilon=\max(\alpha,1/\alpha)\) e escores calibrados (ver seção 4.6).

## 4.4 Metodologia de testes

### 4.4.1 Dataset

Enquanto se coletam fotos reais (protocolo em `data/README.md`), utilizou-se um **dataset sintético controlado** gerado por `scripts/generate_synthetic_dataset.py`:

| Classe | N | Características da silhueta sintética |
|--------|---|----------------------------------------|
| PET | 12 | Corpo elíptico alongado + gargalo; fundo claro; ruído leve |
| Lata | 12 | Elipse mais compacta + topo; *highlight* pontual |
| Papelão | 12 | Retângulo rotacionado (±12°); textura pontilhada |
| **Total** | **36** | Manifesto em `data/manifest_synthetic.json` |

O uso de dados sintéticos nesta etapa permite: (i) validar o *pipeline* de ponta a ponta; (ii) calibrar limiares do classificador; (iii) produzir figuras reprodutíveis para a banca. **A entrega final recomenda substituir/complementar com fotos reais** nas mesmas pastas, reexecutando `evaluate_dataset.py`.

### 4.4.2 Testes automatizados (pytest)

Foram implementados testes em `tests/`:

- filtragem (forma preservada; método inválido → exceção);  
- segmentação/morfologia em imagem bimodal sintética;  
- integração do *pipeline* (contorno + rótulo válidos).

Resultado obtido no ambiente de desenvolvimento: **7 passed**.

### 4.4.3 Avaliação em lote

O script `scripts/evaluate_dataset.py` percorre `data/raw/*`, executa o *pipeline*, grava:

- `predictions.csv` (rótulo verdadeiro, previsto, confiança e *features*);  
- `summary.json` (acurácia e matriz de confusão);  
- mosaicos PNG por classe em `data/results/eval_*/mosaicos/` (cópias em `docs/figuras/`).

Configurações comparadas: **Gaussiano+Otsu** e **Mediana+Otsu**.

## 4.5 Resultados qualitativos (imagens antes/depois)

Para cada classe, o mosaico 2×3 exibe: original → filtrada → cinza → binária → morfologia → contorno/classe.

Figuras de referência (dataset sintético, Gaussiano+Otsu):

- `docs/figuras/PET_synth_pet_00.png`  
- `docs/figuras/Lata_synth_lata_00.png`  
- `docs/figuras/Papelao_synth_papelao_00.png`  

**Observações qualitativas:**

1. O filtro reduz granulância do fundo sem apagar a silhueta nas imagens sintéticas.  
2. Otsu, com inversão de polaridade, isola bem objetos escuros/coloridos sobre fundo claro.  
3. A morfologia fecha pequenos buracos (ex.: textura do papelão) e estabiliza o contorno.  
4. Falhas residuais de classificação ocorrem sobretudo quando a silhueta da lata fica alongada demais ou o papelão muito arredondado pela rotação/suavização — limitação esperada de um classificador só geométrico.

> Ao migrar para fotos reais, inserir neste capítulo novos mosaicos e discutir reflexos, sombras e transparência do PET.

## 4.6 Resultados quantitativos

### 4.6.1 Gaussiano + Otsu (configuração default)

| Métrica | Valor |
|---------|-------|
| Imagens avaliadas | 36 |
| Sem contorno válido | 0 |
| Classificáveis | 36 |
| **Acurácia** | **88,89%** (32/36) |

**Matriz de confusão** (linhas = verdadeiro; colunas = previsto):

|  | PET | Lata | Papelão |
|--|-----|------|---------|
| **PET** | 12 | 0 | 0 |
| **Lata** | 1 | 9 | 2 |
| **Papelão** | 1 | 0 | 11 |

### 4.6.2 Mediana + Otsu

| Métrica | Valor |
|---------|-------|
| Imagens avaliadas | 36 |
| Sem contorno válido | 0 |
| **Acurácia** | **88,89%** (32/36) |

**Matriz de confusão:**

|  | PET | Lata | Papelão |
|--|-----|------|---------|
| **PET** | 12 | 0 | 0 |
| **Lata** | 1 | 10 | 1 |
| **Papelão** | 2 | 0 | 10 |

### 4.6.3 Análise

- No conjunto sintético, Gaussiano e mediana empatam em acurácia global (88,89%), com leve redistribuição de erros entre lata e papelão.  
- A classe **PET** foi perfeita (12/12) após a introdução da elongação \(\varepsilon=\max(\alpha,1/\alpha)\).  
- Confusões concentram-se em **lata ↔ papelão/PET**, coerentes com sobreposição geométrica de silhuetas.  
- A calibração inicial (antes do ajuste de escores) classificava quase tudo como “Lata” (~33% de acurácia), evidenciando a necessidade do protocolo experimental do Cap. 4 e a sensibilidade das regras a limiares.

Esses números **não** devem ser extrapolados diretamente para ambiente industrial; servem como prova de conceito acadêmica e baseline até a coleta de imagens reais.

## 4.7 Discussão e limitações

1. **Dataset sintético:** controla variáveis, mas não reproduz transparência real do PET, amassados, rótulos complexos nem fundos texturizados.  
2. **Classificador por regras:** interpretável e didático, porém frágil a mudanças de pose (ex.: garrafa vista de cima).  
3. **Segmentação por limiar:** depende de contraste objeto/fundo; cenas cluttered exigirão métodos mais ricos (cor, *GrabCut*, deep learning).  
4. **Morfologia fixa:** parâmetros únicos podem ser subótimos por classe.  
5. **Próximos passos:** (i) fotografar 10–15 amostras reais por classe; (ii) reavaliar métricas; (iii) opcionalmente treinar k-NN/SVM sobre o vetor \(\mathbf{x}\) como baseline supervisionado (seção 3.2.2).

## 4.8 Interface de demonstração

A aplicação Streamlit (`app/gui_streamlit.py`) permite carregar uma imagem, escolher filtro e limiar, ajustar morfologia e visualizar o mosaico + diagnóstico (*features*, rótulo e *rationale*). A CLI (`app/cli.py`) gera o mesmo mosaico em arquivo, útil para automatizar figuras do relatório.
