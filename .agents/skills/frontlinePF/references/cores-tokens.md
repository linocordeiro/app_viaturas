# Frontline PF — Especificação Completa de Cores e Design Tokens

A paleta de cores do Frontline da Polícia Federal foi projetada para conferir alto contraste, sobriedade, legibilidade e acessibilidade (aderente aos padrões WCAG 2.1 AA e e-MAG), além de reforçar a identidade visual histórica da corporação baseada no preto profundo, dourado brasão e azul técnico.

---

## 1. Cores Primárias

As cores primárias compõem os elementos centrais de identificação visual, cabeçalhos, barras de navegação, ações de maior hierarquia e destaques institucionais.

### 1.1. PF-BLACK
Utilizado como cor base para fundos escuros de headers, footers, elementos de autoridade e textos de maior contraste.

| Nome Token | HEX | RGB | Cor do Texto Recomendada | Uso / Aplicação |
|:---|:---:|:---:|:---:|:---|
| **PF-Black** | `#111213` | `17, 18, 19` | `#FFFFFF` | Fundo de cabeçalhos institucionais, navbar, tema escuro e textos de alto contraste |
| **PF-Black200** | `#2A2A2A` | `42, 42, 42` | `#FFFFFF` | Superfícies elevadas em dark mode, cards secundários, sidebars escuras |
| **PF-Black100** | `#373C42` | `55, 60, 66` | `#FFFFFF` | Linhas divisórias em dark mode, bordas de cards escuros e elementos desativados |

### 1.2. PF-GOLD
O dourado representa a tradição, o brasão da Polícia Federal e os destaques solenes. O tom **PF-Gold500** é o padrão oficial.

| Nome Token | HEX | RGB | Cor do Texto Recomendada | Uso / Aplicação |
|:---|:---:|:---:|:---:|:---|
| **PF-Gold700** | `#856404` | `133, 100, 4` | `#FFFFFF` | Texto escuro de alerta sobre fundos dourados claros, estados ativos |
| **PF-Gold600** | `#C19515` | `193, 149, 21` | `#FFFFFF` | Hover e foco de botões dourados, bordas de destaque forte |
| **PF-Gold500** *(Padrão)* | `#E1AD62` | `225, 173, 98` | `#111213` / `#FFFFFF` | **Ouro Oficial PF**. Detalhes do brasão, divisores finos de header, badges nobres |
| **PF-Gold400** | `#F2B64E` | `242, 182, 78` | `#856404` | Realces intermediários, ícones de aviso e atenção |
| **PF-Gold300** | `#F7CE68` | `247, 206, 104` | `#856404` | Destaques sutis em tabelas e seleções |
| **PF-Gold200** | `#FFEBB9` | `255, 235, 185` | `#856404` | Badges de status pendente, fundos suaves de atenção |
| **PF-Gold100** | `#FFF8E3` | `255, 248, 227` | `#856404` | Fundo de caixas de mensagens informativas/alerta |

### 1.3. PF-BLUE
O azul técnico representa a precisão, funcionalidade e links interativos de sistemas corporativos e do Gov.br.

| Nome Token | HEX | RGB | Cor do Texto Recomendada | Uso / Aplicação |
|:---|:---:|:---:|:---:|:---|
| **PF-Blue700** | `#0F4B8B` | `15, 75, 139` | `#FFFFFF` | Botão primário em estado pressionado/active, cabeçalhos de tabelas densas |
| **PF-Blue600** | `#1F628D` | `31, 98, 141` | `#FFFFFF` | Hover de botões primários e links em foco |
| **PF-Blue500** *(Padrão)* | `#3363CC` | `51, 99, 204` | `#FFFFFF` | **Ação Primária Oficial**. Botões principais, links ativos, badges de status informativo |
| **PF-Blue400** | `#367ECC` | `54, 126, 204` | `#FFFFFF` | Variações claras de botões e ícones interativos |
| **PF-Blue300** | `#78ABE0` | `120, 171, 224` | `#0F4B8B` | Indicadores de seleção e foco acessível |
| **PF-Blue200** | `#A1C6ED` | `161, 198, 237` | `#0F4B8B` | Fundo de tags ativas e chips |
| **PF-Blue100** | `#CFDBE8` | `207, 219, 232` | `#0F4B8B` | Fundo de caixas informativas e linhas alternadas de tabelas |

---

## 2. Cores Secundárias (Apoio e Semânticas)

As cores secundárias garantem a comunicação de status do sistema (sucesso, erro, alerta, neutros de leitura).

### 2.1. PF-GREY (Escala Neutra)
Essencial para hierarquia de texto, superfícies de formulários, bordas e divisores.

| Nome Token | HEX | RGB | Cor do Texto | Uso / Aplicação |
|:---|:---:|:---:|:---:|:---|
| **PF-Grey700** | `#41434E` | `65, 67, 78` | `#FFFFFF` | Títulos h1-h4, texto corrido padrão em fundo claro |
| **PF-Grey600** | `#555868` | `85, 88, 104` | `#FFFFFF` | Textos secundários, legendas de inputs, descrições auxiliares |
| **PF-Grey500** *(Padrão)* | `#6A6D7C` | `106, 109, 124` | `#FFFFFF` | Ícones inativos, texto desabilitado, bordas neutras |
| **PF-Grey400** | `#8E919F` | `141, 151, 160` | `#FFFFFF` | Placeholders de formulário e bordas de containers secundários |
| **PF-Grey300** | `#BDBEC3` | `189, 190, 195` | `#41434E` | Borda padrão de inputs desmarcados |
| **PF-Grey200** | `#DADADD` | `218, 218, 221` | `#41434E` | Linhas divisórias de tabela, separadores horizontais |
| **PF-Grey100** | `#ECEDEE` | `236, 237, 238` | `#41434E` | Fundo de cards neutros, zebrado de tabelas |

