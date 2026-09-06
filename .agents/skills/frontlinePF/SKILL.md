---
name: frontlinePF
description: Design System oficial Frontline da Polícia Federal (PF). Especificações completas de identidade visual, paleta de cores primárias e secundárias (HEX/RGB), escala tipográfica (Roboto/Open Sans), grid modular de 8px, componentes de UI para sistemas internos e portais externos Gov.br, além de diretrizes especializadas para Landing Pages, Apresentações corporativas (slides) e peças para Redes Sociais.
---

# Frontline PF — Design System & Identidade Visual da Polícia Federal

Guia oficial e executável de identidade visual e especificações técnicas do **Frontline**, o Design System da Polícia Federal. Padroniza sistemas corporativos internos, portais externos de serviços ao cidadão (Gov.br), landing pages, apresentações de alto nível e comunicação digital em redes sociais.

---

## 1. Tabela de Consulta Rápida

| Domínio | Especificação Padrão | Observações e Regras |
|:---|:---|:---|
| **Cores Primárias** | **PF-Black** (`#111213`), **PF-Gold500** (`#E1AD62`), **PF-Blue500** (`#3363CC`) | Preto profundo de autoridade, dourado oficial do brasão e azul de ação primária |
| **Cores Secundárias** | **PF-Grey500** (`#6A6D7C`), **PF-Green500** (`#33A841`), **PF-Red500** (`#BF0C1D`) | Escala de cinzas para textos e divisores, verde para sucesso e vermelho para erros críticos |
| **Tipografia Primária** | **Roboto** (Google Fonts) | Headings `h1` (36px) até `h6` (12px); corpos `14px` e `12px` |
| **Tipografia Secundária** | **Open Sans** | Usada em apoios institucionais, legendas e textos auxiliares |
| **Sistema Espacial** | **Grid de 8px (8px Grid System)** | Margens, paddings e alturas obrigatoriamente em múltiplos de 8px (8, 16, 24, 32, 40, 48...) |
| **Grid Responsivo** | **PrimeFlex (12 colunas)** | Breakpoints: `sm: 576px`, `md: 768px`, `lg: 992px`, `xl: 1200px` |
| **Casca Intranet** | `<pf-layout>` | Header corporativo, SubHeader com perfil/módulo, Sidebar recolhível e Footer fixo |
| **Casca Externa Gov.br** | `PfLayoutInternetModel` | Barra superior Gov.br, Ministério da Justiça e Segurança Pública, Brasão PF |
| **Botões Oficiais** | Large (32px), Small (24px) | Primary (apenas 1 por tela), Secondary (neutro), Outline (3+ botões) e Ghost (link/cancelar) |
| **Biblioteca de Ícones**| **Font Awesome 5 Free** & **PrimeIcons** | Prefixos `fas fa-*`, `far fa-*` e `pi pi-*` |

---

## 2. Paleta de Cores Oficial Frontline (Códigos Exatos)

### 2.1. Cores Primárias

```css
/* Tokens Primários Oficiais */
--pf-black:      #111213; /* R 17  G 18  B 19  - Fundo institucional, headers e dark mode */
--pf-black-200:  #2A2A2A; /* R 42  G 42  B 42  - Superfícies elevadas e cards escuros */
--pf-black-100:  #373C42; /* R 55  G 60  B 66  - Divisores escuros e bordas sutis */

--pf-gold-700:   #856404; /* R 133 G 100 B 4   - Texto de alto contraste sobre fundos dourados */
--pf-gold-600:   #C19515; /* R 193 G 149 B 21  - Hover dourado e ênfase */
--pf-gold-500:   #E1AD62; /* R 225 G 173 B 98  - [PADRÃO OFICIAL] Ouro do brasão da PF */
--pf-gold-400:   #F2B64E; /* R 242 G 182 B 78  - Destaques intermediários */
--pf-gold-300:   #F7CE68; /* R 247 G 206 B 104 - Realces suaves */
--pf-gold-200:   #FFEBB9; /* R 255 G 235 B 185 - Badges de atenção */
--pf-gold-100:   #FFF8E3; /* R 255 G 248 B 227 - Fundo de avisos e alertas suaves */

--pf-blue-700:   #0F4B8B; /* R 15  G 75  B 139 - Botões pressionados, texto sobre azul claro */
--pf-blue-600:   #1F628D; /* R 31  G 98  B 141 - Hover de botões primários */
--pf-blue-500:   #3363CC; /* R 51  G 99  B 204 - [PADRÃO OFICIAL] Ações primárias e links */
--pf-blue-400:   #367ECC; /* R 54  G 126 B 204 */
--pf-blue-300:   #78ABE0; /* R 120 G 171 B 224 */
--pf-blue-200:   #A1C6ED; /* R 161 G 198 B 237 - Tags ativas */
--pf-blue-100:   #CFDBE8; /* R 207 G 219 B 232 - Fundo de caixas informativas */
```

