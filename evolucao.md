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

### Integração da Branch ft_review com Resolução de Conflitos e Padronização de Tabelas · 04/10/2026

**Tipo:** `merge` / `refactor` / `feat` — Conclusão do Merge da Branch `ft_review` na `develop`  
**Branch:** `develop`

**Descrição:**
- **Critério de Prevalência Temporal e Resolução de Conflitos:**
  - Conflitos de merge entre `ft_review` e `develop` resolvidos garantindo a prevalência das alterações mais recentes:
    - `serve.py`: Mantido `host='127.0.0.1'` atualizado em 04/10/2026.
    - `core/settings.py`: Integradas configurações de produção mais recentes (28/09/2026) com suporte a `CSRF_TRUSTED_ORIGINS` na porta `9443`, `SECURE_PROXY_SSL_HEADER`, `EnvReloadMiddleware`, `RealIPMiddleware`, e preservação da arquitetura multi-database (`desenvolvimento`, `producao`) e cache RBAC.
    - `requirements.txt` e `uv.lock`: Mantida versão limpa com `tzdata 2026.4` gerada mais recentemente via `uv export --no-hashes` (28/09/2026).
    - `usuarios/urls.py` e `usuarios/views.py`: Preservadas as rotas e views de gerenciamento de perfis RBAC (`perfis_gerenciar`), edição de perfil próprio (`meu_perfil`) e reset de senha seguro via POST com CSRF e auditoria completa.
- **Padrão Obrigatório de Botões de Ação em Tabelas (`padrao-tabelas-acoes.md`):**
  - Unificação em todas as tabelas do sistema (`templates/dashboard/index.html`, `templates/fichas/lista.html`, `templates/usuarios/lista.html`, `templates/veiculos/lista.html`):
    - Uso exclusivo de ícones sem texto na coluna de ações através de `.pf-action-btn` dentro do container oficial `.pf-table-actions`.
    - Garantia de acessibilidade por meio de atributos `title` e `aria-label` contextuais.
    - Preservação de todas as restrições granulares de acesso RBAC (`tem_perm`).
- **Testes Automatizados:**
  - Atualizado `veiculos/tests.py` para compatibilidade com o padrão de acessibilidade dos botões de ação.
  - Execução e aprovação de 100% da suíte de testes do Django (62/62 testes OK).

---

### Identificação Institucional da SR/PF/AC no Cabeçalho dos Relatórios · 27/09/2026

**Tipo:** `style` / `feat` — Adição da Superintendência Regional da Polícia Federal no Acre nos Cabeçalhos Oficiais  
**Branch:** `develop`

**Descrição:**
- **Identidade Institucional nos Relatórios Oficiais (`services/relatorios_pdf.py`):**
  - Adicionado o texto `SUPERINTENDÊNCIA REGIONAL DA POLÍCIA FEDERAL NO ACRE` no bloco de cabeçalho unificado dos relatórios PDF (`cabecalho_institucional`), posicionado imediatamente abaixo de `DEPARTAMENTO DE POLÍCIA FEDERAL`.
  - Criado o estilo tipográfico `HeaderRegional` (Helvetica-Bold, 10pt, entrelinha de 12pt, cor preta institucional PF) em conformidade com o Frontline PF Design System, assegurando hierarquia visual harmônica entre o órgão central, a superintendência regional e o título do documento.
  - A alteração reflete automaticamente em todos os relatórios oficiais do sistema:
    - Ficha Diária de Controle de Viaturas (`gerar_pdf_ficha`);
    - Relatório Geral da Frota de Viaturas (`gerar_pdf_viaturas`);
    - Histórico Individual de Manutenções da Viatura (`gerar_pdf_manutencoes_viatura`).
- **Testes Automatizados (`veiculos/tests.py`):**
  - Implementado teste unitário `test_cabecalho_institucional_superintendencia` na classe `RelatoriosVeiculosTestCase`, validando a presença e a correta ordem de precedência da Superintendência Regional em relação ao Departamento de Polícia Federal.

---

### Sincronização de Bases de Dados (db_dev e db_prod) e Atualização de Ambientes · 27/09/2026

**Tipo:** `chore` / `infra` — Sincronização Estrutural e de Permissões entre Bases de Desenvolvimento e Produção  
**Branch:** `develop`

**Descrição:**
- **Ajuste no Roteador de Banco de Dados (`core/db_router.py`):**
  - Atualizado o método `allow_migrate` do `DynamicDatabaseRouter` para permitir a execução explícita de migrações direcionadas tanto para `desenvolvimento` quanto para `producao` (`return db in ("default", "desenvolvimento", "producao")`).
- **Migrações Sincronizadas (`database/db_dev.sqlite3`, `database/db_prod.sqlite3`):**
  - Aplicada a migração `fichas.0007_fichacontrole_assinatura_vigilante_and_more` no banco de dados de produção (`db_prod.sqlite3`), alinhando o esquema com o banco de desenvolvimento (`db_dev.sqlite3`).
