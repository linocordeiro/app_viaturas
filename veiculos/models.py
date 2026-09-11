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

    status = models.CharField("Estado do Veículo", max_length=20, choices=STATUS_CHOICES, default=STATUS_DISPONIVEL)
    setor_pertencente = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name="viaturas",
        verbose_name="Unidade / Setor Pertencente"
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
        if self.responsavel_tipo == self.RESP_TIPO_PESSOA and self.responsavel_pessoa:
            return self.responsavel_pessoa.get_full_name() or self.responsavel_pessoa.username
        if self.responsavel_setor:
            return self.responsavel_setor
        return self.setor_pertencente.sigla

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
