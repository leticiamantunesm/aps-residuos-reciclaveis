# 2 REFERENCIAL TEÓRICO

**Identificação**  
Integrante: Letícia Mateus Antunes de Melo  
Orientador: Mario Quinello  

**Nota:** capítulo de referencial teórico completo em rascunho acadêmico (aquisição, filtragem, segmentação, morfologia, características e proposta de VC). Ajuste fino de citações e figuras ocorrerá após os testes do Cap. 4.

---

## 2.1 Descrição formal do problema computacional

Seja \(I: \Omega \subset \mathbb{Z}^2 \rightarrow \{0,1,\ldots,L-1\}^c\) uma imagem digital com \(c\) canais (tipicamente \(c=3\) no espaço BGR/RGB) e \(L=256\) níveis de intensidade por canal. O objetivo do sistema é produzir:

1. uma máscara binária \(M: \Omega \rightarrow \{0,1\}\) que indique a região do resíduo; e  
2. um rótulo \(c \in \{\text{PET}, \text{Lata}, \text{Papelão}\}\).

Em termos de *pipeline*, define-se a composição de operadores

\[
\hat{c} = \mathcal{C}\big(\Phi(\mathcal{S}(\mathcal{F}(\mathcal{A}(I))))\big),
\]

em que \(\mathcal{A}\) representa aquisição/redimensionamento, \(\mathcal{F}\) a filtragem, \(\mathcal{S}\) a segmentação, \(\Phi\) a extração de características geométricas e \(\mathcal{C}\) o classificador. A qualidade de \(\mathcal{F}\) condiciona diretamente \(\mathcal{S}\): ruído residual e artefatos de reflexão tendem a gerar contornos fragmentados e descritores instáveis.

## 2.2 Aquisição de imagens digitais

A aquisição corresponde à conversão de uma cena contínua em uma matriz discreta de intensidades, por meio de sensor (câmera) e digitalização. No escopo deste APS, adotam-se imagens estáticas de resíduos recicláveis capturadas em condições semi-controladas (fundo preferencialmente homogêneo, objeto dominante no enquadramento). Após a captura, aplica-se redimensionamento com preservação de aspecto, limitando o maior lado da imagem a um valor máximo \(N_{\max}\) (por exemplo, 640 px), a fim de reduzir custo computacional sem eliminar as estruturas relevantes à classificação.

Fatores de aquisição relevantes ao problema incluem: iluminação não uniforme, sombras projetadas, compressão JPEG (que introduz artefatos de bloco) e reflexos especulares em superfícies de PET e alumínio. Esses fatores motivam a etapa de filtragem antes da limiarização.

## 2.3 Manipulação e representação de imagens

Uma imagem colorida pode ser tratada canal a canal ou convertida para uma representação escalar (escala de cinza) previamente à segmentação por limiar. Operações pontuais (ajuste de brilho/contraste) e espaciais (vizinhança) constituem o núcleo do PDI clássico (GONZALEZ; WOODS, 2010). Neste trabalho, a sequência didática privilegia: (i) filtragem espacial de suavização; (ii) segmentação por limiar; (iii) morfologia matemática; e (iv) descritores de forma — preparando os dados para um modelo de visão computacional interpretável.

## 2.4 Filtragem no domínio espacial

A filtragem espacial combina o valor de um pixel \(I(x,y)\) com os de sua vizinhança \(\mathcal{N}(x,y)\), produzindo uma imagem de saída \(G(x,y)\). Em filtros lineares, essa combinação assume a forma de convolução discreta:

\[
G(x,y) = \sum_{i=-a}^{a}\sum_{j=-b}^{b} w(i,j)\, I(x-i,\, y-j),
\]

em que \(w\) é o *kernel* (máscara) de pesos. Filtros não lineares, como a mediana, não admitem essa representação por soma ponderada, porém também operam sobre a mesma noção de vizinhança.

No contexto de resíduos recicláveis, a filtragem busca: (i) atenuar ruído de sensor e artefatos de compressão; (ii) reduzir oscilações locais que confundem o histograma usado por Otsu; e (iii) preservar, na medida do possível, as bordas que delimitam o objeto — pois é sobre o contorno que se calcularão área, perímetro e circularidade.

### 2.4.1 Filtro Gaussiano

O filtro Gaussiano é um suavizador linear cujos pesos aproximam uma função gaussiana bidimensional. Em tempo contínuo,

\[
g_{\sigma}(x,y) = \frac{1}{2\pi\sigma^{2}} \exp\!\left(-\frac{x^{2}+y^{2}}{2\sigma^{2}}\right),
\]

onde \(\sigma > 0\) controla a dispersão (e, portanto, o grau de borramento). Na prática digital, utiliza-se um kernel discreto de tamanho ímpar \(k \times k\) (por exemplo, \(5 \times 5\)), normalizado para que \(\sum_{i,j} w(i,j) = 1\), garantindo preservação do nível médio de cinza em regiões homogêneas.

