from datetime import date

from django.conf import settings
from django.db import models


class Setor(models.Model):
    """
    Setor ou Unidade da Polícia Federal (ex: DREX, DELEPAT, GISE, GPI, NUTRAN).
    """
    sigla = models.CharField("Sigla", max_length=20, unique=True)
    nome = models.CharField("Nome do Setor / Delegacia", max_length=150)
    responsavel = models.CharField("Responsável pelo Setor", max_length=100, blank=True, null=True)
    ramal = models.CharField("Ramal / Telefone", max_length=30, blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Setor / Unidade"
        verbose_name_plural = "Setores / Unidades"
        ordering = ["sigla"]

    def __str__(self):
        return f"{self.sigla} - {self.nome}"


class Viatura(models.Model):
    """
    Veículo oficial da frota da Polícia Federal.
    """
    STATUS_DISPONIVEL = "DISPONIVEL"
    STATUS_EM_USO = "EM_USO"
    STATUS_MANUTENCAO = "MANUTENCAO"
    STATUS_INDISPONIVEL = "INDISPONIVEL"

    STATUS_CHOICES = [
        (STATUS_DISPONIVEL, "Disponível"),
        (STATUS_EM_USO, "Em Uso / Em Trânsito"),
        (STATUS_MANUTENCAO, "Em Manutenção"),
        (STATUS_INDISPONIVEL, "Indisponível"),
    ]

    TIPO_OSTENSIVA = "OSTENSIVA"
    TIPO_DESCARACTERIZADA = "DESCARACTERIZADA"
    TIPO_ADMINISTRATIVA = "ADMINISTRATIVA"

    TIPO_CHOICES = [
        (TIPO_OSTENSIVA, "Caracterizada / Ostensiva"),
        (TIPO_DESCARACTERIZADA, "Descaracterizada / Operacional"),
        (TIPO_ADMINISTRATIVA, "Administrativa"),
    ]

    CLASSIFICACAO_FROTA = "FROTA"
    CLASSIFICACAO_EXTERNA = "EXTERNA"
    CLASSIFICACAO_PENDENTE = "PENDENTE"

    CLASSIFICACAO_CHOICES = [
        (CLASSIFICACAO_FROTA, "Frota da Unidade"),
        (CLASSIFICACAO_EXTERNA, "Veículo Externo (não pertence à frota)"),
        (CLASSIFICACAO_PENDENTE, "Aguardando Classificação"),
    ]

    ORIGEM_CADASTRO = "CADASTRO"
    ORIGEM_API = "API"
    ORIGEM_MANUAL = "MANUAL"

    ORIGEM_CHOICES = [
        (ORIGEM_CADASTRO, "Cadastro interno"),
        (ORIGEM_API, "Consulta externa por placa"),
        (ORIGEM_MANUAL, "Preenchimento manual (contingência)"),
    ]

    RESP_TIPO_SETOR = "SETOR"
    RESP_TIPO_PESSOA = "PESSOA"

    RESP_TIPO_CHOICES = [
        (RESP_TIPO_SETOR, "Setor"),
        (RESP_TIPO_PESSOA, "Servidor / Pessoa Específica"),
    ]

    placa = models.CharField("Placa", max_length=10, unique=True, help_text="Ex: ABC-1234 ou BRA2E19")
    marca = models.CharField("Marca", max_length=50, help_text="Ex: Toyota, Chevrolet, Ford")
    modelo = models.CharField("Modelo", max_length=80, help_text="Ex: Hilux 4x4, Trailblazer, Ranger")
    ano_fabricacao = models.PositiveIntegerField("Ano Fabricação", default=2022)
    ano_modelo = models.PositiveIntegerField("Ano Modelo", default=2023)
    cor = models.CharField("Cor", max_length=30, default="Preta")
    tipo = models.CharField("Tipo de Viatura", max_length=25, choices=TIPO_CHOICES, default=TIPO_OSTENSIVA)
    chassi = models.CharField("Chassi", max_length=30, blank=True, null=True)

    classificacao = models.CharField(
        "Classificação",
        max_length=10,
        choices=CLASSIFICACAO_CHOICES,
        default=CLASSIFICACAO_FROTA,
        db_index=True,
    )
    classificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="viaturas_classificadas",
        verbose_name="Classificado por",
    )
    classificado_em = models.DateTimeField("Classificado em", null=True, blank=True)

    responsavel_nome = models.CharField("Nome do Responsável", max_length=150, blank=True, default="")
    responsavel_cargo = models.CharField("Cargo do Responsável", max_length=100, blank=True, default="")

    origem_dados = models.CharField(
        "Origem de Marca/Modelo",
        max_length=10,
        choices=ORIGEM_CHOICES,
        default=ORIGEM_CADASTRO,
    )
    provedor_consulta = models.CharField("Provedor da Consulta", max_length=30, blank=True, default="")
    divergencia_dados = models.TextField(
        "Divergência com a Consulta Externa",
        blank=True,
        default="",
        help_text="Preenchido quando a consulta externa retorna marca/modelo diferentes do informado manualmente",
    )

    status = models.CharField("Estado do Veículo", max_length=20, choices=STATUS_CHOICES, default=STATUS_DISPONIVEL)
    setor_pertencente = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="viaturas",
        verbose_name="Unidade / Setor Pertencente",
        help_text="Obrigatório para veículos classificados como frota",
    )

    responsavel_tipo = models.CharField("Tipo de Responsável", max_length=15, choices=RESP_TIPO_CHOICES, default=RESP_TIPO_SETOR)
    responsavel_setor = models.CharField("Setor Responsável", max_length=100, blank=True, null=True)
    responsavel_pessoa = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="viaturas_sob_responsabilidade",
        verbose_name="Servidor Responsável"
    )

    km_atual = models.PositiveIntegerField("Quilometragem Atual (KM)", default=0)
    proxima_manutencao_km = models.PositiveIntegerField(
        "Próxima Manutenção por KM",
        blank=True,
        null=True,
        help_text="Quilometragem limite para a próxima revisão"
    )
    proxima_manutencao_data = models.DateField(
        "Próxima Manutenção por Data",
        blank=True,
        null=True,
        help_text="Data limite para a próxima revisão"
    )

    observacoes = models.TextField("Observações e Avarias Históricas", blank=True, null=True)
    ativo = models.BooleanField("Viatura Ativa na Frota", default=True)
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True)

    class Meta:
        verbose_name = "Viatura"
        verbose_name_plural = "Viaturas"
        ordering = ["modelo", "placa"]

    def __str__(self):
        return f"{self.marca} {self.modelo} - Placa {self.placa} ({self.get_status_display()})"

    @property
    def identificacao_responsavel(self):
        if self.responsavel_nome:
            cargo = f" ({self.responsavel_cargo})" if self.responsavel_cargo else ""
            return f"{self.responsavel_nome}{cargo}"
        if self.responsavel_tipo == self.RESP_TIPO_PESSOA and self.responsavel_pessoa:
            return self.responsavel_pessoa.get_full_name() or self.responsavel_pessoa.username
        if self.responsavel_setor:
            return self.responsavel_setor
        if self.setor_pertencente:
            return self.setor_pertencente.sigla
        return "Não definido"

    @property
    def eh_frota(self):
        return self.classificacao == self.CLASSIFICACAO_FROTA

    def get_alerta_manutencao(self):
        """
        Retorna o nível de alerta da manutenção:
        - status: 'vencida', 'proxima', 'regular'
        - mensagem: descrição do alerta
        - tipo_alerta: 'km', 'data', 'ambos' ou 'nenhum'
        """
        hoje = date.today()
        alertas = []
        is_vencida = False
        is_proxima = False

        # Verificação por KM
        if self.proxima_manutencao_km:
            diferenca_km = self.proxima_manutencao_km - self.km_atual
            if diferenca_km <= 0:
                is_vencida = True
                alertas.append(f"Revisão por KM vencida há {abs(diferenca_km):,} km")
            elif diferenca_km <= 1000:
                is_proxima = True
                alertas.append(f"Revisão por KM próxima (restam {diferenca_km:,} km)")

        # Verificação por Data
        if self.proxima_manutencao_data:
            dias = (self.proxima_manutencao_data - hoje).days
            if dias < 0:
                is_vencida = True
                alertas.append(f"Revisão por Data vencida há {abs(dias)} dias ({self.proxima_manutencao_data.strftime('%d/%m/%Y')})")
            elif dias <= 15:
                is_proxima = True
                alertas.append(f"Revisão por Data próxima ({dias} dias restantes - {self.proxima_manutencao_data.strftime('%d/%m/%Y')})")

        if is_vencida:
            return {
                "status": "vencida",
                "classe": "pf-badge-danger",
                "cor": "#BF0C1D",
                "icone": "fas fa-exclamation-triangle",
                "mensagens": alertas
            }
        if is_proxima:
            return {
                "status": "proxima",
                "classe": "pf-badge-warning",
                "cor": "#E1AD62",
                "icone": "fas fa-clock",
                "mensagens": alertas
            }
        return {
            "status": "regular",
            "classe": "pf-badge-success",
            "cor": "#33A841",
            "icone": "fas fa-check-circle",
            "mensagens": ["Manutenção em dia"]
        }


