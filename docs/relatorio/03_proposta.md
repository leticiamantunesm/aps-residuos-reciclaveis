# 3 PROPOSTA DO PROJETO

**Identificação**  
Integrante: Letícia Mateus Antunes de Melo  
Orientador: Mario Quinello  

**Nota:** capítulo de proposta completo em rascunho — filtros, *pipeline* de segmentação/morfologia e modelagem de inteligência (protótipo + evolução). Parâmetros numéricos serão confirmados experimentalmente no Capítulo 4.

---

## 3.1 Solução baseada em Processamento Digital de Imagens

A solução proposta consiste em um *pipeline* modular em Python (OpenCV/NumPy), demonstrável via interface Streamlit, organizado nas etapas: aquisição e redimensionamento; filtragem; segmentação; morfologia; extração de características; classificação interpretável. A modularidade permite isolar o efeito de cada operador — requisito didático da disciplina e requisito metodológico para o relatório (análise “antes/depois”).

Do ponto de vista de arquitetura de *software*, cada etapa corresponde a um módulo em `src/residuos_aps/`, orquestrado por `pipeline.py` e exposto na GUI. Essa separação garante: (i) reuso em CLI e Streamlit; (ii) testes unitários por etapa; (iii) rastreabilidade entre o texto acadêmico e o código do apêndice.

### 3.1.1 Justificativa dos filtros escolhidos (matemática e lógica)

#### a) Por que filtrar antes de segmentar?

A limiarização (Otsu ou adaptativa) assume, implicitamente, que pixels do objeto e do fundo formam grupos de intensidade relativamente coerentes. Ruído de alta frequência e *highlights* pontuais alargam ou multimodalizam o histograma local, elevando a chance de:

- buracos no interior do objeto (falsos negativos na máscara);  
- manchas no fundo (falsos positivos);  
- contornos irregulares que inflacionam o perímetro e degradam a circularidade.

Logo, a filtragem \(\mathcal{F}\) não é adorno visual: é condição de estabilidade para \(\mathcal{S}\) e, em cascata, para \(\Phi\) e \(\mathcal{C}\).

#### b) Justificativa matemática do filtro Gaussiano

Adota-se o Gaussiano como filtro **padrão** porque:

1. **Modelo de ruído:** parte significativa do ruído de aquisição aproxima-se de perturbações aditivas de média nula; a convolução com \(g_{\sigma}\) reduz a variância local em regiões homogêneas.  
2. **Separabilidade:** o kernel 2D fatora-se em duas passagens 1D, tornando o custo \(O(k\cdot n)\) atrativo para demonstrações em sala.  
3. **Controle explícito por \(\sigma\):** o parâmetro possui interpretação geométrica clara (escala espacial da suavização), facilitando a discussão acadêmica e a calibração.

Parâmetros iniciais propostos (a validar experimentalmente no Cap. 4):

| Parâmetro | Valor inicial | Lógica |
|-----------|---------------|--------|
| Tamanho do kernel \(k\) | 5 (ímpar) | Vizinhança suficiente para atenuar granulância sem apagar a silhueta em imagens ~640 px |
| Desvio \(\sigma\) | 1,2 | Suavização moderada; evita borramento excessivo de bordas PET/lata |
| Momento de aplicação | Após redimensionamento, antes do cinza/limiar | Atua sobre a imagem já redimensionada, previamente à segmentação |

**Critério de aceite qualitativo:** após o Gaussiano, a máscara de Otsu deve apresentar menos componentes conexos espúrios no fundo, sem “derreter” o contorno do objeto a ponto de alterar grosseiramente a razão de aspecto.

#### c) Justificativa matemática do filtro da mediana

A mediana entra como **alternativa configurável** (e não apenas como menção teórica) quando o residual após o Gaussiano ainda contém impulsos:

\[
G(x,y) = \mathrm{med}\big\{ I(u,v) : (u,v) \in \mathcal{N}_k(x,y) \big\}.
\]

A lógica de escolha apoia-se em três argumentos:

1. **Robustez estatística:** a mediana possui ponto de ruptura elevado frente a *outliers*, adequado a pixels saturados de reflexo em alumínio e PET.  
2. **Preservação de descontinuidades:** em bordas degrau, a mediana tende a manter a transição mais nítida do que a média ponderada, beneficiando o perímetro.  
3. **Complementaridade didática:** permitir a comparação lado a lado (Streamlit) entre Gaussiano e mediana materializa, no software, o conteúdo do referencial teórico (seção 2.4).

