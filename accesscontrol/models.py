from django.conf import settings
from django.db import models


class Modulo(models.Model):
    """
    Módulo principal do sistema (ex: Operação Diária, Gestão de Frota, Gestão de Usuários).
    Serve como organização hierárquica para montar menus e dashboards.
    """

    nome = models.CharField("Nome", max_length=100)
    codigo = models.SlugField("Código", unique=True, help_text="Ex: operacao_diaria, frota, usuarios")
    icone = models.CharField("Ícone (FontAwesome)", max_length=60, blank=True, default="fas fa-cube")
    ordem = models.PositiveIntegerField("Ordem no menu", default=0)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class Submodulo(models.Model):
    """
    Submódulo dentro de um módulo (ex: Gestão de Viaturas, Gestão de Manutenção).
    """

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name="submodulos",
        verbose_name="Módulo",
    )
    nome = models.CharField("Nome", max_length=100)
    codigo = models.SlugField("Código", help_text="Único dentro do módulo. Ex: viaturas, manutencao")
    ordem = models.PositiveIntegerField("Ordem", default=0)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Submódulo"
        verbose_name_plural = "Submódulos"
        unique_together = ("modulo", "codigo")
        ordering = ["ordem", "nome"]

    def __str__(self):
        return f"{self.modulo.nome} / {self.nome}"


class Acao(models.Model):
    """
    Unidade real de permissão. Representa uma tela/rota, um botão/ação dentro de uma tela,
    ou a visibilidade de um dado/widget no dashboard.

    Exemplos de codigo_completo:
      - operacao_diaria.fichas.visualizar
      - frota.viaturas.editar
      - operacao_diaria.fichas.exportar_pdf
    """

    TIPO_TELA = "tela"
    TIPO_ACAO = "acao"
    TIPO_DADO = "dado"

    TIPO_CHOICES = [
        (TIPO_TELA, "Acesso a tela / rota"),
        (TIPO_ACAO, "Ação / botão dentro de uma tela"),
        (TIPO_DADO, "Visibilidade de dado / widget"),
    ]

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name="acoes",
        verbose_name="Módulo",
    )
    submodulo = models.ForeignKey(
        Submodulo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="acoes",
        verbose_name="Submódulo",
    )
    nome = models.CharField("Nome legível", max_length=150)
    codigo = models.SlugField(
        "Código da ação",
        help_text="Ex: criar, editar, exportar_pdf, apor_visto_chefia",
    )
    # Campo desnormalizado para uso em queries (values_list) sem iterar objetos Python
    codigo_completo = models.CharField(
        "Código completo",
        max_length=200,
        unique=True,
        editable=False,
        help_text="Gerado automaticamente. Ex: frota.viaturas.editar",
    )
    tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES, default=TIPO_ACAO)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Ação"
        verbose_name_plural = "Ações"
        unique_together = ("modulo", "submodulo", "codigo")
        ordering = ["modulo__ordem", "submodulo__ordem", "codigo"]

    def save(self, *args, **kwargs):
        # Monta o código completo desnormalizado
        partes = [self.modulo.codigo]
        if self.submodulo_id:
            # Garante que o submodulo está carregado
            if not hasattr(self, "_submodulo_codigo"):
                self._submodulo_codigo = Submodulo.objects.filter(pk=self.submodulo_id).values_list("codigo", flat=True).first()
            partes.append(self._submodulo_codigo or "")
        partes.append(self.codigo)
        self.codigo_completo = ".".join(filter(None, partes))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_completo} — {self.nome}"


