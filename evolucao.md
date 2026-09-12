# 📋 Evolução do Sistema — App Viaturas PF

> **Sistema de Controle de Entrada e Saída de Viaturas**
> Superintendência Regional da Polícia Federal no Acre (SR/PF/AC) — NTI
>
> Este documento registra cronologicamente todas as alterações realizadas no sistema desde o início de sua construção.

---

## Visão Geral do Projeto

| Item | Detalhe |
|---|---|
| **Nome do Projeto** | `app-viaturas` |
| **Versão Atual** | `1.0.0` |
| **Tecnologia Backend** | Django >= 5.2 / Python >= 3.13 |
| **Banco de Dados** | SQLite (desenvolvimento) |
| **Linter/Formatter** | Ruff |
| **Bibliotecas Principais** | Pillow, ReportLab, OpenPyXL, python-dotenv |
| **Início do Desenvolvimento** | 06/09/2026 |
| **Branch Principal** | `main` / `develop` |
| **Autor** | Juscelino Cordeiro |

---

## Histórico de Commits

### Funcionalidades de Gestão de Turnos · 12/09/2026

**Tipo:** `feat` — Gestão de Turnos, Modal e Melhorias na UI  
**Branch:** `develop`

**Descrição:**
- Implementação de Modal para encerramento de ficha com alerta de viaturas pendentes;
- Remoção da restrição `unique=True` do campo `data_expediente` (permitindo turno Dia e Noite na mesma data);
- Lógica de auto-identificação de turno (07h às 19h e 19h às 07h) ao abrir Ficha Diária;
- Bloqueio seletivo (read-only) dos dados de saída ao editar registros de viaturas em turnos diferentes;
- Auto-preenchimento via JS do odômetro da viatura na tela de saída.

---


### `[v0]` — Commit `5e0bf2d` · 06/09/2026 14:19

**Tipo:** `chore` — Inicialização do repositório  
**Branch:** `main`

**Descrição:**
Criação inicial do repositório Git com os arquivos base de configuração do projeto.

**Arquivos adicionados:**

| Arquivo | Descrição |
|---|---|
| `.gitignore` | Regras de exclusão do Git (218 linhas) |
| `LICENSE` | Licença do projeto |
| `README.md` | Arquivo README inicial (stub) |

---

### `[v1.0]` — Commit `c2eff62` · 06/09/2026 16:20

**Tipo:** `feat` — Primeira versão funcional completa  
**Branch:** `develop`

**Descrição:**
Implementação completa do sistema na sua primeira versão funcional. Criação de toda a estrutura Django com os módulos **veículos**, **fichas**, **usuários** e **dashboard**, além do design system Frontline PF e serviços de geração de relatórios.

**Módulos criados:**

#### 🔧 Core (Configurações do Django)
- `core/settings.py` — Configurações gerais do projeto Django
- `core/urls.py` — Roteamento principal da aplicação
- `core/asgi.py` / `core/wsgi.py` — Interfaces de servidor

#### 🚗 App `veiculos`
- `veiculos/models.py` — Modelos `Viatura` e `Manutencao` (232 linhas)
- `veiculos/views.py` — CRUD completo de viaturas e manutenções
- `veiculos/forms.py` — Formulários de cadastro e edição
- `veiculos/urls.py` — Rotas do módulo
- `veiculos/migrations/0001_initial.py` — Migration inicial
- `veiculos/management/commands/seed_data.py` — Comando de seed de dados para desenvolvimento

#### 📄 App `fichas`
- `fichas/models.py` — Modelos `Ficha` e `RegistroUso` (260 linhas)
- `fichas/views.py` — CRUD de fichas e registros de uso (saída/chegada)
- `fichas/forms.py` — Formulários de ficha, saída e chegada
- `fichas/urls.py` — Rotas do módulo
- `fichas/migrations/0001_initial.py` / `0002_initial.py` — Migrations iniciais

#### 👤 App `usuarios`
- `usuarios/models.py` — Modelo de usuário customizado estendendo AbstractUser
- `usuarios/views.py` — Login, logout, CRUD de usuários
- `usuarios/forms.py` — Formulário de cadastro/edição de usuários

#### 📊 App `dashboard`
- `dashboard/views.py` — Painel principal com estatísticas e gráficos (71 linhas)
- `dashboard/urls.py` — Rota do dashboard

#### 🛠️ Serviços (`services/`)
- `services/relatorios_pdf.py` — Geração de relatórios em PDF via ReportLab (358 linhas)
- `services/relatorios_excel.py` — Geração de relatórios em Excel via OpenPyXL (248 linhas)
- `services/gerar_brasao.py` — Serviço para geração/processamento do brasão da PF (82 linhas)

