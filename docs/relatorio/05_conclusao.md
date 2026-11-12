# 5 CONCLUSÃO

**Identificação**  
Integrante: Letícia Mateus Antunes de Melo  
Orientador: Mario Quinello  

---

O presente trabalho propôs e desenvolveu, no âmbito das Atividades Práticas Supervisionadas da UNIP, uma aplicação computacional de Processamento Digital de Imagens e Visão Computacional voltada à **segmentação e classificação de resíduos sólidos recicláveis** (garrafa PET, lata de alumínio e papelão), alinhada ao tema institucional de sustentabilidade ambiental.

Em relação aos objetivos específicos, considera-se que:

a) o referencial teórico fundamentou aquisição, filtragem espacial (Gaussiano e mediana), segmentação (Otsu e limiar adaptativo), morfologia matemática, descritores geométricos e uma proposta de modelo de VC em duas camadas (preparação por PDI e evolução supervisionada);  
b) os filtros de suavização foram implementados de forma modular, comparáveis na interface e avaliados qualitativa e quantitativamente;  
c) a binarização e as operações morfológicas (abertura seguida de fechamento) produziram máscaras utilizáveis, com correção de polaridade para compatibilidade com a extração de contornos;  
d) o classificador por regras sobre elongação, circularidade e *extent* distinguiu as três classes de modo interpretável, após calibração experimental;  
e) a interface Streamlit e os mosaicos Matplotlib viabilizam demonstração em sala e figuras “antes/depois” para o relatório;  
f) a metodologia de testes (pytest, avaliação em lote e matriz de confusão) documentou desempenho e limitações de forma reproduzível.

No conjunto **sintético** de 36 imagens (12 por classe), a configuração default (Gaussiano + Otsu) alcançou **acurácia de 88,89%**, com detecção de contorno em todas as amostras. Esse resultado valida o *pipeline* como prova de conceito acadêmica, sem pretender esgotar o problema em ambiente real de triagem — onde transparência do PET, reflexos metálicos, fundos heterogêneos e variação de pose exigirão novos dados e, eventualmente, modelos supervisionados (k-NN, SVM ou CNN), conforme proposto no Capítulo 3.

Do ponto de vista socioambiental, o projeto ilustra como técnicas clássicas de PDI, implementadas em *software* livre, podem apoiar a preparação de dados visuais para automação parcial da coleta seletiva, potencializando vazão e consistência sem substituir o papel social das cooperativas. A contribuição imediata é educacional e metodológica: um fluxo completo, documentado e demonstrável, que liga teoria, código e sustentabilidade.

**Limitações** relevantes incluem a dependência atual de silhuetas contrastadas, a fragilidade do classificador geométrico frente a mudanças de pose e o uso predominante de dataset sintético na fase de medição reportada. Como **trabalhos futuros**, destacam-se: (i) expansão do *dataset* com fotografias reais nas três classes; (ii) reavaliação das métricas do Capítulo 4 sob condições de captura semi-controladas; (iii) enriquecimento do vetor de características com cor/textura; e (iv) substituição gradual das regras por um indutor supervisionado alimentado pelas máscaras já produzidas pelo *pipeline* de PDI.

Em síntese, o APS cumpriu o ciclo pesquisa–implementação–avaliação previsto no manual da disciplina, entregando sistema funcional, relatório estruturado segundo as orientações da UNIP e caminho claro de evolução tecnológica a serviço da sustentabilidade ambiental.
