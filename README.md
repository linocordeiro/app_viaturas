# APP_VIATURAS — Sistema de Controle de Frota e Expediente

<p align="center">
  <strong>Polícia Federal • Diretoria de Tecnologia da Informação e Inovação (DTI)</strong><br>
  <em>Sistema corporativo para controle de entrada, saída, utilização diária e manutenção da frota oficial de viaturas</em>
</p>

<p align="center">
  <img src="static/img/brasao_pf.png" alt="Brasão da Polícia Federal" width="120">
</p>

---

## 📌 Visão Geral

O **APP_VIATURAS** digitaliza o processo de fiscalização e registro diário do uso da frota de veículos oficiais da Polícia Federal. Ele substitui os livros de registro e fichas físicas em papel por um fluxo digital auditável, seguro e em conformidade estrita com o Design System corporativo **Frontline PF**.

O sistema garante rastreabilidade total de condutores, destinos, odômetros de partida e retorno, controle de avarias, histórico e alertas de manutenções preventivas, além do ciclo formal de vistos e encerramento do expediente pelo vigilante/plantonista, responsável setorial e chefia.

---

## 🚀 Principais Funcionalidades

### 1. Fichas de Controle Diário de Expediente (`fichas`)
- **Unicidade de Expediente**: Regra mandatória de uma única ficha de controle por dia calendário.
- **Lançamento de Saídas e Chegadas**: Registro em tempo real de viatura, condutor, setor, destino/missão, horários e odômetros.
- **Validação de Odômetro e Quilometragem**: Validação automática `odometro_chegada >= odometro_saida` e atualização do odômetro do veículo no retorno.
- **Registro de Avarias e Ocorrências**: Apontamento detalhado de avarias para fins de fiscalização e auditoria interna.
- **Ciclo de Assinaturas e Vistos Digitais**: Visto do Vigilante, Visto do Responsável pelas Viaturas e Visto da Chefia com carimbo de data/hora e usuário autenticado.
- **Encerramento de Expediente**: Bloqueio definitivo de edição após o encerramento formal para garantia da fé pública dos registros.

### 2. Gestão da Frota de Viaturas (`veiculos`)
- Cadastro completo de viaturas (Marca, Modelo, Placa Mercosul/Antiga, Chassi, Ano, Cor, Setor de Lotação, Responsável e Categoria Ostensiva/Descaracterizada/Administrativa).
- Controle de status operacional em tempo real: `Disponível`, `Em Trânsito`, `Em Manutenção` ou `Indisponível`.
- Histórico cronológico e financeiro de manutenções e revisões (Preventiva, Corretiva, Periódica ou Sinistro).
- **Alertas Automatizados de Manutenção**: Disparo de avisos visuais por quilometragem excedente ou proximidade da data limite de revisão.

### 3. Dashboard Gerencial e Operacional (`dashboard`)
- Indicadores em tempo real (KPIs) de viaturas na rua, veículos disponíveis no pátio e viaturas retidas em oficina.
- Acesso rápido à ficha do expediente do dia.
- Painel de viaturas em trânsito com atalho imediato para registrar retorno.
- Gráficos analíticos de utilização e histórico de quilometragem percorrida.

### 4. Emissão de Relatórios Oficiais (`services`)
- **PDF Oficial da Ficha Diária**: Modelo impresso idêntico ao padrão oficial da Polícia Federal (com espaços para rubrica/assinatura física e digital).
- **Planilhas em Excel (XLSX)**: Exportação formatada com a identidade visual Frontline para auditoria e prestação de contas.
- **Relatórios Individuais de Viatura**: Ficha técnica e histórico integral de manutenções e custos em PDF e Excel.

---

## 🎨 Identidade Visual — Frontline PF

A interface do sistema adota integralmente as normas do **Frontline — Design System da Polícia Federal**:

| Elemento | Padrão Frontline Adotado |
|:---|:---|
| **Cores Primárias** | **PF-Black** (`#111213`), **PF-Gold500** (`#E1AD62`), **PF-Blue500** (`#3363CC`) |
| **Cores de Apoio** | **PF-Green500** (`#33A841`) para status regular; **PF-Red500** (`#BF0C1D`) para erros e alertas críticos |
| **Tipografia** | Família **Roboto** (Google Fonts), hierarquia de `h1` (36px) a `h6` (12px) |
| **Regra de Tipografia** | Textos em Title Case e Sentence Case (sem utilização de `text-uppercase` contínuo) |
| **Espaçamento** | **Grid de 8px** (múltiplos obrigatórios de 8px em paddings, margens e gaps) |
| **Casca Intranet** | Estrutura corporativa com Header escuro, SubHeader funcional, Sidebar colapsável e Footer fixo |
| **Páginas de Erro** | Templates oficiais institucionais para códigos HTTP 403, 404 e 500 |

---

## 👥 Perfis de Acesso e Permissões

1. **Vigilante / Portaria**: Abre a ficha diária, cadastra saídas e retornos de viaturas, registra odômetros e avarias.
2. **Responsável pelas Viaturas**: Gerencia cadastros de viaturas, lança e atesta manutenções, assina o visto das viaturas na ficha de controle.
3. **Chefia**: Consulta relatórios gerenciais, dashboards e assina o visto de homologação da chefia na ficha do expediente.
4. **Administrador**: Gestão total de usuários, parâmetros e auditoria.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: [Python 3.13+](https://www.python.org/)
- **Framework Web**: [Django 5.2](https://www.djangoproject.com/)
- **Banco de Dados**: SQLite (configurado para desenvolvimento e portabilidade)
- **Geração de Relatórios**: [ReportLab](https://www.reportlab.com/) (PDF) e [OpenPyXL](https://openpyxl.readthedocs.io/) (Excel)
- **Visualização de Dados**: [Chart.js](https://www.chartjs.org/)
- **Ícones**: Font Awesome 5 Free
- **Qualidade de Código**: [Ruff](https://astral.sh/ruff)

---

## ⚙️ Instalação e Execução

### 1. Clonar o repositório
```bash
git clone https://github.com/linocordeiro/app_viaturas.git
cd app_viaturas
```

### 2. Criar e ativar o ambiente virtual
```bash
python -m venv .venv

# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# No Linux / macOS:
source .venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
# Ou utilizando as dependências listadas no pyproject.toml
pip install django reportlab openpyxl
```

### 4. Aplicar migrações do banco de dados
```bash
python manage.py migrate
```

### 5. Carga de Dados Inicial (Opcional para Demonstração)
```bash
python manage.py seed_data
```

### 6. Iniciar o servidor de desenvolvimento
```bash
python manage.py runserver
```
Acesse a aplicação no navegador em: `http://127.0.0.1:8000/`

---

## 🧪 Execução de Testes Automatizados

O sistema conta com suíte de testes unitários e de integração cobrindo regras de negócio, validações de odômetro, unicidade de fichas e bloqueio de edições pós-encerramento:

```bash
python manage.py test
```

---

## 📄 Licença

Uso restrito e institucional sob a licença definida no arquivo [LICENSE](LICENSE).

---

<p align="center">
  <strong>Polícia Federal — Ministério da Justiça e Segurança Pública</strong>
</p>