Parâmetros iniciais: \(k \in \{3,5\}\). Valores \(k \ge 7\) só serão considerados se testes mostrarem impulsos densos; caso contrário, prioriza-se não erosão excessiva de protuberâncias da silhueta (gargalo de garrafa, aba de lata, cantos de papelão).

#### d) Critério lógico de seleção em tempo de execução

Na interface e no *pipeline*, propõe-se a seguinte política:

1. **Default:** Gaussiano (\(k=5\), \(\sigma=1{,}2\)).  
2. **Alternar para mediana** quando inspeção visual indicar *highlights* pontuais ou ruído “sal e pimenta”, ou quando a máscara pós-Otsu permanecer fragmentada após morfologia leve.  
3. **Não empilhar** Gaussiano + mediana em série na versão didática inicial (para não confundir o efeito de cada filtro na análise do Cap. 4). A combinação em cascata fica registrada como trabalho futuro, caso o *dataset* exija.

#### e) Relação com as classes-alvo

| Classe | Desafio visual típico | Filtro preferencial (hipótese) |
|--------|------------------------|--------------------------------|
| PET | Transparência parcial, reflexos lineares | Gaussiano; mediana se brilhos pontuais dominarem |
| Lata de alumínio | Reflexos especulares intensos | Mediana frequentemente vantajosa |
| Papelão | Textura rugosa, menos specular | Gaussiano costuma bastar; mediana com \(k\) pequeno |

Essas hipóteses serão confirmadas ou refutadas pelos testes quantitativos/qualitativos do Capítulo 4, com mosaicos “antes/depois” exportados pelo próprio sistema.

### 3.1.2 Pipeline de segmentação e morfologia

Após \(\mathcal{F}\), a proposta de segmentação e refinamento morfológico materializa o operador \(\mathcal{S}\) discutido no Cap. 2, com parâmetros iniciais explícitos e critérios de aceite.

#### a) Fluxo operacional proposto

\[
I \xrightarrow{\mathcal{A}} I_r \xrightarrow{\mathcal{F}} I_f \xrightarrow{\text{cinza}} I_g \xrightarrow{\text{limiar}} M \xrightarrow{\text{morfologia}} M' \xrightarrow{\text{contorno}} \Gamma.
\]

1. **Aquisição (\(\mathcal{A}\)):** carga da imagem e redimensionamento com maior lado \(N_{\max}=640\) px, preservando aspecto.  
2. **Filtragem (\(\mathcal{F}\)):** Gaussiano (default) ou mediana (seção 3.1.1).  
3. **Escala de cinza:** conversão BGR→cinza para histograma unidimensional.  
4. **Limiarização:** Otsu (default) ou adaptativa.  
5. **Morfologia:** abertura seguida de fechamento com elemento estruturante elíptico.  
6. **Contorno principal:** maior componente com área \(\ge A_{\min}\).

#### b) Escolha do método de limiar

| Método | Quando usar (proposta) | Parâmetros iniciais |
|--------|------------------------|---------------------|
| **Otsu** (default) | Fundo homogêneo, contraste global objeto/fundo | \(T^{*}\) automático |
| **Adaptativa** | Sombra lateral, gradiente de iluminação, bancada irregular | bloco \(b=35\) (ímpar), \(C=5\) |

**Lógica:** Otsu maximiza interpretabilidade e atende ao cenário didático “objeto único + fundo limpo”. A adaptativa fica disponível na Streamlit para demonstrar robustez quando a hipótese de bimodalidade global falha. Em ambos os casos, pode ser necessário **inverter** a máscara se o objeto for mais claro que o fundo (tratado empiricamente nos testes; o código pode expor *toggle* de inversão se os experimentos exigirem).

**Critério de aceite qualitativo da segmentação:** a máscara \(M\) deve cobrir a maior parte do resíduo sem incorporar grandes regiões de fundo; idealmente um ou poucos componentes conexos antes da morfologia.

#### c) Operações morfológicas propostas

Adota-se a sequência

\[
M' = (M \circ E) \bullet E,
\]