**Interpretação espectral (intuitiva):** o Gaussiano comporta-se como filtro passa-baixas, atenuando componentes de alta frequência espacial tipicamente associadas a ruído. Quanto maior \(\sigma\) (ou \(k\)), maior a suavização e maior o risco de **borrar bordas** úteis à segmentação.

**Aplicação ao problema de resíduos.** Em imagens de garrafas PET e latas, é comum observar granulância leve e variações de iluminação de alta frequência sobre o fundo. O Gaussiano reduz essas flutuações, estabilizando a posterior limiarização. Contudo, reflexos especulares intensos (brilhos localizados) podem ser apenas “espalhados” pelo borramento, criando halos que ainda perturbam o limiar. Por isso, o Gaussiano é adotado como filtro **padrão inicial** do *pipeline*, com parâmetros moderados (\(k=5\), \(\sigma \approx 1{,}2\)), sujeitos a calibração experimental no Capítulo 4.

**Trade-off central:** suavização insuficiente mantém ruído que fragmenta a máscara; suavização excessiva funde objeto e fundo, erode detalhes do contorno e distorce descritores geométricos (perímetro e circularidade). A escolha de \(\sigma\) deve, portanto, equilibrar estabilidade da segmentação e fidelidade da forma.

### 2.4.2 Filtro da mediana

O filtro da mediana é um operador **não linear**. Para cada posição \((x,y)\), ordenam-se os valores da vizinhança de tamanho ímpar \(k \times k\) e atribui-se a \(G(x,y)\) o valor mediano dessa lista. Diferentemente da média (ou do Gaussiano), um único pixel “outlier” de intensidade extrema exerce pouca influência sobre a saída, desde que não domine mais da metade da vizinhança.

**Propriedades relevantes:**

1. **Robustez a ruído impulsivo** (“sal e pimenta”), frequente após digitalização precária ou compressão agressiva;  
2. **Melhor preservação de bordas** em muitos cenários, se comparado a suavizadores lineares de mesma janela, porque a mediana não mistura intensidades de regiões distintas da mesma forma que uma média ponderada;  
3. **Custo computacional** tipicamente maior que o Gaussiano separável, ainda aceitável para imagens redimensionadas neste APS.

**Aplicação ao problema de resíduos.** Superfícies de alumínio e PET geram *highlights* pontuais (pixels saturados). Esses picos comportam-se de modo semelhante a impulsos: a mediana tende a removê-los ou atenuá-los sem difundir tanto o brilho para o fundo quanto o Gaussiano. Já em papelão — textura mais mate e rugosa — a mediana pode, se \(k\) for grande, eliminar detalhes de textura que, embora não sejam essenciais à silhueta, ajudam a distinguir visualmente a classe em análises qualitativas. Assim, recomenda-se \(k \in \{3,5\}\) como faixa inicial.

**Comparação operacional Gaussiano × mediana (resumo didático):**

| Critério | Gaussiano | Mediana |
|----------|-----------|---------|
| Natureza | Linear (convolução) | Não linear (estatística de ordem) |
| Ruído gaussiano / granulância | Muito adequado | Adequado |
| Ruído impulsivo / highlights | Parcial (espalha o impulso) | Geralmente superior |
| Preservação de bordas | Moderada (borramento) | Frequentemente superior |
| Uso sugerido neste APS | Filtro padrão do *pipeline* | Alternativa quando há reflexos fortes |

Em síntese, a fundamentação teórica sustenta a disponibilização **das duas** opções no sistema (selecionáveis na interface Streamlit): o Gaussiano como escolha default por estabilidade e custo, e a mediana como recurso quando a aquisição apresentar impulsos ou brilhos pontuais que prejudiquem a binarização.

## 2.5 Segmentação

A segmentação é o processo de particionar a imagem em regiões significativas — neste APS, essencialmente **objeto (resíduo) versus fundo**. Após a filtragem, trabalha-se com uma representação em tons de cinza e aplica-se limiarização para obter a máscara binária \(M\). A qualidade dessa máscara determina a fidelidade do contorno e, portanto, a confiabilidade dos descritores geométricos.

### 2.5.1 Conversão para escala de cinza

Seja \(I_R\), \(I_G\) e \(I_B\) os canais de cor. Uma conversão clássica para luminância (aproximação perceptiva) é

\[
I_{\text{cinza}}(x,y) = 0{,}299\,I_R(x,y) + 0{,}587\,I_G(x,y) + 0{,}114\,I_B(x,y).
\]