### 2.2. Cores Secundárias e Semânticas

```css
/* Escala Neutra (Grey) */
--pf-grey-700:   #41434E; /* R 65  G 67  B 78  - Títulos e textos escuros */
--pf-grey-600:   #555868; /* R 85  G 88  B 104 - Textos secundários e legendas */
--pf-grey-500:   #6A6D7C; /* R 106 G 109 B 124 - [PADRÃO OFICIAL] Ícones inativos e bordas neutras */
--pf-grey-400:   #8E919F; /* R 141 G 151 B 160 - Placeholders de formulário */
--pf-grey-300:   #BDBEC3; /* R 189 G 190 B 195 - Bordas de inputs */
--pf-grey-200:   #DADADD; /* R 218 G 218 B 221 - Linhas de tabelas e divisores */
--pf-grey-100:   #ECEDEE; /* R 236 G 237 B 238 - Zebrado de tabelas e fundos neutros */

/* Semântico de Sucesso (Green) */
--pf-green-700:  #3C6841; /* R 60  G 104 B 65 */
--pf-green-600:  #287831; /* R 40  G 120 B 49  - Hover de confirmação */
--pf-green-500:  #33A841; /* R 51  G 168 B 65  - [PADRÃO OFICIAL] Status regular e sucesso */
--pf-green-100:  #DDECDC; /* R 221 G 236 B 220 - Fundo de alerta de sucesso */

/* Semântico de Erro e Perigo (Red) */
--pf-red-700:    #6E363B; /* R 110 G 54  B 59 */
--pf-red-600:    #921F2A; /* R 146 G 31  B 42  - Hover de ação destrutiva */
--pf-red-500:    #BF0C1D; /* R 191 G 12  B 29  - [PADRÃO OFICIAL] Validação .pf-error e falhas */
--pf-red-100:    #F8E8EA; /* R 248 G 232 B 234 - Fundo de caixas de erro crítico */
```

---

## 3. Escala Tipográfica Frontline

A tipografia oficial é fundamentada na família **Roboto** com tamanhos, line-heights e letter-spacings normatizados:

- **`h1`**: Roboto Bold **36px** (2.25rem), line-height: 40px — *Apenas 1 por página*.
- **`h2`**: Roboto Bold **30px** (1.875rem), line-height: 36px.
- **`h3`**: Roboto Medium **24px** (1.5rem), line-height: 30px.
- **`h4`**: Roboto Medium **20px** (1.25rem), line-height: 26px.
- **`h5`**: Roboto Medium **16px** (1.0rem), line-height: 22px.
- **`h6`**: Roboto Medium **12px** (0.75rem), line-height: 16px.
- **Body Default**: Roboto Regular **14px**, line-height: 16px a 20px.
- **Body Small**: Roboto Regular **12px**, line-height: 16px.
- **Table Header**: Roboto Medium **14px**, line-height: 16px.
- **Table Row**: Roboto Regular **14px**, line-height: 16px.
- **Menu Label**: Roboto Medium **14px**, line-height: 16px, `letter-spacing: 0.125em (12.5%)`.
- **Menu Title**: Roboto Medium **12px**, line-height: 16px, `letter-spacing: 0.125em (12.5%)`.
- **Footer Version**: Roboto Regular **10px**, line-height: 12px, `letter-spacing: 0.100em (10%)`.

> [!IMPORTANT]
> **Regra de Ouro da Tipografia**: Jamais utilizar `text-uppercase` em cabeçalhos, menus laterais e botões. A caixa alta contínua prejudica o ritmo visual e a acessibilidade da leitura.

---

## 4. O Sistema de Grid de 8px e Formulários

Todo o espaçamento de interface no Frontline obedece rigorosamente a múltiplos de 8px:

- **Distância entre Label e Campo**: **8px** (`0.5rem`).
- **Distância entre campos na mesma linha (`.p-formgrid`)**: **16px** (`1rem`).
- **Distância vertical entre linhas de formulário (`.p-fluid`)**: **32px** (`2rem`).
- **Largura máxima da Sidebar de navegação**: até **338px** (múltiplos de 8px).
- **Paddings de cards e caixas de diálogo**: **24px** ou **32px**.

---

## 5. Biblioteca de Componentes e Casca da Aplicação

### 5.1. Intranet Corporativa (`<pf-layout>`)
1. **Header Corporativo**: Nome do sistema, perfil do operador com foto/email, central de notificações com badge e botão de saída Keycloak.
2. **SubHeader**: Módulo atual com indicação obrigatória de sensibilidade (`1 - Comum`, `2 - Sensível`) e seletor de perfil.
3. **Sidebar / Menu**:
   - Ícones FontAwesome apenas nos itens de nível 1.
   - Subitens sem ícones, agrupados em acordeão colapsável.
   - Limite sugerido: até 10 itens principais.
