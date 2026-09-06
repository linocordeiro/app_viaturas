# Frontline PF — Tipografia, Grid e Responsividade

A padronização tipográfica e espacial do Frontline garante ritmo visual, clareza hierárquica e coerência entre todas as aplicações da Polícia Federal.

---

## 1. Famílias Tipográficas Oficiais

| Papel | Família de Fonte | Pesos Utilizados | Origem / Referência |
|:---|:---|:---|:---|
| **Primária** | **Roboto** | Regular (400), Medium (500), Bold (700) | Google Fonts (`font-family: 'Roboto', sans-serif;`) |
| **Secundária / Apoio** | **Open Sans** | Regular (400), SemiBold (600), Bold (700) | Google Fonts (`font-family: 'Open Sans', sans-serif;`) |
| **Ícones** | **Font Awesome 5 Free** & **PrimeIcons** | Regular / Solid | `fas fa-*`, `far fa-*` e `pi pi-*` |

```css
/* Definição de fallback global */
body, .pf-component {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.42857;
  color: #41434E; /* PF-Grey700 */
}
```

---

## 2. Escala Tipográfica Frontline

A escala do Frontline adota o tamanho base de **16px** (`1rem`) para títulos estruturais e **14px** para corpos de sistema:

### 2.1. Cabeçalhos (Headings)

| Elemento | Tamanho (px) | Tamanho (em/rem) | Peso | Line-Height | Uso Recomendado |
|:---|:---:|:---:|:---:|:---:|:---|
| `h1` | `36px` | `2.25em` / `2.25rem` | Bold (700) | `40px` | **Título Principal da Página** (máximo 1 por página) |
| `h2` | `30px` | `1.875em` / `1.875rem` | Bold (700) | `36px` | Títulos de grandes seções do sistema |
| `h3` | `24px` | `1.5em` / `1.5rem` | Medium (500) | `30px` | Cabeçalhos de cards principais e formulários |
| `h4` | `20px` | `1.25em` / `1.25rem` | Medium (500) | `26px` | Subseções, títulos de modais e painéis |
| `h5` | `16px` | `1.0em` / `1.0rem` | Medium (500) | `22px` | Agrupamentos de campos, subpainéis |
| `h6` | `12px` | `0.75em` / `0.75rem` | Medium (500) | `16px` | Legendas técnicas, tags menores |

### 2.2. Textos de Corpo e Elementos de Interface

| Estilo / Elemento | Tamanho (px) | Peso | Line-Height | Letter-Spacing | Uso / Aplicação |
|:---|:---:|:---:|:---:|:---:|:---|
| **Body Default** | `14px` | Regular (400) | `16px` / `20px` | Normal | Texto padrão de parágrafos, inputs e tabelas |
| **Body Small** | `12px` | Regular (400) | `16px` | Normal | Mensagens de ajuda, breadcrumb, notas de rodapé |
| **Table Header** | `14px` | Medium (500) | `16px` | Normal | Cabeçalho de colunas em tabelas (`th`) |
| **Table Row** | `14px` | Regular (400) | `16px` | Normal | Linhas de dados em tabelas (`td`) |
| **Menu Label** | `14px` | Medium (500) | `16px` | `0.125em` (12.5%) | Itens principais do menu lateral |
| **Menu Title** | `12px` | Medium (500) | `16px` | `0.125em` (12.5%) | Títulos de agrupamentos no menu lateral |
| **Footer Version** | `10px` | Regular (400) | `12px` | `0.100em` (10.0%) | Marcação de versão no rodapé do sistema |

---

## 3. Boas Práticas Tipográficas

1. **Apenas um `<h1>` por página**: O título principal deve ser unívoco e refletir diretamente o objetivo da tela.
2. **Hierarquia sem saltos**: Não pular níveis hierárquicos (ex: saltar de `h1` diretamente para `h4`).
3. **Evitar `text-uppercase`**:
   - Não utilizar caixa alta em headers, menus e botões. O uso excessivo de maiúsculas reduz a legibilidade e transmite um tom agressivo inadequado ao design institucional sóbrio.
4. **Alinhamento**: Priorizar alinhamento à esquerda em textos corridos. Justificar apenas em apresentações solenes ou relatórios técnicos diagramados.

---

## 4. O Sistema de Grid de 8px (8px Grid System)

Todos os componentes, margens e espaçamentos (verticais e horizontais) no Frontline são estritamente fundamentados em **múltiplos de 8px** (`8px`, `16px`, `24px`, `32px`, `40px`, `48px`, `64px`):

```
+---+---+---+---+---+---+---+---+
| 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |  --> Escala Modular
+---+---+---+---+---+---+---+---+
  8px  16px  24px  32px  40px ...
```

### 4.1. Espaçamentos Chave em Formulários
- **Label até o Input**: `8px` (`0.5rem`).
- **Distância Horizontal entre Campos no FormGrid**: `16px` (`1rem`).
- **Distância Vertical entre Linhas de Formulário (`.p-fluid`)**: `32px` (`2rem`).
- **Padding interno padrão de botões e inputs**: múltiplos de `8px`.

### 4.2. Por que 8px?
- **Para Designers**: Menos decisões arbitrárias; ritmo visual harmônico e previsível.
- **Para Desenvolvedores**: Eliminação de dúvidas sobre medidas exatas de pixels; fácil percepção visual.
- **Para Usuários**: Consistência estética e conforto ergonômico em qualquer resolução.

---

## 5. Breakpoints e Grid Responsivo (PrimeFlex)

O Frontline integra a biblioteca PrimeFlex para o layout fluido em 12 colunas (`.p-grid`, `.p-col-*`):

| Breakpoint | Prefixo PrimeFlex | Resolução Mínima | Dispositivos Alvo |
|:---|:---:|:---:|:---|
| **Small (sm)** | `.p-sm-*` | `576px` | Smartphones em modo paisagem e telas compactas |
| **Medium (md)** | `.p-md-*` | `768px` | Tablets e telas intermediárias |
| **Large (lg)** | `.p-lg-*` | `992px` | Laptops e monitores desktop padrão |
| **Extra Large (xl)** | `.p-xl-*` | `1200px` | Monitores widescreen de alta resolução |

### 5.1. Exemplo de Grid Responsivo Frontline
```html
<div class="p-grid p-formgrid">
  <!-- Ocupa 12 colunas no celular, 6 no tablet, 4 no desktop -->
  <div class="p-col-12 p-md-6 p-lg-4">
    <div class="p-field">
      <label for="campo1">Número do Processo</label>
      <input id="campo1" type="text" class="pf-inputtext" />
    </div>
  </div>
  <div class="p-col-12 p-md-6 p-lg-4">
    <div class="p-field">
      <label for="campo2">Unidade PF</label>
      <input id="campo2" type="text" class="pf-inputtext" />
    </div>
  </div>
  <div class="p-col-12 p-md-12 p-lg-4">
    <div class="p-field">
      <label for="campo3">Status</label>
      <input id="campo3" type="text" class="pf-inputtext" />
    </div>
  </div>
</div>
```

---

## 6. Dimensões de Layout

- **Largura máxima da Sidebar (Menu)**: padrão de até **338px** (múltiplo de 8px + espaçamento do grid).
- **Altura do Header Corporativo**: `64px` a `72px` (múltiplos de 8px).
- **Altura do Rodapé**: `48px` a `56px` (fixo na base e abaixo da sidebar).