Bibliotecas como o OpenCV utilizam conversões equivalentes no espaço BGR. A redução a um único canal simplifica o histograma e torna aplicáveis os métodos de limiar global e adaptativo. Em resíduos recicláveis, a conversão é adequada quando há contraste tonal suficiente entre objeto e fundo; casos de PET transparente sobre fundo claro ou papelão marrom sobre madeira podem exigir cuidado na aquisição (fundo contrastante) ou, futuramente, segmentação em outro espaço de cor (HSV/Lab) — fora do escopo mínimo do protótipo, porém mencionada como limitação.

### 2.5.2 Limiarização de Otsu

A limiarização global mapeia

\[
M(x,y) =
\begin{cases}
1, & \text{se } I_{\text{cinza}}(x,y) > T, \\
0, & \text{caso contrário,}
\end{cases}
\]

(ou a desigualdade inversa, conforme a polaridade objeto/fundo). O método de **Otsu** escolhe automaticamente o limiar \(T^{*}\) que maximiza a **variância entre classes** do histograma, sob a hipótese de que a imagem é aproximadamente bimodal (dois grupos dominantes de intensidades: fundo e objeto) (GONZALEZ; WOODS, 2010).

Se \(p(i)\) é a probabilidade normalizada do nível de cinza \(i\), e para um limiar \(T\) definem-se as probabilidades acumuladas e as médias das classes \(C_0=\{0,\ldots,T\}\) e \(C_1=\{T+1,\ldots,L-1\}\), a variância entre classes é

\[
\sigma_B^{2}(T) = \omega_0(T)\,\omega_1(T)\big(\mu_0(T)-\mu_1(T)\big)^{2},
\]

e

\[
T^{*} = \arg\max_{T} \sigma_B^{2}(T).
\]

**Aplicação ao problema.** Em capturas semi-controladas (fundo claro homogêneo e objeto mais escuro, ou vice-versa), Otsu costuma produzir máscaras coerentes com baixo custo. É o método **default** do sistema por interpretabilidade e alinhamento didático. Limitações: iluminação não uniforme, sombras fortes e reflexos podem violar a bimodalidade, gerando \(T^{*}\) inadequado e máscaras “vazadas” ou excessivas.

### 2.5.3 Limiarização adaptativa

Quando a iluminação varia espacialmente, um único \(T\) global falha. A limiarização **adaptativa** calcula um limiar local \(T(x,y)\) a partir da vizinhança do pixel, por exemplo pela média (ou média ponderada gaussiana) da janela de lado ímpar \(b\), corrigida por uma constante \(C\):

\[
T(x,y) = \mu_{\mathcal{N}_b}(x,y) - C,
\]

\[
M(x,y) =
\begin{cases}
1, & \text{se } I_{\text{cinza}}(x,y) > T(x,y), \\
0, & \text{caso contrário.}
\end{cases}
\]

**Aplicação ao problema.** Bancadas com sombra de um lado, ou latas com gradiente de brilho, beneficiam-se do limiar local. Em contrapartida, a adaptativa pode realçar textura de papelão e ruído residual, exigindo morfologia mais cuidadosa. No protótipo, \(b\) e \(C\) são parâmetros ajustáveis na interface (valores iniciais típicos: \(b=35\), \(C=5\)), permitindo comparação experimental com Otsu no Capítulo 4.

## 2.6 Operações morfológicas

A morfologia matemática sobre imagens binárias utiliza um elemento estruturante \(E\) (neste projeto, disco/elipse discreta de tamanho ímpar) para refinar \(M\) sem recorrer a modelos estatísticos complexos (PEDRINI; SCHWARTZ, 2008).

Sejam dilatação e erosão denotadas por \(M \oplus E\) e \(M \ominus E\). Intuitivamente:

- **Dilatação:** expande regiões “objeto” (valor 1), preenchendo pequenas lacunas e conectando componentes próximos;  
- **Erosão:** contrai o objeto, eliminando protuberâncias finas e ruído pontual.

A partir delas definem-se:

\[
\text{abertura:}\quad M \circ E = (M \ominus E) \oplus E,
\]

\[
\text{fechamento:}\quad M \bullet E = (M \oplus E) \ominus E.
\]

A **abertura** remove pequenos artefatos brancos no fundo; o **fechamento** preenche buracos escuros no interior do objeto. A sequência didática adotada no *pipeline* é

\[
M' = (M \circ E) \bullet E,
\]

isto é, abertura seguida de fechamento, com \(E\) elíptico de tamanho inicial \(5 \times 5\) e uma iteração — parâmetros calibráveis. O objetivo é obter uma máscara com **um componente conexo dominante** correspondente ao resíduo, estável o bastante para a extração de contorno.

**Cautela:** morfologia agressiva (kernel grande ou muitas iterações) pode arredondar excessivamente a silhueta, reduzindo a discriminação entre garrafa alongada e lata mais compacta. Por isso a morfologia é tratada como etapa de *refino*, não como substituta de boa aquisição e boa filtragem.

