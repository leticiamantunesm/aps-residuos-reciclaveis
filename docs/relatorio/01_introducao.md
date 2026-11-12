# 1 INTRODUÇÃO

**Identificação**  
Integrante: Letícia Mateus Antunes de Melo  
Orientador: Mario Quinello  
Instituição: Universidade Paulista — UNIP  
Curso: Ciência da Computação (5º/6º semestre)  
Disciplina: Atividades Práticas Supervisionadas (APS)  

**Formatação adotada:** fonte Arial 12; espaçamento 1,5; papel A4; margens esquerda e direita de 2,5 cm (conforme manual da disciplina de APS).

---

A crescente geração de resíduos sólidos urbanos e a baixa eficiência da segregação na origem pressionam sistemas de coleta seletiva, aterros e cadeias de reciclagem. Em muitos municípios brasileiros, a separação entre materiais recicláveis — em especial plásticos (como o politereftalato de etileno, PET), metais (latas de alumínio) e papel/papelão — ainda depende fortemente de inspeção manual, sujeita a fadiga, erro humano e baixa vazão operacional. Nesse cenário, técnicas de Processamento Digital de Imagens (PDI) e Visão Computacional (VC) surgem como instrumentos viáveis para apoiar a automação da identificação e do direcionamento de resíduos, desde que os dados visuais sejam adequadamente preparados por um *pipeline* de aquisição, filtragem, segmentação e extração de características.

O presente trabalho, desenvolvido no âmbito das Atividades Práticas Supervisionadas (APS) do curso de Ciência da Computação da Universidade Paulista (UNIP), sob orientação do professor Mario Quinello e elaborado pela discente Letícia Mateus Antunes de Melo, propõe a construção de uma aplicação computacional voltada à **classificação e segmentação de resíduos sólidos recicláveis**, com ênfase em três classes de interesse didático e prático: **garrafa PET**, **lata de alumínio** e **papelão**. A solução privilegia, em primeiro plano, o PDI clássico — filtragem para redução de ruído, binarização (Otsu e/ou adaptativa) e operações morfológicas — de modo a isolar o objeto de interesse do fundo e gerar descritores geométricos (área, perímetro, circularidade, entre outros). Tais descritores alimentam um classificador simples, interpretável e alinhado ao caráter acadêmico da disciplina, servindo também como etapa de preparação de dados para modelos de visão computacional mais elaborados em trabalhos futuros.

Além da dimensão técnica, o projeto dialoga com a agenda de sustentabilidade ambiental: a melhoria da segregação reduz contaminação de lotes recicláveis, aumenta o valor agregado da matéria-prima secundária e diminui o volume destinado a aterros. Assim, a contribuição esperada é dupla — (i) demonstrar, de forma modular e reproduzível, um fluxo completo de PDI/VC aplicado a um problema real; e (ii) produzir documentação acadêmica (normas ABNT, observadas as margens e tipografia do manual da APS) que fundamente teoricamente cada escolha metodológica, conforme as orientações da disciplina de Processamento de Imagens e Visão Computacional.

## 1.1 Definição do problema

O problema computacional tratado consiste em, a partir de imagens digitais de resíduos recicláveis capturadas em condições controladas ou semi-controladas (fundo relativamente homogêneo, iluminação estável e objeto predominante no enquadramento), **detectar a região correspondente ao resíduo**, **separá-la do fundo** e **atribuir um rótulo de classe** entre as categorias PET, lata de alumínio e papelão. Formalmente, busca-se mapear uma imagem de entrada \(I\) a um par \((M, c)\), em que \(M\) é uma máscara binária (ou contorno) do objeto segmentado e \(c \in \{\text{PET}, \text{Lata}, \text{Papelão}\}\) é a classe estimada.

Desafios típicos incluem variação de brilho e sombras, ruído de aquisição, reflexos em superfícies metálicas e plásticas, deformações de contorno e sobreposição parcial com o fundo. Sem pré-processamento adequado, a segmentação por limiar tende a fragmentar o objeto ou a incorporar ruído de fundo, degradando a qualidade das *features* e, consequentemente, a classificação. O problema, portanto, não se reduz à escolha de um classificador: exige um encadeamento coerente de etapas de PDI que estabilize a representação do objeto antes da decisão.

## 1.2 Contexto ecológico e social

A Política Nacional de Resíduos Sólidos (Lei nº 12.305/2010) estabelece a responsabilidade compartilhada pelo ciclo de vida dos produtos e prioriza a não geração, a redução, a reutilização e a reciclagem em detrimento da disposição final. Ainda assim, índices nacionais de reciclagem — sobretudo de plásticos — permanecem aquém do potencial técnico dos materiais, em parte pela falha na segregação na origem e pela contaminação cruzada em cooperativas e centros de triagem.

Do ponto de vista social, cooperativas de catadores desempenham papel central na cadeia da reciclagem, frequentemente em condições de trabalho intensivo e com baixa automação. Soluções de visão computacional de baixo custo, baseadas em *software* livre (por exemplo, Python e OpenCV), podem atuar como apoio à triagem — não necessariamente substituindo o trabalho humano, mas **aumentando vazão, consistência e segurança** em esteiras ou bancadas de separação. Ecologicamente, cada fração corretamente classificada reduz demanda por matéria-prima virgem (petróleo no caso do PET; bauxita/energia no alumínio; celulose no papelão) e mitiga impactos associados a aterros e poluição difusa.

Nesse contexto, o recorte deste APS — três classes amplamente presentes no cotidiano urbano — equilibra relevância ambiental e viabilidade acadêmica de implementação e avaliação em um semestre letivo.

## 1.3 Objetivos

### 1.3.1 Objetivo geral

Desenvolver uma aplicação em Python que implemente um *pipeline* modular de Processamento Digital de Imagens para segmentação e classificação de resíduos recicláveis (PET, lata de alumínio e papelão), acompanhada de relatório acadêmico conforme as normas ABNT e as diretrizes da APS da UNIP, sob orientação do Prof. Mario Quinello.

### 1.3.2 Objetivos específicos

a) fundamentar teoricamente as etapas de aquisição, filtragem, segmentação, morfologia e extração de características, bem como a proposta de modelo de visão computacional adequado ao problema;  
b) implementar filtros de suavização (Gaussiano e/ou mediana) e avaliar qualitativa e quantitativamente seu efeito sobre a segmentação;  
c) aplicar binarização por Otsu e/ou limiarização adaptativa, seguida de operações morfológicas, para obtenção de máscaras coerentes do objeto;  
d) extrair descritores geométricos de contorno e utilizar lógica de classificação interpretável para distinguir as três classes;  
e) disponibilizar interface de demonstração em Streamlit e artefatos visuais “antes/depois” para análise de resultados e apresentação em sala;  
f) documentar metodologia de testes, limitações e trabalhos futuros, incluindo o código-fonte em apêndice.