- **Suporte Multi-Database no Comando de Permissões (`accesscontrol/management/commands/setup_permissoes.py`):**
  - Implementado o argumento `--database` no comando de gestão `setup_permissoes`, com suporte especial à opção `all`.
  - Executada a sincronização completa de módulos, ações, widgets e perfis (`vigilante`, `nutran`, `inteligencia`, `chefia`, `administrador`) em ambas as bases de dados simultaneamente (`--reset --database all`).

---

### Texto Branco em Cabeçalhos de Tabelas PDF e Permissões de Relatórios para NUTRAN · 27/09/2026

**Tipo:** `fix` — Correção de Cor de Cabeçalho em Relatórios PDF e Habilitação de Relatórios para o Perfil NUTRAN  
**Branch:** `develop`

**Descrição:**
- **Estilização de Cabeçalhos em Relatórios PDF (`services/relatorios_pdf.py`):**
  - Identificado que o ReportLab não herda a cor do estilo de tabela (`TableStyle`) para os elementos filhos do tipo `Paragraph`.
  - Criados estilos dedicados com `textColor=colors.white` e `fontName="Helvetica-Bold"` aplicados diretamente aos `Paragraph` de cabeçalho das tabelas em:
    - `gerar_pdf_ficha`: tabela de movimentações de viaturas;
    - `gerar_pdf_viaturas`: tabela do relatório geral da frota;
    - `gerar_pdf_manutencoes_viatura`: tabela do histórico individual de manutenções.
  - O texto dos cabeçalhos agora é renderizado com legibilidade e contraste perfeitos sobre o fundo escuro (`PF_BLACK`).
- **Permissões de Emissão de Relatórios para NUTRAN (`accesscontrol/seeders.py`):**
  - Adicionadas as ações `operacao_diaria.fichas.exportar_pdf` e `operacao_diaria.fichas.exportar_excel` ao perfil `nutran`.
  - O responsável pelas viaturas (NUTRAN) agora pode exportar os relatórios oficiais em PDF e planilhas Excel tanto na página de detalhes da ficha diária quanto nas visualizações da frota e manutenções.
- **Testes Automatizados (`fichas/tests.py`):**
  - Criada a classe `NutranRelatoriosTestCase` cobrindo a geração de relatórios PDF e planilhas Excel pelo perfil NUTRAN e a exibição dos respectivos botões na interface.
  - Suíte completa de testes executada (61 testes) e aprovada com 100% de sucesso.

---

### Assinatura Eletrônica do Vigilante e Lançamento Automático no Encerramento · 27/09/2026

**Tipo:** `feat` — Ação de Assinatura do Vigilante e Lançamento Automático ao Encerrar a Ficha  
**Branch:** `develop`

**Descrição:**
- **Modelo de Dados (`fichas/models.py`, Migration `0007`):**
  - Adicionados os campos `assinatura_vigilante` (BooleanField), `vigilante_assinatura_usuario` (ForeignKey para Usuario) e `data_assinatura_vigilante` (DateTimeField) ao modelo `FichaControle`.
  - Implementado o método `assinar_vigilante(usuario)` para aposição da assinatura eletrônica do vigilante.
  - Atualizado o método `encerrar_ficha(usuario)` para lançar automaticamente a assinatura eletrônica do vigilante (com identificação do usuário e data/hora atuais) caso a ficha ainda não tenha sido assinada manualmente.
- **Ação de Assinatura e Permissões (`fichas/views.py`, `fichas/urls.py`, `accesscontrol/seeders.py`):**
  - Criada a view `ficha_assinar_vigilante` vinculada à rota `/fichas/<pk>/assinar/vigilante/`, protegida pela permissão `operacao_diaria.fichas.assinar_vigilante`.
  - Adicionada a ação `assinar_vigilante` na estrutura do submódulo de fichas e atribuída ao perfil `vigilante` (e administradores).
- **Interface e Experiência Visual (`templates/fichas/detalhe.html`, `templates/fichas/lista.html`):**
  - **Detalhe da Ficha:** O card "1. Vigilante do Dia" agora apresenta status reativo. Se assinada, exibe o nome do operador, carimbo de data/hora da assinatura digital e badge verde `<i class="fas fa-check-circle"></i> Assinatura Lançada`. Se pendente e com a ficha aberta, exibe o botão interativo `[ <i class="fas fa-signature"></i> Assinar Ficha ]`.
  - **Listagem de Fichas:** Exibição do badge `Assinada` junto ao nome do vigilante para identificação imediata das fichas devidamente assinadas.
- **Relatórios Oficiais (`services/relatorios_pdf.py`, `services/relatorios_excel.py`):**
  - No PDF da ficha diária, o rodapé agora carimba: `Assinado digitalmente por <Nome>` e `Data: <Data/Hora>` no quadro do Vigilante do Dia.
  - Na planilha Excel, o campo do Vigilante passa a registrar o status `(ASSINADO)`.