### 2.2. PF-GREEN (Semântico - Sucesso e Confirmação)
Indica operações concluídas com êxito, aprovações, status regulares e certidões válidas.

| Nome Token | HEX | RGB | Cor do Texto | Uso / Aplicação |
|:---|:---:|:---:|:---:|:---|
| **PF-Green700** | `#3C6841` | `60, 104, 65` | `#FFFFFF` | Texto escuro sobre fundos verdes claros |
| **PF-Green600** | `#287831` | `40, 120, 49` | `#FFFFFF` | Hover de botões de confirmação/sucesso |
| **PF-Green500** *(Padrão)* | `#33A841` | `51, 168, 65` | `#FFFFFF` | **Status Sucesso Oficial**. Ícones de check, badges regulares |
| **PF-Green400** | `#2DC73F` | `45, 199, 63` | `#FFFFFF` | Destaque gráfico em dashboards |
| **PF-Green300** | `#8CC89D` | `140, 200, 157` | `#3C6841` | Bordas de caixas de sucesso |
| **PF-Green200** | `#BAE2B8` | `186, 226, 184` | `#3C6841` | Badges e chips de aprovação |
| **PF-Green100** | `#DDECDC` | `221, 236, 220` | `#3C6841` | Fundo de mensagens de sucesso (alert-success) |

### 2.3. PF-RED (Semântico - Erro, Crítico e Ações Destrutivas)
Indica falhas de validação, bloqueios de sistema, erros 401/403/404/500 e ações irreversíveis (como exclusão de registros).

| Nome Token | HEX | RGB | Cor do Texto | Uso / Aplicação |
|:---|:---:|:---:|:---:|:---|
| **PF-Red700** | `#6E363B` | `110, 54, 59` | `#FFFFFF` | Texto escuro sobre fundos vermelhos claros |
| **PF-Red600** | `#921F2A` | `146, 31, 42` | `#FFFFFF` | Hover de botão de exclusão/perigo |
| **PF-Red500** *(Padrão)* | `#BF0C1D` | `191, 12, 29` | `#FFFFFF` | **Status Erro Oficial**. Validação `.pf-error`, mensagens de erro |
| **PF-Red400** | `#D85965` | `216, 89, 101` | `#FFFFFF` | Ícones de alerta crítico |
| **PF-Red300** | `#DD959C` | `221, 149, 156` | `#6E363B` | Bordas de campos com erro |
| **PF-Red200** | `#E5C0C3` | `229, 192, 195` | `#6E363B` | Badges de status rejeitado ou cancelado |
| **PF-Red100** | `#F8E8EA` | `248, 232, 234` | `#6E363B` | Fundo de caixas de erro crítico (alert-danger) |

---

## 3. Tokens de Superfície (Surfaces)

O Frontline adota o sistema de superfícies para controle de elevação e profundidade:

```css
:root {
  --surface-0: #ffffff;    /* Fundo de página claro */
  --surface-50: #eef1f2;   /* Fundo suave de seções */
  --surface-100: #dde2e4;  /* Cards em repouso */
  --surface-200: #bbc5ca;  /* Bordas sutis */
  --surface-300: #98a8af;  /* Divisores médios */
  --surface-400: #768b95;  /* Elementos neutros */
  --surface-500: #546e7a;  /* Ícones de interface */
  --surface-600: #435862;  /* Superfícies escuras */
  --surface-700: #324249;  /* Modais escuros */
  --surface-800: #222c31;  /* Sidebar dark */
  --surface-900: #111618;  /* Background escuro profundo */
}
```

---

## 4. Como Importar nos Projetos

### 4.1. Importação Oficial SCSS
No arquivo principal de estilos (`styles.scss`):

```scss
@import "~pf-frontline/assets/scss/pf-colors";
```

### 4.2. Classes Utilitárias Prontas no Frontline
O Frontline disponibiliza classes para estilização direta:

- **Cores de Texto**: `.pf-black`, `.pf-gold-500`, `.pf-blue-500`, `.pf-grey-700`, `.pf-grey-600`, `.pf-green-500`, `.pf-red-500`.
- **Estados de Validação**: `.pf-error` (aplica cor vermelha `#BF0C1D` e borda de erro nos inputs).
- **Subtextos**: `.pf-text-secondary` (aplica `#6A6D7C`).

---

## 5. Diretrizes de Contraste e Acessibilidade (WCAG 2.1 AA)

1. **Rácio de Contraste Mínimo**:
   - Texto normal (< 18pt ou < 14pt bold): rácio mínimo de **4.5:1** em relação ao fundo.
   - Texto grande (≥ 18pt ou ≥ 14pt bold): rácio mínimo de **3.0:1**.
2. **Uso de PF-Gold500 (`#E1AD62`)**:
   - Quando aplicado sobre fundo claro (`#FFFFFF`), utilizar **PF-Gold700 (`#856404`)** para texto ou badges para garantir legibilidade.
   - Sobre fundo escuro (**PF-Black `#111213`**), o **PF-Gold500** atinge contraste pleno e acabamento visual nobre.
3. **Não confiar unicamente na cor para transmitir estado**:
   - Mensagens de erro (`.pf-error`) devem sempre acompanhar um ícone informativo (`fas fa-exclamation-circle`) e texto descritivo explicativo.