4. **Footer Corporativo**: Fixo na base, abaixo do menu, contendo link para manual, canal "Fale com a equipe" e versão da aplicação.

### 5.2. Acesso Externo ao Cidadão (Gov.br + Frontline)
- Barra superior Gov.br com links de acessibilidade (Alt+1 ao Alt+4) e VLibras.
- Assinatura oficial: **Ministério da Justiça e Segurança Pública**.
- Título principal: **Polícia Federal**, subtítulo com o nome do serviço.
- Botão oficial de autenticação: **Entrar com gov.br**.
- Rodapé externo com marcas de Acesso à Informação, Governo Federal e Brasão da PF.

### 5.3. Sistema de Botões e Regras de Agrupamento
- **Tamanhos**:
  - `Large (32px)`: Uso padrão e preferencial em toda a interface.
  - `Small (24px)`: Espaços confinados (ex: células de tabelas).
- **Estilos**:
  - `Primary (#3363CC)`: Máximo **1 por tela/modal** (ação mandatória de avanço/confirmação).
  - `Secondary (#DADADD)`: Ações secundárias em formulários.
  - `Outline (borda azul)`: Ação intermediária em agrupamentos com **3 ou mais botões**. Não usar isolado.
  - `Ghost (fundo transparente)`: Retorno, cancelar ou links contextuais.
- **Composições Homologadas**:
  - *2 opções*: `Primary` + `Ghost` (alto contraste).
  - *Opções neutras*: `Ghost` + `Ghost`.
  - *3 ou mais opções*: `Primary` (principal) + `Outline` (intermediária) + `Ghost` (retorno).

### 5.4. Componentes PF Especializados
- **Formulários**: `InputCPF`, `InputCNPJ`, `InputCPF/CNPJ` (híbrido automático), `InputCEP`, `UploadImage`, `Crop` biométrico.
- **Dados**: `TableCustom` (paginador superior e inferior para buscas densas), `TableFilter`.
- **Fluxos**: `Steps` (até 10 etapas lineares com validação obrigatória), `SideTab` (âncoras laterais), `Timeline` (histórico de investigações e processos).
- **Erros**: `PfErrorPageComponent` (páginas 401, 403, 404, 500 e 504 no formato "Código - Nome em Português", Brasão PF e botões de contingência).

---

## 6. Guias Especializados

Para instruções aprofundadas, consulte os documentos de referência na pasta `references/`:

1. [Especificação Completa de Cores e Tokens](references/cores-tokens.md): Tabela de contraste WCAG, CSS variables e SCSS imports.
2. [Tipografia, Grid e Responsividade](references/tipografia-grid.md): Escala completa, regras de quebra e grid PrimeFlex de 12 colunas.
3. [Especificação Completa de Componentes de UI](references/componentes-ui.md): Código Angular/PrimeNG, estados, modelos de dados e tratamento de erros.
4. [Guia de Criação de Landing Pages](references/guia-landing-pages.md): Estrutura de Hero Section, serviços, acessibilidade e template HTML completo.
5. [Guia de Apresentações Corporativas (Slides)](references/guia-apresentacoes.md): Matrizes Dark e Light em 16:9, Big Numbers, gráficos e regras de sigilo de fotos policiais.
6. [Guia de Criação de Conteúdo em Redes Sociais](references/guia-redes-sociais.md): Formatos 4:5 e 9:16, aplicação de cores semânticas (vermelho para golpes, verde para apreensões), tipografia mobile e tom de voz institucional.
7. [BrandProfile JSON](references/brand-profile.json): Objeto canônico estruturado para uso com o ecossistema `brand-extractor`.

---

## 7. Workflow para Desenvolvimento com Frontline PF

Ao construir uma nova interface ou artefato com o Frontline PF:
1. **Determinar o Tipo de Aplicação**:
   - Sistema Interno -> Aplicar `<pf-layout>`, módulo de sensibilidade no SubHeader e tema sóbrio.
   - Portal Externo / Cidadão -> Aplicar barra Gov.br, assinatura do Ministério da Justiça e Segurança Pública e login Gov.br.
   - Landing Page / Apresentação / Post Social -> Consultar o guia especializado correspondente.
2. **Aplicar a Paleta de Cores Homologada**:
   - Base escura: `#111213` (PF-Black).
   - Realces solenes: `#E1AD62` (PF-Gold500).
   - Interações e botões primários: `#3363CC` (PF-Blue500).
3. **Respeitar o Grid de 8px e Tipografia**:
   - Validar se todos os espaçamentos são múltiplos de 8px.
   - Garantir uso da fonte Roboto e apenas 1 `<h1>` por tela sem `text-uppercase`.