#### 🎨 Frontend / Templates
- `static/css/frontline.css` — Design system Frontline PF (792 linhas)
- `static/js/frontline.js` — Scripts auxiliares do frontend
- `static/img/brasao_pf.png` — Brasão oficial da Polícia Federal
- Templates completos para todos os módulos:
  - `templates/base.html` — Layout base com navbar e sidebar
  - `templates/dashboard/index.html` — Dashboard principal (331 linhas)
  - `templates/fichas/` — Formulários e listagem de fichas
  - `templates/veiculos/` — Formulários, listagem e detalhes de viaturas
  - `templates/usuarios/` — Login, cadastro e listagem de usuários

#### 🤖 Agentes / Configurações IA
- `.agents/rules/idioma.md` — Regra de idioma para agentes IA
- `.agents/skills/frontlinePF/SKILL.md` — Skill local do Design System Frontline PF (185 linhas)
- `.agents/skills/frontlinePF/references/` — Referências completas do design system

**Estatísticas do commit:**
- **78 arquivos** criados
- **7.891 linhas** de código adicionadas

---

### `[v1.0.1]` — Commit `0b9d997` · 09/09/2026 23:29

**Tipo:** `fix` — Correção de bugs nas fichas  
**Branch:** `develop`

**Descrição:**
Correção de dois problemas críticos no módulo de fichas:
1. **Edição de dados de chegada**: Sistema não permitia editar dados já registrados no retorno da viatura.
2. **Validação de clean**: Correção da validação no método `clean()` do formulário que gerava erros inconsistentes.

**Arquivos modificados:**

| Arquivo | Tipo | Linhas |
|---|---|---|
| `fichas/forms.py` | Modificado | +74 |
| `fichas/models.py` | Modificado | +21 |
| `fichas/views.py` | Modificado | +5 / -10 |
| `fichas/tests.py` | Modificado | +64 |
| `templates/fichas/registro_editar_form.html` | **NOVO** | +175 |

**Novidades:**
- ✅ Novo template `registro_editar_form.html` para edição de registros de chegada
- ✅ Testes unitários adicionados para cobrir os cenários de edição
- 🐛 Correção da validação de datas no formulário de registro

**Estatísticas:**
- **5 arquivos** modificados/criados
- **339 linhas** adicionadas / **10 linhas** removidas

---

### `[v1.1]` — Commit `04f3264` · 10/09/2026 21:25

**Tipo:** `chore` — Reorganização do Design System Frontline  
**Branch:** `develop`

**Descrição:**
Remoção da skill `frontlinePF` do repositório local do projeto (`.agents/skills/`) por ter sido promovida para o nível **global** do sistema de agentes IA. A regra local foi atualizada para referenciar a skill global.

**Arquivos alterados:**

| Arquivo | Tipo | Descrição |
|---|---|---|
| `.agents/rules/frontiline.md` | **NOVO** | Regra apontando para skill global |
| `.agents/skills/frontlinePF/` | **REMOVIDO** | Skill local removida (9 arquivos, 1.097 linhas) |

**Motivação:**
A skill do Design System Frontline PF foi consolidada como uma skill global reutilizável em todos os projetos da organização, evitando duplicação de configurações.

---

### `[v1.2]` — Commit `e8698ac` · 10/09/2026 22:58

**Tipo:** `feat` — Datas explícitas de saída e chegada  
**Branch:** `develop`  
**Co-autor:** Claude (Anthropic)

**Descrição:**
Grande atualização funcional que resolve o cenário onde uma viatura sai e retorna em **dias diferentes**. Anteriormente, as datas de saída e retorno eram implícitas (derivadas da data da Ficha). Com esta versão, cada `RegistroUso` passa a ter campos explícitos `data_saida` e `data_chegada`.

**Mudanças principais:**

#### 🗄️ Banco de Dados
- Novos campos `data_saida` e `data_chegada` em `RegistroUso`
- Migration `0003` — Adição dos campos de data
- Migration `0004` — Migração de dados (popula datas para registros existentes com base na data da Ficha)
- Migration `0002` de viaturas — Ajuste no relacionamento `Manutencao.viatura`

#### ⚙️ Backend
- `fichas/models.py` — Adicionados campos `data_saida` e `data_chegada` ao model `RegistroUso`
- `fichas/forms.py` — Formulários de saída e chegada atualizados com os novos campos de data
- `fichas/views.py` — Views refatoradas para lidar com as datas explícitas
- `fichas/urls.py` — Novas rotas adicionadas
- `dashboard/views.py` — Dashboard atualizado para refletir datas corretas

