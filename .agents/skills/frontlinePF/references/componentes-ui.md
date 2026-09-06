# Frontline PF — Especificação Completa de Componentes de UI

O Frontline estabelece uma biblioteca rica de componentes especializados desenvolvidos em Angular e integrados ao PrimeNG / PrimeFlex, divididos em dois ecossistemas estruturais:
1. **Sistemas Corporativos Internos (Intranet PF)**
2. **Portais de Acesso Externo ao Cidadão (Gov.br + Identidade Frontline PF)**

---

## 1. Estrutura de Layout e Casca da Aplicação

### 1.1. Layout Corporativo Interno (`<pf-layout>`)
Utilizado obrigatoriamente como estrutura base de todas as aplicações internas da Polícia Federal.

```html
<!-- app.component.html -->
<pf-layout [config]="layoutConfig"></pf-layout>
```

#### Anatomia dos 4 Pilares:
1. **Header**:
   - Nome oficial do sistema (em destaque à esquerda).
   - Perfil do usuário autenticado (foto, nome completo, email corporativo).
   - Ícone de Notificações com contador de badge dinâmico e gaveta lateral de alertas.
   - Botão de logout integrado com o Keycloak da PF.
2. **SubHeader**:
   - Identificação do módulo ou subsetor operacional ativo.
   - Perfil de acesso do operador (ex: Administrador, Perito, Agente, Escrivão).
   - Indicador de tipo de módulo: `1 - Comum`, `2 - Sensível` (com alerta de sigilo).
   - Seletor de troca de módulo / unidade regional.
3. **Sidebar (Menu Principal)**:
   - Largura máxima padrão de até **338px** (respeitando múltiplos de 8px).
   - Itens de nível 1 acompanhados de ícones FontAwesome (ex: `fas fa-home`, `fas fa-folder-open`).
   - Subitens agrupados sem ícones para evitar ruído visual.
   - Comportamento de sanfona (accordion): ao abrir um menu, os demais se fecham automaticamente.
   - Botão inferior/superior para recolher/expandir a barra lateral.
   - Limite recomendado: **máximo de 10 itens principais** no primeiro nível.
4. **Footer (Rodapé Fixo)**:
   - Sempre visível, fixo na parte inferior da tela e abaixo da sidebar.
   - Nome e sigla do sistema.
   - Link direto "Fale com a equipe" (`/frontline/contact-us`).
   - Link para o Guia do Usuário / Manual Operacional.
   - Identificação da versão da aplicação (ex: `v2.4.1` em fonte Roboto 10px com letter-spacing 10%).

---

### 1.2. Layout de Acesso Externo (Gov.br + Frontline)
Utilizado para portais e serviços voltados a cidadãos e entidades externas (ex: emissão de passaportes, certidões de antecedentes, Sinarm).

```typescript
// Interface oficial: PfLayoutInternetModel
export interface PfLayoutInternetModel {
  title: string;                  // Nome do sistema externo
  version: string;                // Versão da aplicação
  linkVersion?: string;           // URL com changelog
  menu: MenuItem[];               // Itens de navegação principal
  links?: MenuItem[];             // Links de acesso rápido
  headerIconsMenu?: MenuItem[];   // Ícones utilitários no topo
  showSocialNetworks?: boolean;   // Exibir links para redes oficiais da PF
  user?: { name: string; email?: string }; // Usuário Gov.br logado
  redirectUrlLogout?: string;     // Retorno após encerramento de sessão
}
```

#### Boas Práticas do Acesso Externo:
- **Barra Superior Gov.br**: Logo oficial do Gov.br, atalhos de acessibilidade (Alt+1 ao Alt+4), alto contraste e VLibras.
- **Assinatura Ministerial**: Identificação do **Ministério da Justiça e Segurança Pública**.
- **Título Institucional**: "Polícia Federal" como título principal e o nome do serviço público como subtítulo.
- **Área de Autenticação**: Botão de login "Entrar com gov.br".
- **Rodapé Externo**: Não fixo (rola com a página), exibindo marcas de Acesso à Informação, Governo Federal e Brasão da Polícia Federal.

---

## 2. Sistema de Botões (Button System)

Os botões do Frontline comunicam ações e hierarquias com clareza imediata.

### 2.1. Tamanhos de Botão
- **Large (`32px` de altura)**: Botão de **uso preferencial**. Alinha-se harmoniosamente com os campos de formulário do Frontline.
- **Small (`24px` de altura)**: Desenvolvido estritamente para espaços reduzidos, como células de tabelas (`TableCustom`) e filtros compactos.

### 2.2. Estilos e Hierarquia

| Estilo | Visual / Tokens | Regra de Uso |
|:---|:---|:---|
| **Primary** | Fundo `#3363CC` (PF-Blue500), texto branco | **Ação Principal**. Usar apenas **1 por página ou modal**. Representa avançar, salvar, emitir, confirmar. |
| **Secondary** | Fundo neutro claro (`#DADADD` / `#ECEDEE`), texto escuro | Ações de suporte em formulários sem poluir a tela. |
| **Outline** | Borda `1px solid #3363CC`, fundo transparente | **Ação Intermediária**. Usar exclusivamente em grupos com 3 ou mais botões. Nunca utilizar isolado. |
| **Ghost** | Sem borda, fundo transparente, comportamento de link | **Ação de Menor Hierarquia / Retorno**. Cancelar, voltar, fechar. Pode ser agrupado com outro Ghost. |

### 2.3. Regras Oficiais de Agrupamento

1. **Composição de 2 Opções (Alto Contraste)**:
   ```html
   <!-- Primary + Ghost: máxima clareza entre ação principal e cancelamento -->
   <div class="p-d-flex p-jc-end p-ai-center">
     <button class="pf-button pf-button-ghost p-mr-2">Cancelar</button>
     <button class="pf-button pf-button-primary">Salvar Processo</button>
   </div>
   ```
