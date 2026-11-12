# Dataset — resíduos recicláveis (APS)

## Organização

```text
data/raw/pet/       # Garrafas PET
data/raw/lata/      # Latas de alumínio
data/raw/papelao/   # Papelão
data/results/       # Mosaicos e métricas geradas pelos scripts
```

## Dataset sintético (já gerado)

```bash
.\.venv\Scripts\python.exe scripts\generate_synthetic_dataset.py --n 12
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --denoise gaussian --threshold otsu
```

Arquivos: `synth_*.png` + `data/manifest_synthetic.json`.  
Baseline Cap. 4: **88,89%** de acurácia (Gaussiano+Otsu).

## Fotos reais — checklist para a Letícia

Meta: **10–15 fotos por classe** (PET, lata, papelão).

### Como fotografar
1. Fundo **claro e homogêneo** (papel A4 / parede branca).
2. **Um objeto** por foto, centralizado, ocupando boa parte do quadro.
3. Luz estável (dia perto da janela ou lâmpada fixa); evitar sombra forte de um lado.
4. Variar levemente a pose (frente, leve giro), sem empilhar objetos.
5. Formato JPG ou PNG.

### Onde salvar
Coloque os arquivos assim (nomes livres, preferencialmente sem `synth_`):

```text
data/raw/pet/foto01.jpg
data/raw/lata/foto01.jpg
data/raw/papelao/foto01.jpg
```

### O que fazer com as sintéticas
- **Opção A (recomendada para o relatório final):** mover `synth_*.png` para uma pasta à parte (ex.: `data/raw/_sintetico_backup/`) e deixar em `raw/` só as fotos reais.  
- **Opção B:** manter sintéticas + reais juntas (a avaliação mistura os dois conjuntos).

### Depois de salvar as fotos
Avise no chat **“fotos prontas”** — aí reexecutamos:

```bash
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --denoise gaussian --threshold otsu
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --denoise median --threshold otsu
```

e atualizamos as seções 4.5–4.6 do Cap. 4 com a nova acurácia, matriz de confusão e mosaicos.