com \(E\) elipse discreta de tamanho \(5\times 5\) e **1 iteração** (valores iniciais). A abertura remove fuligem binária no fundo; o fechamento reduz buracos internos causados por rótulos, reflexos escuros ou transparência do PET.

| Situação observada em \(M\) | Ajuste sugerido |
|----------------------------|-----------------|
| Muitos pontos isolados no fundo | Aumentar ênfase da abertura (ou \(k\) de \(E\)) |
| Buracos no interior do objeto | Aumentar fechamento / iterações (com parcimônia) |
| Silhueta “inchada” ou arredondada demais | Reduzir \(k\) ou iterações |

**Critério de aceite de \(M'\):** contorno único dominante, sem fragmentação severa; gargalo de PET e cantos de papelão ainda reconhecíveis visualmente.

#### d) Extração do contorno válido

Seleciona-se

\[
\Gamma^{*} = \arg\max_{\Gamma} A(\Gamma) \quad \text{sujeito a} \quad A(\Gamma) \ge A_{\min},
\]

com \(A_{\min}=500\) pixels (em imagem já redimensionada) como rejeição de ruído. Se nenhum contorno satisfizer a restrição, o sistema reporta falha de detecção — comportamento preferível a classificar “no escuro”.

#### e) Saídas intermediárias para o relatório

Para cada imagem de teste, o sistema deve poder exportar o mosaico: original → filtrada → cinza → binária → morfologia → contorno/classe. Essas figuras alimentam a análise “antes/depois” do Capítulo 4 e a demonstração em sala.

## 3.2 Modelagem e algoritmos de inteligência adequados

A modelagem distingue **o que o protótipo implementa agora** (decisão interpretável sobre descritores geométricos) da **evolução teórica** exigida pelo edital (modelos de VC supervisionados alimentados pelos dados preparados pelo PDI).

### 3.2.1 Classificador por regras / descritores geométricos (protótipo)

#### a) Representação

Dado \(\Gamma^{*}\), define-se o vetor de características

\[
\mathbf{x} = \big(A,\, P,\, \kappa,\, \alpha,\, e,\, s\big),
\]

em que \(\kappa = 4\pi A / P^{2}\) (circularidade), \(\alpha = w/h\) (*aspect ratio*), \(e = A/(w\cdot h)\) (*extent*) e \(s = A/A_{\text{convex}}\) (*solidity*).

Essa representação é deliberadamente **geométrica**: depende da qualidade da máscara, o que reforça a importância das etapas de PDI e torna o erro de classificação diagnosticável (falhou a silhueta ou a regra?).

#### b) Funções de pontuação (heurística inicial)

Define-se a elongação \(\varepsilon = \max(\alpha, 1/\alpha)\) (com \(\alpha>0\)), invariante à orientação largura/altura. Para o protótipo, propõem-se escores em \([0,1]\) (valores de corte calibráveis no Cap. 4):

\[
s_{\text{Lata}}(\mathbf{x}) = \mathrm{clip}\!\left(\frac{\kappa-0{,}75}{0{,}25}\right),\quad
s_{\text{PET}}(\mathbf{x}) = \mathrm{clip}\!\left(\frac{\varepsilon-1{,}35}{0{,}90}\right),\quad
s_{\text{Papelão}}(\mathbf{x}) = \mathrm{clip}\!\left(\frac{0{,}78-\kappa}{0{,}25}\right)\cdot \max(e,0{,}5),
\]

com \(\mathrm{clip}\) restringindo ao intervalo unitário. A decisão é

\[
\hat{c} = \arg\max_{c} s_c(\mathbf{x}),
\]

e a “confiança” exibida na GUI é \(s_{\hat{c}}(\mathbf{x})\), acompanhada de *rationale* textual com \(\kappa\), \(\alpha\), \(\varepsilon\) e \(e\).

**Justificativa lógica das regras:**

- latas tendem a silhuetas mais compactas/circulares → privilegiar \(\kappa\) alto;  
- garrafas PET, em vista lateral típica, alongam-se → privilegiar \(\varepsilon\);  
- papelão aproxima retângulos de circularidade menor → privilegiar baixa \(\kappa\) ponderada por \(e\).

#### c) Limitações conscientes do protótipo

1. Dependência forte da pose (garrafa vista de cima pode parecer lata).  
2. Ausência de cor/textura (PET âmbar vs. transparente; papelão impresso).  
3. Escores não calibrados como probabilidades.  
4. Necessidade de ajuste fino com o *dataset* real no Cap. 4 (possivelmente limiares adicionais ou pesos).

Mesmo com essas limitações, o modelo atende ao objetivo acadêmico: **decisão explicável** sobre dados preparados por PDI, pronta para ser substituída por um indutor supervisionado sem reescrever o *frontend* de aquisição/segmentação.

#### d) Protocolo de avaliação previsto

- Conjunto mínimo por classe (meta: dezenas de imagens; piso didático: amostra balanceada PET/lata/papelão).  
- Métricas: acurácia global, matriz de confusão, taxa de “sem contorno”.  
- Análise qualitativa dos mosaicos e dos casos de erro (segmentação vs. regra).  
- Tempo médio por imagem (garantir fluidez na apresentação).

### 3.2.2 Perspectiva de evolução (k-NN, SVM ou CNN supervisionada)

O edital pede propor modelagem e algoritmos de inteligência adequados para imagens. Mantendo a Camada A (PDI) fixa, a Camada B pode evoluir em três níveis de complexidade:

#### Nível 1 — k-NN sobre \(\mathbf{x}\)

Com um conjunto rotulado \(\{(\mathbf{x}_i,y_i)\}\), o *k-Nearest Neighbors* classifica uma nova amostra pela maioria dos \(k\) vizinhos no espaço de descritores (distância euclidiana ou Mahalanobis após normalização).  

**Adequação:** *dataset* pequeno; implementação simples; boa linha de base (*baseline*) para medir o ganho sobre regras manuais.

#### Nível 2 — SVM sobre \(\mathbf{x}\) (e *features* estendidas)

Uma SVM com *kernel* RBF aprende fronteiras não lineares entre classes no espaço de descritores. Pode-se estender \(\mathbf{x}\) com estatísticas de cor na região mascarada (média/desvio em HSV) ou descritores de textura (LBP), mitigando confusões puramente geométricas.

**Adequação:** médio porte de dados; ainda interpretável via importância relativa de atributos (com análises auxiliares).

#### Nível 3 — CNN leve sobre o recorte mascarado

Utilizar \(M'\) para recortar o objeto (ou zerar o fundo) e treinar uma rede convolucional compacta (ex.: MobileNet) para classificar PET/lata/papelão.

**Adequação:** quando houver volume e variedade suficientes (pose, iluminação, marcas); maior acurácia potencial, menor interpretabilidade pontual — compensada pelos artefatos de PDI ainda visíveis no *pipeline*.

#### Critério de escolha recomendado neste APS

| Critério | Regras (protótipo) | k-NN/SVM | CNN |
|----------|--------------------|----------|-----|
| Esforço de rotulagem | Mínimo | Médio | Alto |
| Explicabilidade na banca | Alta | Média | Baixa/média |
| Alinhamento ao PDI da disciplina | Direto | Direto (usa \(\mathbf{x}\)) | Indireto (usa máscara/recorte) |
| Potencial de acurácia | Limitado | Bom | Alto (com dados) |

**Proposta oficial do trabalho:** implementar e avaliar o **classificador por regras** como núcleo da entrega prática; documentar k-NN/SVM/CNN como **rota de evolução** teoricamente fundamentada, deixando opcional a inclusão de um *baseline* k-NN se o calendário e o *dataset* permitirem. Assim, cumpre-se tanto a exigência de PDI quanto a de modelagem de VC para sustentabilidade ambiental, sem descaracterizar o caráter supervisionado da disciplina.

## 3.3 Síntese da proposta

O projeto entrega um sistema capaz de: (i) preparar imagens de resíduos recicláveis por um *pipeline* clássico de PDI; (ii) segmentar o objeto de interesse; (iii) extrair descritores de forma; e (iv) classificar, de modo interpretável, entre PET, lata e papelão — com interface Streamlit para demonstração. A filtragem (Gaussiano/mediana), a limiarização (Otsu/adaptativa) e a morfologia (abertura+fechamento) formam a espinha dorsal metodológica; a inteligência do protótipo privilegia transparência, e a inteligência futura privilegia aprendizado supervisionado sobre os dados já preparados.
