# Sumário do Relatório Acadêmico (APS UNIP)

**Tema:** Classificação e Segmentação de Resíduos Sólidos (Lixo Reciclável) para Automação de Coleta Seletiva  

**Integrante:** Letícia Mateus Antunes de Melo  
**Orientador:** Mario Quinello  
**Curso:** Ciência da Computação — 5º/6º semestre — UNIP  

**Formatação (manual APS):** Arial 12; espaçamento 1,5; A4; margens esquerda e direita **2,5 cm**.

---

## Elementos pré-textuais (entrega final)

1. Capa  
2. Folha de rosto  
3. Resumo / Abstract (opcional conforme orientação do professor)  
4. Lista de figuras  
5. Lista de tabelas (se houver)  
6. Sumário  

---

## Estrutura textual

### 1 INTRODUÇÃO
1.1 Definição do problema  
1.2 Contexto ecológico e social  
1.3 Objetivos  
  1.3.1 Objetivo geral  
  1.3.2 Objetivos específicos  

### 2 REFERENCIAL TEÓRICO
2.1 Descrição formal do problema computacional  
2.2 Aquisição de imagens digitais  
2.3 Manipulação e representação de imagens  
2.4 Filtragem no domínio espacial  
  2.4.1 Filtro Gaussiano  
  2.4.2 Filtro da mediana  
2.5 Segmentação  
  2.5.1 Conversão para escala de cinza  
  2.5.2 Limiarização de Otsu  
  2.5.3 Limiarização adaptativa  
2.6 Operações morfológicas  
2.7 Extração de características e classificação  
2.8 Proposta teórica de modelo de Visão Computacional  

### 3 PROPOSTA DO PROJETO
3.1 Solução baseada em Processamento Digital de Imagens  
  3.1.1 Justificativa dos filtros escolhidos (matemática e lógica)  
  3.1.2 Pipeline de segmentação e morfologia  
3.2 Modelagem e algoritmos de inteligência adequados  
  3.2.1 Classificador por regras / descritores geométricos (protótipo)  
  3.2.2 Perspectiva de evolução (k-NN, SVM ou CNN supervisionada)  
3.3 Síntese da proposta  

### 4 DESENVOLVIMENTO
4.1 Ferramentas utilizadas  
4.2 Arquitetura do software  
4.3 Implementação das etapas do pipeline  
4.4 Metodologia de testes  
4.5 Resultados qualitativos (imagens antes/depois)  
4.6 Resultados quantitativos (acurácia, tempo, falhas)  
4.7 Discussão e limitações  

### 5 CONCLUSÃO

### REFERÊNCIAS (ABNT NBR 6023)

### APÊNDICE A — Código-fonte do programa desenvolvido  

### ANEXO — Ficha de Atividades Práticas Supervisionadas  

---

## Cronograma sugerido (alinhado ao edital)

| Fase | Conteúdo | Status |
|------|----------|--------|
| Intermediária I (pré-P1) | Cap. 1 + filtragem nos Caps. 2 e 3 | Caps. 1–3 ok; passar para DOCX ABNT |
| Intermediária II (pré-P2) | Plano final + protótipo | Caps. 1–5 + sistema ok (acc. sintética 88,9%); falta fotos reais e DOCX/apresentação |
| Apresentação (10–15 min) | Problema, demo Streamlit, resultados | A preparar |