2. **Composição de Opções Neutras**:
   ```html
   <!-- Ghost + Ghost: ações de mesmo peso secundário -->
   <button class="pf-button pf-button-ghost">Limpar Filtros</button>
   <button class="pf-button pf-button-ghost">Exportar CSV</button>
   ```
3. **Composição de 3 ou Mais Opções**:
   ```html
   <!-- Primary + Outline + Ghost: hierarquia tripla perfeita -->
   <div class="p-d-flex p-jc-end p-ai-center">
     <button class="pf-button pf-button-ghost p-mr-2">Voltar</button>
     <button class="pf-button pf-button-outline p-mr-2">Salvar Rascunho</button>
     <button class="pf-button pf-button-primary">Finalizar e Enviar</button>
   </div>
   ```

---

## 3. Componentes de Formulários e Validação

O Frontline utiliza a classe `.p-field` como bloco atômico. A distância entre o Label e o Input deve ser rigorosamente de **8px (`0.5rem`)**.

```html
<div class="p-fluid p-formgrid p-grid">
  <!-- Campo de Texto Simples -->
  <div class="p-field p-col-12 p-md-6">
    <label for="nome">Nome Completo</label>
    <input id="nome" type="text" class="pf-inputtext" />
    <small class="pf-help-text">Informe o nome conforme documento de identificação.</small>
  </div>

  <!-- Campo com Erro de Validação -->
  <div class="p-field p-col-12 p-md-6">
    <label for="doc">CPF do Requerente</label>
    <input id="doc" type="text" class="pf-inputtext pf-error" />
    <small class="pf-error-message">
      <i class="fas fa-exclamation-circle"></i> CPF inválido ou não cadastrado na base da Receita.
    </small>
  </div>
</div>
```

### 3.1. Inputs Especializados com Máscara Integrada
- **`InputCPF`**: Validação algorítmica de dígitos verificadores e máscara automática `999.999.999-99`.
- **`InputCNPJ`**: Validação de pessoa jurídica e máscara `99.999.999/9999-99`.
- **`InputCPF/CNPJ`**: Campo híbrido inteligente que detecta a quantidade de dígitos digitados e alterna dinamicamente a máscara.
- **`InputCEP`**: Formatação `99999-999` com autopreenchimento de logradouro via catálogo de serviços corporativo.
- **`Crop` e `UploadImage`**: Componente de captura e recorte com proporções pré-definidas para fotos de passaporte, mandados ou cadastro biométrico de custodiados.

---

## 4. Componentes de Dados e Navegação de Processos

### 4.1. Table Custom (`<pf-table-custom>`)
Projetada para buscas operacionais com múltiplos níveis hierárquicos:
- **Paginator Superior e Inferior**: Recomendado em tabelas com mais de 20 registros por página para evitar que o operador precise rolar até o fim para avançar.
- **Linhas Zebradas**: Linhas alternadas com fundo `#ECEDEE` (`PF-Grey100`) para leitura contínua sem fadiga visual.
- **Ações Rápidas por Linha**: Botões small (`24px`) com ícones para visualização de detalhes, edição e impressão.

### 4.2. Steps (`<pf-steps>`)
- Utilizado para fluxos lineares e cadastros em etapas (ex: solicitação de passaporte ou credenciamento).
- **Regras de Negócio**:
  - Limite recomendado: **máximo de 10 etapas**.
  - Validação estrita: O botão "Avançar" só é liberado se todos os campos obrigatórios da etapa atual estiverem validados.
  - Botão "Voltar" obrigatório em todas as etapas, com exceção da primeira.

### 4.3. Timeline (`<pf-timeline>`)
- Exibição cronológica de auditoria e tramitação processual (ex: Instauração de IPL, Diligências, Despachos, Conclusão de Relatório).
- Formatos de card:
  - `Título + Data`
  - `Título + Data + Conteúdo`
  - `Título + Data + Subtítulo + Anexos`

---

## 5. Tratamento de Erros e Página de Erro Oficial

O Frontline disponibiliza o módulo `PfErrorModule` e o serviço `PfErrorService` para padronização de mensagens de contingência:

### 5.1. Anatomia da Página de Erro
1. **Código de Estado**: 3 dígitos seguidos de hífen e título oficial em português (ex: `401 - Acesso Não Autorizado`, `403 - Acesso Proibido`, `404 - Página Não Encontrada`, `500 - Erro Interno do Servidor`, `504 - Tempo Limite da Porta de Entrada`).
2. **Descrição do Erro**: Explicação objetiva e não técnica do que ocorreu.
3. **Parágrafo de Solução**: Orientações claras de contingência (ex: "Verifique suas credenciais de acesso ou tente recarregar a página").
4. **Botões de Ação**: Botão primário para tentar novamente / recarregar e botão secundário opcional para acionar suporte técnico.
5. **Brasão da Polícia Federal**: Inserido com área de respiro e tamanho institucional.

```typescript
// Exemplo de acionamento via PfErrorService
this.pfErrorService.showErrorPage({
  statuCode: '403 - Acesso Restrito',
  description: 'Você não possui as permissões necessárias para acessar este módulo de investigação.',
  paragraphSolution: 'Solicite a habilitação do perfil junto à chefia da sua unidade ou administrador de TI.',
  labelButton: 'Voltar ao Início',
  iconButton: 'fas fa-home',
  labelButton2: 'Falar com Suporte',
  iconButton2: 'fas fa-headset',
  buttonClick: () => this.router.navigate(['/home']),
  button2Click: () => window.open('https://projetos.dpf.gov.br/redmine2/projects/agil-frontline', '_blank')
});
```
