"""
Constantes de seed compartilhadas entre a migration 0002_seed_perfis e o
comando setup_permissoes. Alterar aqui reflete nos dois lugares.
"""

ESTRUTURA = [
    {
        "nome": "Operação Diária",
        "codigo": "operacao_diaria",
        "icone": "fas fa-clipboard-list",
        "ordem": 1,
        "submodulos": [
            {
                "nome": "Fichas de Controle",
                "codigo": "fichas",
                "ordem": 1,
                "acoes": [
                    ("visualizar", "Visualizar fichas", "tela"),
                    ("criar", "Abrir nova ficha / registrar ficha de hoje", "tela"),
                    ("registrar_saida", "Registrar saída de viatura", "acao"),
                    ("registrar_chegada", "Registrar chegada de viatura", "acao"),
                    ("editar_registro", "Editar registro de saída/chegada", "acao"),
                    ("encerrar", "Encerrar ficha do expediente", "acao"),
                    ("exportar_pdf", "Exportar ficha em PDF", "acao"),
                    ("exportar_excel", "Exportar ficha em Excel", "acao"),
                    ("apor_visto_nutran", "Apor visto do Responsável pelas Viaturas (NUTRAN)", "acao"),
                    ("apor_visto_chefia", "Apor visto da Chefia", "acao"),
                ],
            },
        ],
    },
    {
        "nome": "Gestão de Frota",
        "codigo": "frota",
        "icone": "fas fa-car",
        "ordem": 2,
        "submodulos": [
            {
                "nome": "Viaturas",
                "codigo": "viaturas",
                "ordem": 1,
                "acoes": [
                    ("visualizar", "Visualizar lista e detalhe de viaturas", "tela"),
                    ("criar", "Cadastrar nova viatura", "acao"),
                    ("editar", "Editar dados da viatura", "acao"),
                    ("desativar", "Desativar viatura da frota", "acao"),
                ],
            },
            {
                "nome": "Manutenção",
                "codigo": "manutencao",
                "ordem": 2,
                "acoes": [
                    ("visualizar", "Visualizar histórico de manutenções", "tela"),
                    ("criar", "Registrar manutenção", "acao"),
                    ("editar", "Editar registro de manutenção", "acao"),
                ],
            },
        ],
    },
    {
        "nome": "Gestão de Usuários",
        "codigo": "usuarios",
        "icone": "fas fa-users",
        "ordem": 3,
        "submodulos": [
            {
                "nome": "Cadastro de Usuários",
                "codigo": "cadastro",
                "ordem": 1,
                "acoes": [
                    ("visualizar", "Visualizar lista de usuários", "tela"),
                    ("criar", "Cadastrar novo usuário", "acao"),
                    ("editar", "Editar dados do usuário", "acao"),
                    ("toggle_ativo", "Ativar / desativar usuário", "acao"),
                ],
            },
            {
                "nome": "Gerenciamento de Perfis",
                "codigo": "perfis",
                "ordem": 2,
                "acoes": [
                    ("visualizar", "Visualizar perfis e permissões", "tela"),
                    ("atribuir", "Atribuir perfil a usuário", "acao"),
                    ("remover", "Remover perfil de usuário", "acao"),
                ],
            },
        ],
    },
    {
        "nome": "Auditoria do Sistema",
        "codigo": "auditoria",
        "icone": "fas fa-shield-alt",
        "ordem": 4,
        "submodulos": [
            {
                "nome": "Logs de Auditoria",
                "codigo": "logs",
                "ordem": 1,
                "acoes": [
                    ("visualizar", "Visualizar logs e trilha de auditoria", "tela"),
                    ("detalhes", "Visualizar detalhes de alteração e payloads", "acao"),
                    ("exportar", "Exportar logs de auditoria", "acao"),
                ],
            },
        ],
    },
]


WIDGETS = [
    ("ficha_hoje", "Status da ficha do dia", 1),
    ("viaturas_em_transito", "Viaturas em trânsito", 2),
    ("metricas_frota", "Métricas da frota (contadores)", 3),
    ("alertas_manutencao", "Alertas de manutenção", 4),
    ("grafico_km_7dias", "Gráfico de KM nos últimos 7 dias", 5),
    ("total_saidas_mes", "Total de saídas no mês", 6),
]

PERFIS = {
    "vigilante": {
        "descricao": "Vigilante / Plantonista responsável pelo preenchimento da ficha diária",
        "acoes": [
            "operacao_diaria.fichas.visualizar",
            "operacao_diaria.fichas.criar",
            "operacao_diaria.fichas.registrar_saida",
            "operacao_diaria.fichas.registrar_chegada",
            "operacao_diaria.fichas.editar_registro",
            "operacao_diaria.fichas.encerrar",
        ],
        "widgets": ["viaturas_em_transito"],
    },
    "nutran": {
        "descricao": "Responsável pelas Viaturas (NUTRAN) — gestão da frota e manutenções",
        "acoes": [
            "frota.viaturas.visualizar",
            "frota.viaturas.criar",
            "frota.viaturas.editar",
            "frota.manutencao.visualizar",
            "frota.manutencao.criar",
            "frota.manutencao.editar",
            "operacao_diaria.fichas.visualizar",
            "operacao_diaria.fichas.apor_visto_nutran",
        ],
        "widgets": ["viaturas_em_transito", "metricas_frota", "alertas_manutencao", "grafico_km_7dias", "total_saidas_mes"],
    },
    "inteligencia": {
        "descricao": "Inteligência — acesso somente leitura e exportação de fichas",
        "acoes": [
            "operacao_diaria.fichas.visualizar",
            "operacao_diaria.fichas.exportar_pdf",
            "operacao_diaria.fichas.exportar_excel",
        ],
        "widgets": ["viaturas_em_transito"],
    },
    "chefia": {
        "descricao": "Chefia — visualização de fichas, exportação e apor visto da chefia",
        "acoes": [
            "operacao_diaria.fichas.visualizar",
            "operacao_diaria.fichas.exportar_pdf",
            "operacao_diaria.fichas.exportar_excel",
            "operacao_diaria.fichas.apor_visto_chefia",
            "frota.viaturas.visualizar",
            "frota.manutencao.visualizar",
        ],
        "widgets": ["viaturas_em_transito"],
    },
    "administrador": {
        "descricao": "Administrador do Sistema — acesso total a todos os módulos e funcionalidades",
        "acoes": "__all__",
        "widgets": "__all__",
    },
}

PERFIL_LEGADO_MAP = {
    "VIGILANTE": "vigilante",
    "RESPONSAVEL_VIATURAS": "nutran",
    "CHEFIA": "chefia",
    "ADMINISTRADOR": "administrador",
}
