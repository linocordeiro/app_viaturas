# Plano de Implementação — APP_VIATURAS (Polícia Federal)

O **APP_VIATURAS** é um sistema web corporativo para controle de entrada, saída, histórico de utilização e manutenção da frota de veículos da Polícia Federal, substituindo o preenchimento manual em fichas de papel por um fluxo digital seguro, auditável e alinhado ao Design System oficial **Frontline da PF**.

---

## 1. Visão Geral da Arquitetura

O sistema será construído utilizando **Python 3.11** e **Django 5.2**, banco de dados **SQLite**, geração de relatórios com **ReportLab** (PDF) e **OpenPyXL** (Excel), e interface 100% desenhada conforme os tokens e componentes da skill `frontlinePF`:
- **Paleta de Cores Oficial**: PF-Black (`#111213`), PF-Gold500 (`#E1AD62`), PF-Blue500 (`#3363CC`), PF-Grey700 (`#41434E`), PF-Green500 (`#33A841`), PF-Red500 (`#BF0C1D`).
- **Tipografia**: Família **Roboto** (Headings `h1` a `h6`, corpos 14px e 12px, sem `text-uppercase` em cabeçalhos/botões).
- **Grid Espacial**: Baseado no **8px Grid System** da Polícia Federal e **PrimeFlex** responsivo.
- **Layout**: Estrutura Frontline corporativa com Header, SubHeader com perfil/módulo, Sidebar retrátil (até 338px) e Footer fixo institucional.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Header Frontline PF (Brasão Oficial + "APP_VIATURAS" + Perfil + Sair)  │
├────────────────────────────────────────────────────────────────────────┤
│ SubHeader (Setor Operacional + Perfil de Acesso: Vigilante/Chefia)     │
├───────────────┬────────────────────────────────────────────────────────┤
│ Sidebar Menu  │ Área Principal de Conteúdo                             │
│ • Dashboard   │ • Cards de Métricas (Em trânsito, Disponíveis)         │
│ • Fichas      │ • Ficha de Controle Diário Aberta                      │
│ • Viaturas    │ • Gráficos de KM Rodados (Chart.js / Frontline Dark)  │
│ • Manutenção  │ • Tabela de Movimentações (TableCustom Frontline)      │
│ • Usuários    │ • Alertas de Revisão Preventiva por KM / Data          │
│ • Relatórios  │                                                        │
├───────────────┴────────────────────────────────────────────────────────┤
│ Footer Frontline PF (Versão v1.0.0 + Suporte TI + Copyright DPF)       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Regras de Negócio Implementadas

### 2.1. Módulo Usuários e Perfis
- **Perfis Operacionais**:
  - `Vigilante / Portaria`: Preenche as fichas diárias, lança saídas e chegadas de viaturas com odômetro e avarias.
  - `Responsável pelas Viaturas`: Cadastra veículos, agenda e atesta manutenções, assina o visto de viaturas na ficha diária.
  - `Chefia`: Assina o visto da chefia nas fichas diárias, acessa relatórios executivos e gerenciais.
  - `Administrador`: Gestão completa de usuários, setores e parâmetros.
- **CRUD completo** de usuários com controle de permissões e auditoria de ações.

### 2.2. Módulo Veículos (Viaturas)
- **Atributos**: Marca, Modelo, Placa (validação Mercosul/Antiga), Chassi, Ano/Modelo, Cor, Categoria (Ostensiva / Descaracterizada / Administrativa), Setor ao qual pertence (DREX, DELEPAT, GISE, GPI, NUTRAN, etc.), Responsável pela Viatura (Pessoa ou Setor), KM atual.
- **Estados da Viatura**:
  - `Disponível`: Apta para nova saída.
  - `Em Uso / Em Trânsito`: Com registro de saída aberto no dia.
  - `Em Manutenção`: Na oficina/revisão (bloqueada para saídas).
  - `Indisponível`: Com avaria impeditiva ou baixa.
- **Controle de Manutenções**:
  - Histórico cronológico: tipo (Preventiva, Corretiva, Revisão Periódica, Sinistro), data, KM da manutenção, oficina/fornecedor, número da OS, descrição, peças substituídas e valor total.
  - **Alerta de Manutenção**: Notificação visual na interface quando o veículo atingir o limite de KM configurado (ex: a cada 10.000 km) ou quando a data da próxima revisão estiver próxima (< 15 dias) ou vencida.
- **Relatórios**:
  - Relatório geral de viaturas (PDF e Excel).
  - Relatório individual de uma viatura com ficha técnica e histórico completo de manutenções (PDF e Excel).

### 2.3. Módulo Fichas de Controle Diário
- **Ficha Diária (`FichaControle`)**:
  - Data do expediente (restrição: **apenas 1 ficha por dia** no sistema).
  - Horário de início e horário de término do expediente.
  - Vigilante do dia responsável pelo preenchimento.
  - Visto do responsável pelas viaturas (com data e carimbo digital do usuário).
  - Visto da chefia (com data e carimbo digital do usuário).
  - Status: `Aberta` ou `Encerrada`.
  - **Regra de Bloqueio**: A ficha do dia anterior pode ser encerrada manualmente ou é sugerida para encerramento na virada do dia. **Uma vez encerrada, a ficha não pode mais sofrer alterações nem inclusão de novos registros**, preservando a integridade legal da fiscalização.
- **Registros de Uso (`RegistroUso`)**:
  - Viatura selecionada (apenas viaturas disponíveis).
  - Condutor (nome, matrícula e setor).
  - Destino / Missão / Operação.
  - Horário e Odômetro de Saída.
  - Horário e Odômetro de Chegada (preenchido no retorno).
  - Indicação de avarias (Sim/Não) e campo descritivo de danos/ocorrências.
  - Validações: `odometro_chegada >= odometro_saida`; atualização automática do `km_atual` da viatura no retorno.