#### 🎨 Frontend
- `templates/fichas/registro_saida_form.html` — Campo de data de saída adicionado
- `templates/fichas/registro_chegada_form.html` — Campo de data de chegada adicionado
- `templates/fichas/registro_editar_form.html` — Suporte a edição de datas
- `static/css/frontline.css` — +102 linhas de estilos adicionais

#### 📄 Novos Templates de Erro
- `templates/403.html` — Página de acesso negado
- `templates/404.html` — Página não encontrada
- `templates/500.html` — Página de erro interno do servidor

#### 📋 Relatórios
- `services/relatorios_pdf.py` — Relatórios atualizados para exibir datas explícitas
- `services/relatorios_excel.py` — Planilhas atualizadas

#### 🔧 Infraestrutura e Configuração
- `core/settings.py` — Refatoração e melhorias nas configurações
- `pyproject.toml` — Dependências e configurações do Ruff atualizadas
- `.env.example` — Arquivo de exemplo de variáveis de ambiente criado
- `README.md` — Documentação expandida de 1 para 151 linhas

#### ✅ Testes
- `fichas/tests.py` — Novos testes para datas explícitas
- `dashboard/tests.py` — Testes do dashboard expandidos (+111 linhas)
- `usuarios/tests.py` — Testes de usuários expandidos (+95 linhas)
- `veiculos/tests.py` — Testes de veículos atualizados

**Estatísticas:**
- **61 arquivos** modificados/criados
- **2.044 linhas** adicionadas / **1.154 linhas** removidas

---

### `[v1.2.1]` — Commit `a31afaa` · 10/09/2026 23:20

**Tipo:** `feat(ui)` — Atualização de identidade visual  
**Branch:** `develop` / `ft_review`  
**Co-autor:** Claude (Anthropic)

**Descrição:**
Atualização da identidade visual da aplicação para refletir corretamente a **Superintendência Regional da Polícia Federal no Acre (SR/PF/AC)** e o setor **NTI**, substituindo referências genéricas ao órgão nacional.

**Arquivos modificados:**

| Arquivo | Tipo | Descrição |
|---|---|---|
| `static/img/brasao_pf.png` | Substituído | Brasão atualizado (11.730 → 124.916 bytes) |
| `templates/base.html` | Modificado | Título e footer atualizados para SR/PF/AC |
| `templates/usuarios/login.html` | Modificado | Tela de login com nova identidade visual |

**Impacto visual:**
- 🏛️ Brasão oficial da PF substituído por versão regional de maior resolução
- 🏷️ Título da aplicação reflete a Superintendência Regional do Acre
- 📝 Rodapé atualizado com o nome do setor de TI (NTI)

**Estatísticas:**
- **3 arquivos** modificados
- **7 linhas** adicionadas / **9 linhas** removidas

---

### `[v1.2.2]` — Commit `be263ca` · 10/09/2026 23:32

**Tipo:** `feat(agentes)` — Regra de idioma para commits  
**Branch:** `develop` / `ft_review` / `ft_perfil`  
**Co-autor:** Claude (Anthropic)

**Descrição:**
Adição de regra de comportamento para os agentes IA garantindo que todas as mensagens de commit geradas automaticamente sejam escritas em **português do Brasil**.

**Arquivo adicionado:**

| Arquivo | Descrição |
|---|---|
| `.agents/rules/idioma-commit.md` | Regra que instrui o agente a gerar commits em pt-BR |

**Motivação:**
Padronização do histórico de commits do projeto em idioma português, alinhando com as boas práticas de comunicação da equipe.

---

### `[v1.3]` — Commit `d769b3d` · 12/09/2026 16:12

**Tipo:** `feat(accesscontrol)` — Implementação de Sistema RBAC  
**Branch:** `develop`  
**Co-autor:** Claude (Anthropic)

**Descrição:**
Implementação do sistema de Controle de Acesso Baseado em Papéis (RBAC - Role-Based Access Control) granular, substituindo o campo legado de perfil. A arquitetura foi desenvolvida para permitir o controle minucioso do acesso a módulos, submódulos e ações, vinculados a perfis, suportando múltiplos perfis por usuário com auditoria.

**Mudanças principais:**