## 2.7 Extração de características e classificação

### 2.7.1 Contornos e descritores geométricos

A partir de \(M'\), extrai-se o conjunto de contornos externos. Seleciona-se o contorno \(\Gamma\) de maior área \(A(\Gamma)\), desde que \(A(\Gamma) \ge A_{\min}\) (limiar para rejeitar ruído residual). Sobre \(\Gamma\) calculam-se descritores clássicos:

| Descritor | Definição / interpretação |
|-----------|---------------------------|
| Área \(A\) | Número efetivo de pixels do objeto (via contorno) |
| Perímetro \(P\) | Comprimento de \(\Gamma\) |
| Circularidade | \(4\pi A / P^{2}\) (máx. 1 para círculo ideal) |
| *Aspect ratio* | \(w/h\) do retângulo envolvente |
| *Extent* | \(A / (w\cdot h)\) — ocupação do *bounding box* |
| *Solidity* | \(A / A_{\text{convex}}\) — compacidade frente ao fecho convexo |

Esses atributos são **invariantes a cor** e dependem sobretudo da silhueta — coerente com um protótipo que enfatiza PDI clássico. Hipóteses geométricas iniciais (a validar):

- **Lata:** circularidade relativamente alta, forma mais compacta;  
- **PET:** *aspect ratio* mais extremo (silhueta alongada / gargalo);  
- **Papelão:** menor circularidade, *extent* associado a formas mais retangulares.

### 2.7.2 Classificação por regras interpretáveis

O classificador do protótipo, \(\mathcal{C}\), atribui escores heurísticos às três classes com base nos descritores e seleciona o rótulo de maior escore, expondo também uma *rationale* textual (útil na GUI e na defesa oral). Trata-se de um modelo **transparente**, adequado ao semestre e à avaliação didática, ainda que sujeito a erros quando a segmentação falha ou quando duas classes produzem silhuetas semelhantes (por exemplo, garrafa vista de cima versus lata).

Formalmente, se \(\mathbf{x} = \Phi(\Gamma)\) é o vetor de características,

\[
\hat{c} = \arg\max_{c \in \mathcal{Y}} s_c(\mathbf{x}), \quad \mathcal{Y}=\{\text{PET},\text{Lata},\text{Papelão}\},
\]

onde \(s_c\) são funções de pontuação definidas por regras (Capítulo 3 e implementação no código). A confiança reportada acompanha \(s_{\hat{c}}(\mathbf{x})\), sem pretender probabilidade calibrada no sentido bayesiano.

## 2.8 Proposta teórica de modelo de Visão Computacional

O edital da APS solicita não apenas filtros de PDI, mas uma **proposta teórica de modelo adequado de visão computacional**, de modo que o processamento prepare dados para VC. A arquitetura conceitual deste trabalho organiza-se em duas camadas:

**Camada A — Preparação de dados por PDI (implementada no protótipo).**  
Aquisição → filtragem → segmentação → morfologia → máscara/contorno → vetor \(\mathbf{x}\). Essa camada reduz ruído, isola o objeto e produz representação compacta e interpretável.

**Camada B — Modelo de VC para classificação (proposta de evolução).**  
Com um conjunto rotulado \(\{(\mathbf{x}_i, y_i)\}\) ou com as próprias imagens (ou *patches* mascarados), podem-se empregar:

1. **k-NN ou SVM sobre \(\mathbf{x}\):** baixo custo, bom quando o *dataset* é pequeno e as classes são linearmente/quase-linearmente separáveis no espaço de descritores;  
2. **Classificador supervisionado em *features* de textura/cor** (além da geometria), caso silhuetas se sobreponham;  
3. **CNN (por exemplo, arquitetura leve do tipo MobileNet)** treinada sobre imagens recortadas pela máscara \(M'\), quando houver volume suficiente de exemplos e interesse em robustez a pose e fundo.

A escolha **prioritária para o protótipo acadêmico** é a Camada A + classificador por regras (e, se o calendário permitir, um baseline k-NN sobre \(\mathbf{x}\)), porque:

- evidencia cada etapa de PDI exigida pela disciplina;  
- facilita a explicação em seminário de 10–15 minutos;  
- gera artefatos (máscaras, mosaicos) diretamente aproveitáveis no relatório;  
- deixa explícito o caminho para um modelo de VC mais poderoso sem comprometer a entrega do semestre.

Em outras palavras: o sistema atual **já é** um *pipeline* de visão computacional clássica (percepção → representação → decisão); a proposta teórica reconhece que a decisão pode migrar de regras para aprendizado supervisionado assim que o conjunto de imagens rotuladas for ampliado — exatamente o espírito de “preparação dos dados para, a posteriori, alimentar modelos de VC” presente no manual da APS.