- **Relatórios**:
  - Emissão da Ficha de Controle Diário em formato idêntico ao modelo impresso oficial da PF em PDF (com campos de assinatura para Vigilante, Responsável e Chefia) e planilha Excel.

### 2.4. Dashboard Frontline
- Indicadores em tempo real:
  - Viaturas em trânsito (com botão de ação rápida "Registrar Chegada").
  - Gráfico de disponibilidade (Disponíveis vs Indisponíveis vs Manutenção) nas cores oficiais Frontline.
  - Gráfico histórico de KM rodados por dia/semana (Chart.js tematizado Frontline Dark).
  - Lista de alertas de manutenção preventiva urgente.
  - Card da Ficha de Controle do dia atual (status e atalho para novo registro).

---

## 3. Mudanças Propostas no Projeto

### Estrutura de Diretórios e Arquivos

```
app_viaturas/
├── core/                           # Projeto Django Principal
│   ├── __init__.py
│   ├── settings.py                # Configurações Django, SQLite, Static, Idioma pt-br
│   ├── urls.py                    # Roteamento global
│   ├── wsgi.py
│   └── asgi.py
├── usuarios/                       # App de Usuários e Permissões
│   ├── models.py                  # Custom User com matrícula, setor e perfil
│   ├── views.py                   # Login, Logout, CRUD de usuários
│   ├── forms.py
│   └── urls.py
├── veiculos/                       # App de Viaturas e Manutenção
│   ├── models.py                  # Viatura, Setor, Manutencao, Alertas
│   ├── views.py                   # CRUD Viaturas, Histórico, Alertas, Relatórios
│   ├── forms.py
│   └── urls.py
├── fichas/                         # App de Fichas de Controle e Movimentação
│   ├── models.py                  # FichaControle, RegistroUso
│   ├── views.py                   # Abertura de ficha, Saídas/Chegadas, Vistos, Encerramento
│   ├── forms.py
│   └── urls.py
├── dashboard/                      # App da Home e Dashboard
│   ├── views.py                   # Métricas, KPIs, dados para gráficos
│   └── urls.py
├── services/                       # Serviços de Exportação e Relatórios
│   ├── __init__.py
│   ├── relatorios_pdf.py          # Gerador ReportLab (Ficha Oficial, Viaturas, Manutenção)
│   └── relatorios_excel.py        # Gerador OpenPyXL com formatação corporativa Frontline
├── static/
│   ├── css/
│   │   └── frontline.css          # Design System Frontline PF completo (Cores, 8px grid, botões)
│   ├── js/
│   │   └── frontline.js           # Interações da sidebar, modais e gráficos Chart.js
│   └── img/
│       └── brasao_pf.png          # Brasão oficial da Polícia Federal (em vetor/imagem)
├── templates/
│   ├── base.html                  # Layout mestre Frontline PF (Header, SubHeader, Sidebar, Footer)
│   ├── dashboard/
│   │   └── index.html             # Dashboard gerencial e operacional
│   ├── fichas/
│   │   ├── lista.html             # Listagem de fichas diárias
│   │   ├── detalhe.html           # Visualização e digitação da ficha (estilo ficha em papel)
│   │   └── registrar_uso.html     # Modal/Formulário de saída e chegada
│   ├── veiculos/
│   │   ├── lista.html             # Frota de viaturas com status e badges
│   │   ├── form.html              # Cadastro/Edição de viatura
│   │   ├── detalhe.html           # Detalhe da viatura com histórico de manutenção
│   │   └── form_manutencao.html   # Registro de nova manutenção
│   └── usuarios/
│       ├── login.html             # Tela de login estilizada Frontline PF
│       ├── lista.html             # Gerenciamento de usuários
│       └── form.html              # Cadastro/Edição de usuário
├── manage.py
└── pyproject.toml
```

---

## 4. Plano de Verificação

### 4.1. Testes Automatizados
- Criação de suíte de testes em `veiculos/tests.py` e `fichas/tests.py`:
  - Teste de unicidade da Ficha Diária (não permitir mais de 1 ficha na mesma data).
  - Teste de bloqueio de edição após encerramento da ficha.
  - Teste de transição de status da viatura (`Disponível` -> `Em Uso` ao sair -> `Disponível` ao retornar).
  - Teste de validação de odômetro (`odometro_chegada >= odometro_saida`).
  - Teste de disparo de alertas de manutenção por KM e data.
  - Teste de exportação dos relatórios PDF e Excel sem erros.
- Execução dos testes via terminal:
  ```powershell
  .\.venv\Scripts\python.exe manage.py test
  ```

### 4.2. Verificação Manual e Demonstração
- Popular o banco de dados com um comando de carga inicial (`seed_data`):
  - Viaturas caracterizadas e descaracterizadas da PF.
  - Usuários de teste (vigilante, responsável pelas viaturas, chefe de delegacia, administrador).
  - Ficha aberta do dia com saídas em andamento e saídas concluídas.
  - Registros de manutenção com alertas ativos.
- Iniciar o servidor de desenvolvimento Django (`python manage.py runserver`).
- Testar os fluxos completos:
  1. Acessar o Dashboard e conferir indicadores, gráficos de KM e cards de viaturas em trânsito.
  2. Criar uma nova saída de viatura e registrar o retorno com odômetro e avarias.
  3. Aplicar visto do responsável pelas viaturas e visto da chefia.
  4. Encerrar a ficha e validar que as edições ficam bloqueadas.
  5. Emitir e baixar o PDF oficial da Ficha de Controle e a planilha Excel.
  6. Emitir o relatório individual de viatura com histórico de manutenções em PDF e Excel.