#### 🔒 App `accesscontrol` (Novo)
- `models.py` — Criação dos modelos `Modulo`, `Submodulo`, `Acao` (com código desnormalizado), `Perfil`, `UsuarioPerfil` (through table com auditoria), `DashboardWidget` e `LogAcesso`.
- `services.py` — Serviço de permissões (`obter_codigos_permissao`, `tem_permissao`) com cache via `LocMemCache` (15 minutos).
- `signals.py` — Invalidação automática do cache via signals `post_save`, `post_delete` e `m2m_changed`.
- `middleware.py` — `PermissaoMiddleware` para bloqueio transparente lendo atributos das views e registro de acessos negados no `LogAcesso`.
- `decorators.py` — Decorador `@requer_permissao` para function-based views.
- `templatetags/permissoes.py` — Tag customizada `{% tem_perm "codigo" as var %}` para ocultar elementos visuais (botões, menus).
- `context_processors.py` — Injeção de `modulos_menu`, `codigos_permissao` e `widgets_dashboard` globais.
- `migrations/seeders.py` — Constantes para popular a base.
- `migrations/0002_seed_perfis.py` — Migration para popular 3 módulos, 24 ações, 5 perfis padronizados (vigilante, nutran, inteligencia, chefia, administrador) e migrar usuários legados de forma idempotente.
- `management/commands/setup_permissoes.py` — Comando CLI para reconstruir e resetar a estrutura de permissões no banco de dados sem efeitos colaterais.

#### 👤 App `usuarios`
- `models.py` — Remoção do antigo campo estático `perfil` e adição dos métodos `tem_permissao()` e `listar_perfis()`.
- `views.py` — Proteção de todas as views com RBAC, criação da nova tela de atribuição de perfis por usuário (`usuario_perfis_gerenciar`) com auditoria de atribuição/remoção e a tela do usuário `meu_perfil`.
- `migrations/0002_remove_perfil_field.py` — Remoção do campo CharField `perfil`.

#### 🚗 Apps `veiculos` e `fichas`
- `views.py` — Substituição do decorador padrão `@login_required` para o decorador `@requer_permissao` com códigos de permissão granulares em todas as views.

#### 🎨 Frontend / Templates
- `templates/base.html` — Menu lateral adaptado para ser gerado dinamicamente validando as permissões do usuário.
- `templates/usuarios/lista.html` — Listagem de usuários adaptada para mostrar a lista de perfis do usuário ao invés do perfil legado único. Botões de ação ocultados usando template tag condicionais `{% tem_perm %}`.
- Novos templates: `templates/usuarios/perfis.html` (para gerenciamento das atribuições de perfil por admin) e `templates/usuarios/meu_perfil.html`.

**Estatísticas:**
- **34 arquivos** modificados/criados
- **2.568 linhas** adicionadas / **96 linhas** removidas

---

## Resumo Estatístico Geral

| Métrica | Valor |
|---|---|
| **Total de commits** | 8 |
| **Período de desenvolvimento** | 06/09/2026 a 12/09/2026 (7 dias) |
| **Total de arquivos criados/modificados** | 180+ |
| **Total de linhas adicionadas** | ~12.800+ |
| **Módulos Django** | 6 (core, veiculos, fichas, usuarios, dashboard, accesscontrol) |
| **Apps de serviço** | 1 (services/) |
| **Templates HTML** | 19+ |
| **Migrations** | 10 |
| **Branches utilizadas** | main, develop, ft_review, ft_perfil |

---

## Arquitetura do Sistema

```
app_viaturas/
├── core/               # Configurações e roteamento principal
├── accesscontrol/      # Infraestrutura RBAC (papéis e permissões)
├── veiculos/           # Gestão de viaturas e manutenções
├── fichas/             # Registro de saída e chegada de viaturas
├── usuarios/           # Autenticação e gestão de usuários
├── dashboard/          # Painel de controle e estatísticas
├── services/           # Geração de relatórios PDF/Excel e brasão
├── static/             # CSS (Frontline PF), JS, imagens
│   ├── css/frontline.css
│   ├── js/frontline.js
│   └── img/brasao_pf.png
├── templates/          # Templates HTML organizados por módulo
└── .agents/            # Regras e configurações para agentes IA
```

---

## Tecnologias e Dependências

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | >= 3.13 | Linguagem de programação |
| Django | >= 5.2 | Framework web principal |
| Pillow | >= 11.0 | Processamento de imagens |
| ReportLab | >= 4.0 | Geração de relatórios PDF |
| OpenPyXL | >= 3.1 | Geração de planilhas Excel |
| python-dotenv | >= 1.0 | Gerenciamento de variáveis de ambiente |
| Ruff | — | Linter e formatter Python |
| SQLite | — | Banco de dados (desenvolvimento) |

---

## Branches do Projeto

| Branch | Status | Descrição |
|---|---|---|
| `main` | Produção | Branch estável, versão inicial do repositório |
| `develop` | Ativo | Branch principal de desenvolvimento |
| `ft_review` | Ativo | Feature branch para revisões |
| `ft_perfil` | Ativo | Feature branch para perfil de usuário |

---

*Documento gerado automaticamente com base no histórico de commits do repositório.*  
*Última atualização: 12/09/2026*