- **Auditoria do Sistema (`accesscontrol/models.py`, `accesscontrol/signals_auditoria.py`):**
  - Criado o código de auditoria `FICH_ASSINATURA_VIGILANTE (4019)` para rastreabilidade de aposição da assinatura do vigilante.
- **Testes Automatizados (`fichas/tests.py`):**
  - Criada a classe `AssinaturaVigilanteTestCase` cobrindo 5 cenários: assinatura manual pelo vigilante, lançamento automático de assinatura eletrônica no encerramento da ficha, preservação de assinatura prévia se outro usuário encerrar, view de assinatura via HTTP POST e exibição dinâmica nos templates.

---

### Restrição do Perfil de Chefia para Consulta e Relatórios de Viaturas · 27/09/2026

**Tipo:** `fix` — Perfil de Chefia Estritamente Somente Leitura e Relatórios na Gestão de Frota  
**Branch:** `develop`

**Descrição:**
- **Remoção de Botões de Ação na Gestão de Frota (`templates/veiculos/lista.html`, `templates/veiculos/detalhe.html`):**
  - **Listagem de Viaturas:**
    - O botão `[ + Nova Viatura ]` no cabeçalho foi condicionado à permissão `frota.viaturas.criar`. Usuários do perfil Chefia não visualizam este botão.
    - O botão de edição `[ Editar Veículo ]` na tabela foi condicionado à permissão `frota.viaturas.editar`. O perfil Chefia mantém apenas a ação de consulta `[ Detalhes ]`.
    - Os botões de exportação `[ Relatório PDF ]` e `[ Planilha Excel ]` permanecem totalmente disponíveis para consulta da Chefia.
  - **Detalhes da Viatura:**
    - Botões de alteração `[ Registrar Manutenção ]` e `[ Editar Viatura ]` na barra de ações foram condicionados a `frota.manutencao.criar` e `frota.viaturas.editar`.
    - Botões `[ Agendar / Nova Manutenção ]` no card lateral de quilometragem e `[ Nova Manutenção ]` no cabeçalho do histórico de serviços foram devidamente ocultados para a Chefia.
    - Mantidos os botões de emissão de relatórios `[ PDF Manutenção ]` e `[ Excel Manutenção ]`.
- **Correção da Verificação de Vistos em Fichas Diárias (`templates/fichas/detalhe.html`):**
  - Substituída a verificação legada `user.is_chefia` e `user.is_responsavel_viaturas` por tags de permissão dinâmicas `{% tem_perm 'operacao_diaria.fichas.apor_visto_chefia' %}` e `{% tem_perm 'operacao_diaria.fichas.apor_visto_nutran' %}`.
- **Configuração do Perfil e Widgets (`accesscontrol/seeders.py`):**
  - Atualizada a especificação do perfil `chefia` assegurando permissões puras de consulta (`frota.viaturas.visualizar`, `frota.manutencao.visualizar`, `operacao_diaria.fichas.visualizar`, exportação PDF/Excel e `apor_visto_chefia`).
  - Habilitados widgets analíticos do dashboard (`viaturas_em_transito`, `metricas_frota`, `alertas_manutencao`, `grafico_km_7dias`, `total_saidas_mes`) permitindo ampla visão operacional à Chefia sem qualquer capacidade de escrita.
- **Testes Automatizados (`veiculos/tests.py`):**
  - Criado `PermissoesChefiaVeiculosTestCase` cobrindo 4 cenários:
    - Ocultação dos botões de criação e edição na listagem de viaturas;
    - Ocultação dos botões de manutenção e edição nos detalhes do veículo;
    - Retorno `403 Forbidden` ao tentar forçar requisições diretas em URLs de criação/edição;
    - Geração e download com sucesso de relatórios PDF e planilhas Excel de frota e manutenção.

---

### Ocultação de Botões e Colunas de Ação no Dashboard por Perfil de Acesso · 27/09/2026

**Tipo:** `fix` — Controle Granular de Permissões e Omissão de Ações no Dashboard Operacional  
**Branch:** `develop`

**Descrição:**
- **Omissão Condicional de Botões e Colunas de Ação (`templates/dashboard/index.html`):**
  - **Tabela de Viaturas em Trânsito:** Implementada checagem da permissão `operacao_diaria.fichas.registrar_chegada` (`{% tem_perm %}`). Caso o perfil logado (como o perfil *Inteligência*) não possua autorização para registrar a chegada de viaturas, tanto o botão quanto a coluna de cabeçalho `<th>Ação</th>` são omitidos da tabela, ajustando o `colspan` do estado vazio dinamicamente.
  - **Visualização de Detalhes da Viatura:** Adicionada verificação de `frota.viaturas.visualizar` no nome/placa da viatura em trânsito; usuários sem acesso ao módulo de frota visualizam o texto puro em vez de um link bloqueado.
  - **Card da Ficha do Dia:** Verificações de permissão aplicadas para "Acessar Ficha Diária" (`operacao_diaria.fichas.visualizar`), "Registrar Movimentação" (`operacao_diaria.fichas.registrar_saida`) e "Abrir Ficha de Hoje" (`operacao_diaria.fichas.criar`).
  - **Tabela de Alertas de Manutenção Preventiva:** Ocultação da coluna e botão de "Criar OS" se o usuário não tiver permissão `frota.manutencao.criar`.