class Perfil(models.Model):
    """
    Perfil de acesso. Um usuário pode ter múltiplos perfis.
    A permissão efetiva é a UNIÃO das ações de todos os perfis ativos do usuário.
    """

    nome = models.CharField("Nome", max_length=100, unique=True)
    descricao = models.TextField("Descrição", blank=True)
    ativo = models.BooleanField("Ativo", default=True)
    acoes = models.ManyToManyField(
        Acao,
        related_name="perfis",
        blank=True,
        verbose_name="Ações permitidas",
    )

    class Meta:
        verbose_name = "Perfil de Acesso"
        verbose_name_plural = "Perfis de Acesso"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class UsuarioPerfil(models.Model):
    """
    Tabela through explícita para rastrear a atribuição de perfis a usuários.
    Permite auditoria (quem concedeu, quando) e desativação sem apagar histórico.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfis_atribuidos",
        verbose_name="Usuário",
    )
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        verbose_name="Perfil",
    )
    atribuido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Atribuído por",
    )
    atribuido_em = models.DateTimeField("Atribuído em", auto_now_add=True)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"
        unique_together = ("usuario", "perfil")
        ordering = ["-atribuido_em"]

    def __str__(self):
        status = "ativo" if self.ativo else "inativo"
        return f"{self.usuario} → {self.perfil} ({status})"


class DashboardWidget(models.Model):
    """
    Widgets do dashboard. Cada widget é visível apenas para os perfis autorizados.
    """

    codigo = models.SlugField("Código", unique=True, help_text="Ex: metricas_frota, alertas_manutencao")
    nome = models.CharField("Nome", max_length=150)
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Módulo relacionado",
    )
    ordem = models.PositiveIntegerField("Ordem de exibição", default=0)
    ativo = models.BooleanField("Ativo", default=True)
    perfis = models.ManyToManyField(
        Perfil,
        related_name="widgets",
        blank=True,
        verbose_name="Perfis com acesso",
    )

    class Meta:
        verbose_name = "Widget do Dashboard"
        verbose_name_plural = "Widgets do Dashboard"
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class LogAcesso(models.Model):
    """
    Registro imutável de acessos negados e alterações de perfil.
    Essencial para auditoria em ambiente de delegacia.
    """

    TIPO_NEGADO = "NEGADO"
    TIPO_ATRIBUICAO = "ATRIBUICAO"
    TIPO_REMOCAO = "REMOCAO"

    TIPO_CHOICES = [
        (TIPO_NEGADO, "Acesso negado"),
        (TIPO_ATRIBUICAO, "Perfil atribuído"),
        (TIPO_REMOCAO, "Perfil removido"),
    ]

    tipo = models.CharField("Tipo", max_length=15, choices=TIPO_CHOICES)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs_acesso",
        verbose_name="Usuário",
    )
    acao_tentada = models.CharField("Ação tentada", max_length=200, blank=True)
    rota = models.CharField("Rota / URL", max_length=500, blank=True)
    ip = models.GenericIPAddressField("Endereço IP", null=True, blank=True)
    detalhe = models.TextField("Detalhe", blank=True)
    registrado_em = models.DateTimeField("Registrado em", auto_now_add=True)

    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ["-registrado_em"]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.usuario} — {self.acao_tentada} em {self.registrado_em.strftime('%d/%m/%Y %H:%M')}"


class CodigoAcao:
    """Catálogo canônico de códigos numéricos de ações do sistema."""

    # Faixa 1000 — Autenticação e Sessão
    AUTH_LOGIN = 1001
    AUTH_LOGOUT = 1002
    AUTH_FALHA = 1003
    AUTH_SENHA_ALTERADA = 1004

    # Faixa 2000 — Segurança e Controle de Acesso
    SEC_ACESSO_NEGADO = 2001
    SEC_PERFIL_ATRIBUIDO = 2002
    SEC_PERFIL_REMOVIDO = 2003
    SEC_USUARIO_DESATIVADO = 2004
    SEC_USUARIO_ATIVADO = 2005

    # Faixa 3000 — Gestão de Frota
    VIAT_CRIADA = 3001
    VIAT_EDITADA = 3002
    VIAT_STATUS_ALTERADO = 3003
    VIAT_DESATIVADA = 3004
    MANUT_REGISTRADA = 3010
    MANUT_EDITADA = 3011

    # Faixa 4000 — Operação Diária (Fichas e Viaturas)
    FICH_ABERTA = 4001
    FICH_EDITADA = 4002
    FICH_ENCERRADA = 4003
    FICH_SAIDA_REGISTRADA = 4010
    FICH_RETORNO_REGISTRADO = 4011
    FICH_MOVIMENTACAO_EDITADA = 4012
    FICH_VISTO_NUTRAN = 4020
    FICH_VISTO_CHEFIA = 4021
    FICH_EXPORTADA_PDF = 4030
    FICH_EXPORTADA_EXCEL = 4031

    # Faixa 5000 — Gestão de Usuários
    USER_CRIADO = 5001
    USER_EDITADO = 5002

    # Faixa 9000 — Sistema e Integridade
    SYS_ERRO_500 = 9001
    SYS_ERRO_400 = 9002

    CHOICES = [
        (AUTH_LOGIN, "1001 — Login realizado com sucesso"),
        (AUTH_LOGOUT, "1002 — Logout efetuado"),
        (AUTH_FALHA, "1003 — Falha de autenticação (credenciais inválidas)"),
        (AUTH_SENHA_ALTERADA, "1004 — Alteração de senha de usuário"),
        (SEC_ACESSO_NEGADO, "2001 — Acesso indevido bloqueado por falta de permissão (403)"),
        (SEC_PERFIL_ATRIBUIDO, "2002 — Atribuição de perfil a usuário"),
        (SEC_PERFIL_REMOVIDO, "2003 — Remoção de perfil de usuário"),
        (SEC_USUARIO_DESATIVADO, "2004 — Desativação de usuário"),
        (SEC_USUARIO_ATIVADO, "2005 — Ativação de usuário"),
        (VIAT_CRIADA, "3001 — Cadastro de viatura"),
        (VIAT_EDITADA, "3002 — Edição de dados da viatura"),
        (VIAT_STATUS_ALTERADO, "3003 — Alteração de status da viatura"),
        (VIAT_DESATIVADA, "3004 — Desativação de viatura da frota"),
        (MANUT_REGISTRADA, "3010 — Registro de manutenção de viatura"),
        (MANUT_EDITADA, "3011 — Edição de registro de manutenção"),
        (FICH_ABERTA, "4001 — Abertura de ficha de controle"),
        (FICH_EDITADA, "4002 — Edição de dados da ficha"),
        (FICH_ENCERRADA, "4003 — Encerramento de ficha de controle"),
        (FICH_SAIDA_REGISTRADA, "4010 — Registro de saída de viatura"),
        (FICH_RETORNO_REGISTRADO, "4011 — Registro de retorno de viatura"),
        (FICH_MOVIMENTACAO_EDITADA, "4012 — Edição de movimentação de viatura"),
        (FICH_VISTO_NUTRAN, "4020 — Aposição de visto NUTRAN na ficha"),
        (FICH_VISTO_CHEFIA, "4021 — Aposição de visto da Chefia na ficha"),
        (FICH_EXPORTADA_PDF, "4030 — Exportação de ficha em PDF"),
        (FICH_EXPORTADA_EXCEL, "4031 — Exportação de ficha em Excel"),
        (USER_CRIADO, "5001 — Cadastro de novo usuário"),
        (USER_EDITADO, "5002 — Edição de dados cadastrais de usuário"),
        (SYS_ERRO_500, "9001 — Erro interno do servidor (HTTP 500)"),
        (SYS_ERRO_400, "9002 — Requisição inválida (HTTP 400)"),
    ]

    _MAPA_DESCRICOES = dict(CHOICES)

    @classmethod
    def obter_descricao(cls, codigo: int) -> str:
        desc = cls._MAPA_DESCRICOES.get(codigo)
        if desc:
            return desc.split(" — ", 1)[-1] if " — " in desc else desc
        return f"Ação código {codigo}"

    @classmethod
    def obter_categoria(cls, codigo: int) -> str:
        faixa = codigo // 1000
        mapa = {
            1: "Autenticação",
            2: "Segurança",
            3: "Gestão de Frota",
            4: "Operação Diária",
            5: "Gestão de Usuários",
            9: "Sistema",
        }
        return mapa.get(faixa, "Geral")

    @classmethod
    def obter_badge_info(cls, codigo: int) -> dict:
        faixa = codigo // 1000
        if codigo in (cls.SEC_ACESSO_NEGADO, cls.SYS_ERRO_500, cls.AUTH_FALHA):
            return {"classe": "pf-badge-danger", "cor": "#BF0C1D"}
        elif faixa == 1:
            return {"classe": "pf-badge-gold", "cor": "#E1AD62"}
        elif faixa == 2:
            return {"classe": "pf-badge-warning", "cor": "#C19515"}
        elif faixa == 3:
            return {"classe": "pf-badge-info", "cor": "#3363CC"}
        elif faixa == 4:
            return {"classe": "pf-badge-success", "cor": "#33A841"}
        elif faixa == 5:
            return {"classe": "pf-badge-dark", "cor": "#111213"}
        return {"classe": "pf-badge-secondary", "cor": "#6A6D7C"}


class LogAuditoria(models.Model):
    """
    Registro completo e imutável de todas as ações, alterações e acessos no sistema.
    Base para auditoria oficial e conformidade com normas institucionais da Polícia Federal.
    """

    codigo = models.PositiveIntegerField("Código da Ação", choices=CodigoAcao.CHOICES, db_index=True)
    descricao = models.CharField("Descrição da Ação", max_length=255)
    categoria = models.CharField("Categoria", max_length=50, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs_auditoria",
        verbose_name="Usuário",
    )
    usuario_repr = models.CharField("Identificação do Usuário", max_length=200, blank=True)
    url = models.CharField("URL Acessada", max_length=500, blank=True)
    metodo_http = models.CharField("Método HTTP", max_length=10, blank=True)
    status_code = models.PositiveIntegerField("Status HTTP", null=True, blank=True)
    ip = models.GenericIPAddressField("Endereço IP", null=True, blank=True)
    objeto_repr = models.CharField("Objeto Afetado", max_length=255, blank=True)
    objeto_id = models.CharField("ID do Objeto", max_length=100, blank=True)
    tabela_afetada = models.CharField("Tabela / Model", max_length=100, blank=True)
    detalhes = models.JSONField("Detalhes da Alteração", default=dict, blank=True)
    criado_em = models.DateTimeField("Data e Hora", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["codigo", "-criado_em"]),
            models.Index(fields=["usuario", "-criado_em"]),
        ]

    def __str__(self):
        return f"[{self.codigo}] {self.descricao} — {self.usuario_repr} em {self.criado_em.strftime('%d/%m/%Y %H:%M:%S')}"

    @property
    def badge_info(self):
        return CodigoAcao.obter_badge_info(self.codigo)