class Manutencao(models.Model):
    """
    Registro histórico de manutenção preventiva ou corretiva da viatura.
    """
    TIPO_PREVENTIVA = "PREVENTIVA"
    TIPO_CORRETIVA = "CORRETIVA"
    TIPO_REVISAO = "REVISAO"
    TIPO_SINISTRO = "SINISTRO"

    TIPO_CHOICES = [
        (TIPO_PREVENTIVA, "Preventiva Programada"),
        (TIPO_CORRETIVA, "Corretiva / Reparo Mecânico"),
        (TIPO_REVISAO, "Revisão Periódica / Garantia"),
        (TIPO_SINISTRO, "Funilaria / Sinistro / Danos"),
    ]

    viatura = models.ForeignKey(
        Viatura,
        on_delete=models.CASCADE,
        related_name="manutencoes",
        verbose_name="Viatura",
    )

    tipo = models.CharField("Tipo de Manutenção", max_length=20, choices=TIPO_CHOICES, default=TIPO_PREVENTIVA)
    data_manutencao = models.DateField("Data do Serviço", default=date.today)
    km_no_momento = models.PositiveIntegerField("Odômetro na Manutenção (KM)")
    fornecedor_oficina = models.CharField("Oficina / Fornecedor Contratado", max_length=150)
    numero_ordem_servico = models.CharField("Nº Ordem de Serviço / Nota Fiscal", max_length=60, blank=True, null=True)
    descricao_servico = models.TextField("Descrição dos Serviços Realizados")
    pecas_substituidas = models.TextField("Peças e Componentes Substituídos", blank=True, null=True)
    valor_total = models.DecimalField("Valor Total (R$)", max_digits=10, decimal_places=2, default=0.00)

    proxima_revisao_km = models.PositiveIntegerField("Agendar Próxima Revisão (KM)", blank=True, null=True)
    proxima_revisao_data = models.DateField("Agendar Próxima Revisão (Data)", blank=True, null=True)

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )
    data_registro = models.DateTimeField("Data de Registro no Sistema", auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Manutenção"
        verbose_name_plural = "Registros de Manutenção"
        ordering = ["-data_manutencao", "-data_registro"]

    def __str__(self):
        return f"{self.viatura.placa} - {self.get_tipo_display()} em {self.data_manutencao.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualiza a data e km da próxima revisão na viatura caso definidos
        if self.proxima_revisao_km or self.proxima_revisao_data:
            v = self.viatura
            if self.proxima_revisao_km:
                v.proxima_manutencao_km = self.proxima_revisao_km
            if self.proxima_revisao_data:
                v.proxima_manutencao_data = self.proxima_revisao_data
            v.save(update_fields=["proxima_manutencao_km", "proxima_manutencao_data"])


class ConfiguracaoConsultaPlaca(models.Model):
    """
    Configurações institucionais da consulta externa de veículos por placa.
    Permite alternar entre provedor gratuito e oficial SERPRO, além de configurar
    o proxy corporativo da Polícia Federal e monitorar a saúde das chamadas.
    """
    PROVEDOR_GRATUITO = "GRATUITO"
    PROVEDOR_SERPRO = "SERPRO"

    PROVEDOR_CHOICES = [
        (PROVEDOR_GRATUITO, "API gratuita (plano de testes / gratuito)"),
        (PROVEDOR_SERPRO, "API do Serpro (convênio institucional)"),
    ]

    consulta_habilitada = models.BooleanField("Consulta externa habilitada", default=True)
    provedor_ativo = models.CharField(
        "Provedor ativo",
        max_length=10,
        choices=PROVEDOR_CHOICES,
        default=PROVEDOR_GRATUITO,
    )
    proxy_url = models.CharField(
        "Proxy institucional",
        max_length=200,
        blank=True,
        default="",
        help_text="Ex: http://proxy.pf.gov.br:8080 (vazio = usa HTTPS_PROXY do ambiente)",
    )
    timeout_segundos = models.PositiveSmallIntegerField("Timeout (segundos)", default=5)
    cache_dias = models.PositiveSmallIntegerField("Validade do cache (dias)", default=90)

    # Parâmetros Provedor Gratuito
    gratuito_url = models.CharField(
        "URL da consulta",
        max_length=300,
        blank=True,
        default="",
        help_text="Use {placa} (e {token}, se o token for passado na URL). Ex: https://api.exemplo.com.br/placa/{placa}",
    )
    gratuito_token = models.CharField("Token de acesso", max_length=300, blank=True, default="")
    gratuito_cabecalho = models.CharField(
        "Cabeçalho do token",
        max_length=60,
        blank=True,
        default="Authorization",
        help_text="Vazio = não envia cabeçalho (token na URL)",
    )
    gratuito_prefixo = models.CharField(
        "Prefixo do token",
        max_length=30,
        blank=True,
        default="Bearer ",
        help_text="Ex: 'Bearer ' ou vazio",
    )

    # Parâmetros Provedor SERPRO
    serpro_url_token = models.CharField(
        "URL de obtenção do token",
        max_length=300,
        blank=True,
        default="https://gateway.apiserpro.serpro.gov.br/token",
    )
    serpro_url_consulta = models.CharField(
        "URL da consulta",
        max_length=300,
        blank=True,
        default="",
        help_text="Conforme o contrato/serviço contratado. Use {placa}.",
    )
    serpro_consumer_key = models.CharField("Consumer Key", max_length=200, blank=True, default="")
    serpro_consumer_secret = models.CharField("Consumer Secret", max_length=200, blank=True, default="")

    # Circuit Breaker e Diagnóstico
    falhas_consecutivas = models.PositiveIntegerField(default=0)
    circuito_aberto_ate = models.DateTimeField(null=True, blank=True)
    ultimo_sucesso = models.DateTimeField(null=True, blank=True)
    ultima_falha = models.DateTimeField(null=True, blank=True)
    ultimo_erro = models.CharField(max_length=300, blank=True, default="")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração da Consulta de Placa"
        verbose_name_plural = "Configuração da Consulta de Placa"

    def __str__(self):
        return f"Configuração ({self.get_provedor_ativo_display()}) - {'Ativa' if self.consulta_habilitada else 'Desativada'}"

    @classmethod
    def obter_configuracao(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PlacaConsultada(models.Model):
    """
    Cache local de placas consultadas via API externa.
    Evita chamadas repetidas na rede externa para veículos recorrentes.
    """
    placa = models.CharField("Placa", max_length=8, unique=True)
    marca = models.CharField("Marca", max_length=80)
    modelo = models.CharField("Modelo", max_length=120)
    cor = models.CharField("Cor", max_length=40, blank=True, default="")
    ano = models.CharField("Ano", max_length=10, blank=True, default="")
    provedor = models.CharField("Provedor", max_length=30, blank=True, default="")
    consultado_em = models.DateTimeField("Consultado em", auto_now=True)

    class Meta:
        verbose_name = "Placa Consultada (cache)"
        verbose_name_plural = "Placas Consultadas (cache)"
        ordering = ["-consultado_em"]

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo} ({self.provedor})"