- **Testes Automatizados:** Adicionado teste unitário `test_dashboard_perfil_inteligencia_oculta_botao_chegada` em [dashboard/tests.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/dashboard/tests.py) garantindo que usuários com perfil de Inteligência acessem a visualização de trânsito sem a exibição do botão e nem do cabeçalho da coluna de Ação.

---

### Exibição de Dados de Saída na Edição de Registros e Estilo Unificado de Saída · 27/09/2026

**Tipo:** `fix` — Carregamento de Dados de Saída na Edição de Chegadas Avulsas e Estilo Unificado de Data/Horário de Saída  
**Branch:** `develop`

**Descrição:**
- **Carregamento dos Dados de Saída na Edição (`fichas/forms.py`, `templates/fichas/registro_editar_form.html`, `fichas/views.py`):**
  - Corrigido o formulário `RegistroEdicaoForm` para identificar quando o registro editado é do tipo `CHEGADA` com vínculo a uma `registro_saida_origem` (como no caso da viatura `BRA9F88`).
  - Nesses casos, os dados de saída (`data_saida`, `horario_saida`, `odometro_saida`, `condutor` e `destino`) são herdados e exibidos diretamente nos campos correspondentes na tela para conferência, mantendo-os devidamente protegidos/bloqueados (`disabled=True`).
  - Adicionado banner informativo em azul (`.pf-alert`) informando a qual ficha/expediente a saída original pertence.
- **Estilo Unificado para Conjunto de Data e Horário de Saída (`templates/fichas/detalhe.html`):**
  - Na listagem de Registros de Uso da Ficha Diária, o estilo do badge indicador de saída em outro plantão foi unificado para abranger tanto a **Data** quanto o **Horário** de saída (`.pf-badge.pf-badge-info`), apresentando a informação como um conjunto completo e coeso.
- **Testes Automatizados:** Adicionado teste `test_registro_editar_chegada_avulsa_exibe_dados_saida_origem` em [fichas/tests.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/fichas/tests.py) para garantir que a tela de edição sempre carregue os dados de saída originários.

---

### Unificação dos Botões de Saída e Retorno em "Registrar Movimentação" · 27/09/2026

**Tipo:** `feat` — Fluxo Unificado e Inteligente de Movimentação de Viaturas (Saída e Retorno)  
**Branch:** `develop`

**Descrição:**
- **Botão Único "Registrar Movimentação" (`templates/fichas/detalhe.html`):**
  - Unificados os botões de "Registrar Saída de Viatura" e "Registrar Retorno de Viatura" em uma única ação principal: `[ 🚗 Registrar Movimentação ]` no padrão Frontline PF.
- **Formulário Dinâmico Reativo (`fichas/forms.py`, `templates/fichas/registro_movimentacao_form.html`):**
  - Implementado o `RegistroMovimentacaoForm` e template dedicado onde o operador simplesmente seleciona o veículo desejado.
  - **Detecção Automática de Estado:**
    - *Viatura no Pátio (Disponível)*: Alterna a tela para o fluxo de **Saída** (destacando KM atual sugerido, condutor, destino e horário).
    - *Viatura na Rua (Em Trânsito)*: Alterna a tela para o fluxo de **Retorno** (exibindo painel com a saída original, condutor anterior sugerido, odômetro mínimo e cálculo automático do KM percorrido).
- **Backend Inteligente e Compatibilidade (`fichas/views.py`, `fichas/urls.py`):**
  - Nova view `registro_movimentacao_criar` (`fichas:movimentacao_criar`) roteia e salva com precisão o registro de saída ou chegada (inclusive fechamento de ciclo da mesma ficha ou geração de retorno avulso para saídas de plantões anteriores).
  - Rotas legadas (`saida_criar` e `chegada_avulsa_criar`) mantidas intactas para garantia de retrocompatibilidade total.
- **Testes Automatizados:** Suíte de testes atualizada em [fichas/tests.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/fichas/tests.py) com novos testes para saída e retorno unificados.

---

### Seleção de Turno e Preenchimento Automático da Data na Abertura de Ficha · 27/09/2026

**Tipo:** `feat` — Seleção de Turno Diurno/Noturno via Select e Data Padrão na Abertura de Ficha Diária  
**Branch:** `develop`

**Descrição:**
- **Seleção de Turno em Substituição a Horário de Início e Fim (`fichas/forms.py`, `templates/fichas/form.html`):**
  - Substituídos os campos manuais de horário de início e término no formulário de abertura de ficha por um campo de seleção (`select`) padronizado com as opções:
    - `Diurno - 07:00 às 19:00` (`horario_inicio=07:00`, `horario_termino=19:00`)
    - `Noturno - 19:00 às 07:00` (`horario_inicio=19:00`, `horario_termino=07:00`)
  - A atribuição dos horários no modelo `FichaControle` ocorre de maneira transparente e segura no `clean()` e `save()` do formulário.
  - O sistema sugere inteligentemente o turno padrão inicial com base na hora local atual do plantonista.
