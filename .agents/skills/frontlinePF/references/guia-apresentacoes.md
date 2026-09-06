# Frontline PF — Guia para Apresentações Corporativas (Slides)

Este guia estabelece os padrões visuais e conceituais para criação de apresentações executivas, briefings operacionais, relatórios de gestão e palestras magnas da Polícia Federal, garantindo sobriedade, legibilidade e alto impacto institucional.

---

## 1. Diretrizes Gerais

- **Proporção Obrigatória**: Widescreen **16:9** (1920x1080px).
- **Sobriedade Institucional**: Apresentações da PF devem priorizar clareza, concisão e dados verificáveis, evitando animações exageradas, efeitos 3D ou poluição visual.
- **Identificação e Sigilo**: Todo slide corporativo deve indicar, quando aplicável, o nível de classificação da informação no canto superior direito (ex: `PÚBLICO`, `RESERVADO`, `SECRETO`).

---

## 2. As Duas Matrizes Oficiais de Cores

### 2.1. Dark Master (Solenidade, Briefings Táticos e Grandes Eventos)
Indicada para auditórios, projeções em salas escuras, anúncios de operações policiais e eventos solenes.

- **Fundo**: **PF-Black (`#111213`)** sólido.
- **Títulos**: Branco (`#FFFFFF`) em Roboto Bold.
- **Acentos e Destaques**: **PF-Gold500 (`#E1AD62`)** para filetes finos, números de impacto e ícones principais.
- **Corpo de Texto**: **PF-Grey300 (`#BDBEC3`)** para leitura confortável sem ofuscar.
- **Gráficos e Ações**: **PF-Blue400 (`#367ECC`)** e **PF-Green400 (`#2DC73F`)**.

### 2.2. Light Master (Relatórios Técnicos e Reuniões de Trabalho)
Indicada para salas iluminadas, reuniões de comitê de governança e apresentações que serão impressas ou distribuídas em PDF.

- **Fundo**: Branco puro (`#FFFFFF`) ou **PF-Grey100 (`#ECEDEE`)**.
- **Títulos**: **PF-Grey700 (`#41434E`)** ou **PF-Black (`#111213`)**.
- **Acentos e Destaques**: **PF-Blue500 (`#3363CC`)** e **PF-Gold600 (`#C19515`)**.
- **Corpo de Texto**: **PF-Grey600 (`#555868`)**.

---

## 3. Escala Tipográfica para Slides (pt)

| Elemento do Slide | Tamanho Recomendado | Peso | Cor (Dark / Light) |
|:---|:---:|:---:|:---|
| **Título da Capa** | `40pt` a `48pt` | Bold (700) | `#FFFFFF` / `#111213` |
| **Subtítulo da Capa** | `20pt` a `24pt` | Regular (400) | `#E1AD62` / `#6A6D7C` |
| **Título do Slide** | `28pt` a `32pt` | Bold (700) | `#FFFFFF` / `#41434E` |
| **Subtítulo de Seção** | `18pt` a `20pt` | Medium (500) | `#E1AD62` / `#3363CC` |
| **Texto Corrido / Bullets** | `14pt` a `16pt` | Regular (400) | `#BDBEC3` / `#555868` |
| **Big Numbers (Métricas)** | `56pt` a `72pt` | Bold (700) | `#E1AD62` / `#3363CC` |
| **Rótulo de Métricas** | `12pt` a `14pt` | Medium (500) | `#FFFFFF` / `#41434E` |
| **Notas de Rodapé e Fonte** | `10pt` | Regular (400) | `#6A6D7C` / `#8E919F` |

---

## 4. Estrutura Canônica de um Deck da PF

```
[Slide 1] Capa Institucional (Brasão PF + Título + Data + Assinatura Ministerial)
   │
[Slide 2] Sumário Executivo / Pauta da Reunião
   │
[Slide 3] Contextualização e Objetivos Estratégicos
   │
[Slide 4] Resultados Operacionais / Big Numbers (Métricas de Impacto)
   │
[Slide 5] Tabelas e Gráficos Comparativos (Linhas e Barras Frontline)
   │
[Slide 6] Desdobramentos e Próximos Passos
   │
[Slide 7] Encerramento (Canais Oficiais, Ouvidoria e Brasão)
```

---

## 5. Modelos de Diagramação dos Slides

### 5.1. Slide de Capa Institucional
- Brasão oficial da Polícia Federal posicionado no terço superior esquerdo ou centralizado.
- Título do Projeto ou Nome da Operação em caixa baixa alta (apenas iniciais maiúsculas), peso Bold.
- Barra inferior fina (4px) em **PF-Gold500 (`#E1AD62`)**.
- Rodapé discreto: `Polícia Federal — Ministério da Justiça e Segurança Pública`.

### 5.2. Slide de Métricas e Resultados (Big Numbers)
Organizado em 3 ou 4 colunas no grid de 8px:
- **Card 1**: `R$ 1,4 bi` (Valor em PF-Gold500, 60pt) -> `Patrimônio Descapitalizado` (Roboto 14pt).
- **Card 2**: `148` (Valor em PF-Blue500, 60pt) -> `Mandados de Busca Cumpridos` (Roboto 14pt).
- **Card 3**: `99,4%` (Valor em PF-Green500, 60pt) -> `Índice de Efetividade da Ação` (Roboto 14pt).

### 5.3. Slide de Tabelas e Gráficos
- Inspirado no componente `TableCustom` do Frontline:
  - Cabeçalho escuro com texto branco.
  - Linhas com preenchimento alternado sutil.
  - Alinhamento de dados numéricos sempre à direita; textos à esquerda.

---

## 6. Tratamento de Fotografias e Imagens Operacionais

1. **Fotografias de Ações Policiais**:
   - Devem ter alta resolução e foco nítido, sem saturações artificiais.
   - **Privacidade e Sigilo**: Rostos de agentes táticos devem ser protegidos com desfoque (*blur*) ou tarja neutra sempre que exigido por protocolos operacionais.
   - Rostos de custodiados e investigados só podem ser exibidos em conformidade estrita com a Lei de Abuso de Autoridade (Lei nº 13.869/2019).
2. **Máscara Escura sobre Fotos de Fundo**:
   - Ao utilizar fotos de viaturas, helicópteros ou perícias como fundo de slide, aplicar uma camada (*overlay*) preta com **60% a 80% de opacidade** para garantir que os textos em branco fiquem perfeitamente legíveis.