- **Preenchimento Automático da Data do Expediente:**
  - O campo de data permanece totalmente editável, mas já vem preenchido por padrão com a data do dia corrente (`date.today()`).
- **Validação e Interface Visual Frontline PF (`templates/fichas/form.html`):**
  - Grid remodelado em duas colunas elegantes (Data do Expediente e Turno do Expediente).
  - Alerta de validação contextual (`.pf-alert.pf-alert-danger`) exibindo erros específicos de preenchimento ou colisão de fichas no mesmo turno.
- **Testes Automatizados:** Testes adicionados em [fichas/tests.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/fichas/tests.py) cobrindo abertura com turno diurno, turno noturno, data padrão e submissão via view.

---

### Padrão Visual de Perfis, Senha Padrão mudar@123, Botões de Ícones e Reset de Senha · 27/09/2026

**Tipo:** `feat` — Reformulação Visual de Perfis de Acesso, Senha Padrão de Cadastro, Ações por Ícones e Reset de Senha  
**Branch:** `develop`

**Descrição:**
- **Identidade Visual e Seleção de Perfis no Cadastro/Edição (`templates/usuarios/form.html`):**
  - Implementado grid moderno de cartões interativos (`.pf-perfil-card`) para "Selecione os Perfis de Acesso do Usuário", seguindo as diretrizes do Frontline PF.
  - Cada perfil agora conta com ícone temático, descrição funcional clara, badge de escopo e destaque visual com seleção reativa via JavaScript (`.is-selected`).
- **Senha Padrão `mudar@123` para Novos Usuários (`usuarios/forms.py`):**
  - Usuários recém-cadastrados são criados com a senha padrão `mudar@123` caso nenhuma outra senha seja especificada no formulário.
  - O campo de senha inicializa pré-preenchido com `mudar@123` e possui validação de comprimento mínimo de 6 caracteres.
- **Tabela de Usuários com Botões Exclusivos de Ícones (`templates/usuarios/lista.html`):**
  - Botões de ações da listagem de usuários redesenhados para exibição estrita de ícones representativos, sem texto, com acabamento compacto e tooltips de identificação.
  - Paleta com identidade visual individual para cada operação:
    - *Perfis*: Roxo (`#6B21A8` / `fa-user-shield`).
    - *Editar*: Azul PF (`#1D4ED8` / `fa-pen`).
    - *Resetar Senha*: Âmbar (`#B45309` / `fa-key`).
    - *Desativar*: Vermelho (`#DC2626` / `fa-user-slash`).
    - *Ativar*: Verde (`#059669` / `fa-user-check`).
- **Funcionalidade de Reset de Senha de Usuários (`usuarios/views.py`, `usuarios/urls.py`, `templates/usuarios/lista.html`):**
  - Criada view `usuario_resetar_senha` vinculada à rota `<int:pk>/resetar-senha/`.
  - Integração com modal nativo acessível (`<dialog>`) com confirmação explícita de que a senha será redefinida para `mudar@123`.
- **Testes Automatizados:** Testes atualizados em [usuarios/tests.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/usuarios/tests.py) cobrindo criação com senha padrão e o endpoint de reset de senha.

---

### Correção e Renderização dos Perfis de Acesso no Cadastro de Usuários · 27/09/2026

**Tipo:** `fix` — Renderização do Campo de Perfis, Validação de Senha Provisória e Exibição de Alertas no Formulário de Usuário  
**Branch:** `develop`

**Descrição:**
- **Renderização e Seleção de Perfis no Template:**
  - O template [templates/usuarios/form.html](file:///F:/_PROJETOS_PYHTON/app_viaturas/templates/usuarios/form.html) tentava renderizar o campo inexistente `{{ form.perfil }}`, enquanto no [usuarios/forms.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/usuarios/forms.py) o campo RBAC gerenciado pelo `accesscontrol` é `perfis` (`ModelMultipleChoiceField`).
  - Como o campo não aparecia na tela, a validação falhava silenciosamente por falta de seleção de perfil obrigatório, e os erros não eram exibidos.
  - Implementada seção dedicada com cartões e checkboxes estilizados no padrão Frontline PF para seleção dos perfis (`Administrador`, `Vigilante`, `NUTRAN`, `Chefia`, `Inteligência`).
- **Exibição de Mensagens de Erro e Alertas Visuais:**
  - Inserido bloco `{% if form.errors %}` no topo do template com componente `.pf-alert.pf-alert-danger` listando detalhadamente todas as pendências que impeçam a gravação do registro.
  - Adicionado feedback explícito com `messages.error` nas views `usuario_criar` e `usuario_editar` em [usuarios/views.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/usuarios/views.py).
- **Flexibilização de Senha Provisória Administrativa:**
  - No `clean_password()` de [usuarios/forms.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/usuarios/forms.py), ajustada a validação para permitir senhas provisórias atribuídas por administradores no momento do cadastro inicial (como `vigilante123`), ignorando restrições de semelhança nominal com o login para senhas provisórias que contenham 6 ou mais caracteres.
- **Testes Automatizados:** Suíte de 40 testes validada com 100% de sucesso.

---

### Ciclo Independente de Saídas e Chegadas entre Fichas Diárias · 27/09/2026

**Tipo:** `feat` — Movimentações Independentes e Desacopladas por Expediente/Ficha Diária  
**Branch:** `develop`

**Descrição:**
- **Desacoplamento de Ciclo entre Plantões:**
  - Uma ficha de expediente (`FichaControle`) agora pode ser encerrada formalmente mesmo com viaturas em trânsito (na rua). Nesse caso, a ficha de saída registra exclusivamente o evento de saída da viatura, sem exigir o retorno no mesmo expediente.
  - O retorno dessa viatura é lançado posteriormente na ficha correspondente ao expediente em que ela efetivamente retornar ao pátio, contendo exclusivamente o registro de entrada (sem saída lançada nesta segunda ficha).
  - Cada Ficha Diária de Controle registra apenas e tão-somente os lançamentos ocorridos dentro do seu próprio expediente, preservando a fidelidade histórica do documento físico/digital.
- **Evolução do Modelo de Dados (`fichas/models.py`):**
  - Campos `data_saida`, `horario_saida` e `odometro_saida` tornados anuláveis (`null=True, blank=True`).
  - Adição do campo `tipo_movimentacao` com escolhas `COMPLETO`, `SAIDA` e `CHEGADA`.
  - Adição da chave estrangeira reflexiva `registro_saida_origem = ForeignKey('self', null=True, blank=True, related_name='registros_retorno')` para associar o registro de chegada ao registro de saída originário.
  - Criação de properties `@property` inteligentes: `odometro_saida_efetivo`, `data_saida_efetiva`, `horario_saida_efetivo` e `km_percorrido` (que calcula a distância percorrida subtraindo o odômetro de chegada do odômetro de saída original, mesmo que originado em outra ficha).
  - No `save()`, caso o registro seja do tipo `CHEGADA` avulsa, o registro de saída de origem tem seu status automaticamente concluído (`STATUS_CONCLUIDO`), e a viatura tem seu status retornado para `DISPONIVEL` com o `km_atual` atualizado.
  - Migração `0006_alter_registrouso_options_and_more.py` gerada e aplicada nos bancos `database/db_dev.sqlite3` e `database/db_prod.sqlite3`.
- **Formulário de Chegada Avulsa (`fichas/forms.py`):**
  - Implementação de `RegistroChegadaAvulsaForm` com validações contra o odômetro de saída e data de saída de origem, listagem de veículos com status `EM_USO`, e herança automática de condutor e destino caso omitidos.
- **Views e Rotas (`fichas/views.py` e `fichas/urls.py`):**
  - Nova rota `<int:ficha_pk>/chegada-avulsa/` e view `registro_chegada_avulsa_criar`: permite registrar retorno de viatura que saiu em expediente anterior, com auto-associação e cálculo dinâmico de quilometragem.
  - Atualização de `ficha_detalhe` com contadores segregados: `total_saidas`, `total_chegadas`, `em_transito` e detecção de viaturas na rua para exibição do botão de retorno.
- **Interfaces e Templates Frontline PF (`templates/fichas/`):**
  - Criação de [registro_chegada_avulsa_form.html](file:///F:/_PROJETOS_PYHTON/app_viaturas/templates/fichas/registro_chegada_avulsa_form.html): formulário responsivo com painel dinâmico em tempo real exibindo a ficha de origem, data/hora da saída, KM inicial e cálculo em tempo real do percurso percorrido conforme digitação do odômetro.
  - Atualização de [detalhe.html](file:///F:/_PROJETOS_PYHTON/app_viaturas/templates/fichas/detalhe.html): botão de ação `[Registrar Retorno de Viatura]`, badges discriminando total de saídas e chegadas, e exibição clara na tabela informando se a saída pertenceu a plantão anterior ou se a viatura permaneceu em trânsito com retorno em outro plantão.
- **Relatórios Oficiais em PDF e Excel (`services/relatorios_pdf.py` e `services/relatorios_excel.py`):**
  - Tratamento defensivo de registros com saída ou chegada nula.
  - Geração precisa dos textos indicando `"Saída em ficha ant. (Ficha #X)"` e `"SEM RETORNO NESTE PLANTÃO"` / `"EM TRÂNSITO"`.
- **Auditoria e Signals (`accesscontrol/signals_auditoria.py`):**
  - Suporte ao registro de auditoria `CodigoAcao.FICH_RETORNO_REGISTRADO` em chegadas avulsas criadas diretamente.
- **Testes Automatizados:** Suíte de 40 testes executada com 100% de aprovação em todos os apps (`fichas`, `accesscontrol`, `dashboard`, `usuarios`, `veiculos`, `core`).

---

### Correção de Alinhamento e Fechamento de Tags na Navbar Corporativa · 27/09/2026

**Tipo:** `fix` — Correção Estrutural de HTML e Centralização do Banner na Navbar  
**Branch:** `develop`

**Descrição:**
- **Restauração do Fechamento de Tag:** Corrigida a ausência da tag de fechamento `</div>` em `.pf-header-titles` no [templates/base.html](file:///F:/_PROJETOS_PYHTON/app_viaturas/templates/base.html), que provocava a quebra da árvore DOM e o deslocamento indevido do título e subtítulo para a direita.
- **Posicionamento e Centralização Perfeita:** Aplicado posicionamento absoluto (`position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);`) no banner `<span><h1>BANCO DE DESENVOLVIMENTO</h1></span>`. Com isso, a identidade e títulos mantêm-se estritamente à esquerda, o perfil do usuário e logout à direita, e o aviso em vermelho perfeitamente centralizado na barra corporativa.

---

### Correção de Base de Dados de Desenvolvimento e Limpeza de Variáveis no .env · 27/09/2026

**Tipo:** `fix` — Restauração da Base `db_dev.sqlite3` e Limpeza do `.env`  
**Branch:** `develop`

**Descrição:**
- **Restauração de `database/db_dev.sqlite3`:** Corrigido o arquivo da base de desenvolvimento que havia sido inicializado vazio (0 bytes), sincronizando-o com a estrutura completa e migrada de `database/db_prod.sqlite3` (405 KB), eliminando o erro `OperationalError: no such table: django_session`.
- **Limpeza do `.env`:** Removidas as variáveis legadas e não utilizadas `DEBUG` e `ALLOWED_HOSTS`, cujo controle é agora exclusivamente centralizado pela variável `APP_ENV` (`local` ou `operacao`).

---

### Segregação de Bancos (DB_ENV), Ambientes (APP_ENV), Navbar +40% e Modo Manutenção (APP_MNT) · 27/09/2026

**Tipo:** `feat` — Gestão Dinâmica de Ambientes, Bancos Isolados, Navbar Ampliada e Modo de Manutenção  
**Branch:** `develop`

**Descrição:**
- **Segregação de Bancos e Chaveamento Dinâmico (`DB_ENV`):**
  - Criação da pasta `database/`, movimentação de `db.sqlite3` para `database/db_dev.sqlite3` e criação do banco de produção `database/db_prod.sqlite3`.
  - Implementação de [core/env_utils.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/core/env_utils.py) para leitura em tempo real do `.env` e de [core/middleware.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/core/middleware.py) (`DynamicDatabaseMiddleware`) sincronizando a conexão e roteando para `db_dev.sqlite3` (se `DB_ENV="desenvolvimento"`) ou `db_prod.sqlite3` (se `DB_ENV="producao"`) a cada requisição.
  - Implementação de [core/db_router.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/core/db_router.py) (`DynamicDatabaseRouter`) e [core/context_processors.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/core/context_processors.py) (`ambiente_context`).
- **Indicador Visual de Banco de Desenvolvimento:**
  - Inserção de `<span><h1 style="color: #FF2E2E; font-weight: 900; text-transform: uppercase;">BANCO DE DESENVOLVIMENTO</h1></span>` centralizado na tela de login ([login.html](file:///F:/_PROJETOS_PYHTON/app_viaturas/templates/usuarios/login.html)) e na navbar corporativa ([base.html](file:///F:/_PROJETOS_PYHTON/app_viaturas/templates/base.html)), condicionado a `DB_ENV="desenvolvimento"`.
- **Aumento de 40% na Altura da Navbar Corporativa:**
  - Atualização da variável `--header-height` no [static/css/frontline.css](file:///F:/_PROJETOS_PYHTON/app_viaturas/static/css/frontline.css) de `64px` para `90px` (+40.6%), redimensionando proporcionalmente a logo institucional para 56px e ajustando harmonicamente o subheader, sidebar e área principal sem quebras de layout.
- **Parametrização de Ambiente (`APP_ENV`):**
  - Configuração no [core/settings.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/core/settings.py):
    - `APP_ENV="local"`: `DEBUG = True` e `ALLOWED_HOSTS = ["127.0.0.1", "localhost"]`.
    - `APP_ENV="operacao"`: `DEBUG = False` e `ALLOWED_HOSTS = ["10.68.6.121"]`.
- **Modo de Manutenção (`APP_MNT`) e Encerramento de Sessões:**
  - Criação da página [templates/manutencao.html](file:///F:/_PROJETOS_PYHTON/app_viaturas/templates/manutencao.html) com design Frontline PF, brasão oficial, ícone temático, avisos institucionais e HTTP 503.
  - Criação do `ManutencaoMiddleware` no [core/middleware.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/core/middleware.py) que, ao detectar `APP_MNT=True`, encerra a sessão ativa do usuário (`logout`, `session.flush()`, purga da tabela `django_session`) e redireciona qualquer requisição para `/manutencao/` (exceto arquivos estáticos). Quando `APP_MNT=False`, o sistema opera normalmente.
- **Testes Automatizados:** Criação de suíte de testes em [core/tests.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/core/tests.py) cobrindo todos os fluxos com 100% de sucesso.

---

### Correção de AttributeError no Registro de Retorno de Viatura · 27/09/2026

**Tipo:** `fix` — Correção no Signal de Auditoria de Retorno de Viaturas (`RegistroUso`)  
**Branch:** `develop`

**Descrição:**
- **Correção de Atributos no Signal de Auditoria:** Corrigida a referência ao atributo `horario_retorno` (inexistente no modelo `RegistroUso`, cujo nome correto é `horario_chegada`) e aos campos `km_saida` e `km_retorno` (cujos campos reais no modelo são `odometro_saida` e `odometro_chegada`) em [signals_auditoria.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/accesscontrol/signals_auditoria.py).
- **Compatibilidade Defensiva no Modelo:** Adição de properties `@property` `km_saida`, `km_retorno` e `horario_retorno` no modelo [RegistroUso](file:///F:/_PROJETOS_PYHTON/app_viaturas/fichas/models.py) para retrocompatibilidade e prevenção de exceções similares.
- **Diferenciação Robusta de Rotas de Chegada e Edição:** Ajustada a verificação no signal de auditoria para capturar com precisão a rota de chegada (`FICH_RETORNO_REGISTRADO`) e rotas de edição (`FICH_MOVIMENTACAO_EDITADA`).
- **Testes Automatizados:** Criação de suíte de testes em [accesscontrol/tests.py](file:///F:/_PROJETOS_PYHTON/app_viaturas/accesscontrol/tests.py) cobrindo os signals de auditoria de saída, retorno e o fluxo POST de conclusão de chegada (`registro_chegada_concluir`).

---

### Sistema de Auditoria, Telas de Erro e Códigos Numéricos de Log · 13/09/2026

**Tipo:** `feat` — Sistema de Auditoria, Telas de Erro e Módulo Lateral de Logs  
**Branch:** `develop`

**Descrição:**
- **Catálogo de Códigos Numéricos de Ação:** Padronização estruturada por faixas semânticas (1001 Login, 1002 Logout, 1003 Falha de login, 2001 Acesso bloqueado 403, 3001 Cadastro de viatura, 3002 Edição de viatura, 4001 Abertura de ficha, 4010 Saída de viatura, 4011 Retorno de viatura, 5001 Cadastro de usuário, 9001 Erro 500 no servidor).
- **Modelo de Auditoria Imutável (`LogAuditoria`):** Registro detalhado com código numérico indexado, categoria, usuário, URL acessada, método HTTP, endereço IP, status code, objeto afetado e payload JSON com diff da alteração.
- **Captura Transparente via Contexto e Signals:** Criação do `AuditoriaContextMiddleware` gerenciando requisições com `contextvars` thread-safe, combinado com receivers de signals de autenticação (`user_logged_in`, `user_logged_out`, `user_login_failed`) e modelos de dados (`Viatura`, `Manutencao`, `FichaControle`, `RegistroUso`, `Usuario`, `UsuarioPerfil`).
- **Módulo na Barra Lateral e Controle Estrito de ACL:** Seção **AUDITORIA** na barra lateral corporativa com o item **Logs de Auditoria** (ícone `fas fa-shield-alt`), restrito estritamente a administradores via permissão `auditoria.logs.visualizar`. Usuários de outros perfis (Vigilante, NUTRAN, Inteligência, Chefia) têm o menu oculto e qualquer tentativa de acesso direto é bloqueada com HTTP 403 e registrada com o código `2001`.
- **Telas de Erro Institucionais Frontline PF:** Implementação e padronização das telas 400 (Requisição Inválida), 403 (Acesso Não Autorizado), 404 (Página Não Encontrada) e 500 (Erro Interno do Servidor) com Brasão Oficial da PF, tipografia Roboto e botões de contingência.
- **Painel Analítico de Logs com Filtros Avançados:** Interface em tabela Frontline PF com badges categorizados, paginação limpa, modal com inspeção de detalhes JSON e filtros por intervalo de data, intervalo de horário (início/fim para plantões), código numérico da ação e busca por usuário.

---

### Controle de Acesso e Ordenação (Lista de Fichas) · 12/09/2026


**Tipo:** `feat` — Melhorias de UI e ACL  
**Branch:** `develop`

**Descrição:**
- Ocultação dos botões de exportação (PDF e Excel) na tela de listagem de Fichas para perfis sem permissão (ex: Vigilante).
- Adição de ordenação cronológica decrescente (mais recentes primeiro) na listagem das Fichas Diárias.

---


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
