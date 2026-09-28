from datetime import date, time

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone

from veiculos.models import Viatura


class FichaControle(models.Model):
    """
    Ficha de Controle Diário de Viaturas da Polícia Federal.
    Regra mandatória: Não pode haver mais de uma ficha por data de expediente.
    Ao ser encerrada, a ficha fica bloqueada para alterações e inclusão de registros.
    """
    STATUS_ABERTA = "ABERTA"
    STATUS_ENCERRADA = "ENCERRADA"

    STATUS_CHOICES = [
        (STATUS_ABERTA, "Aberta"),
        (STATUS_ENCERRADA, "Encerrada"),
    ]

    data_expediente = models.DateField(
        "Data do Expediente",
        default=date.today,
        help_text="Data correspondente ao expediente de controle das viaturas"
    )
    horario_inicio = models.TimeField(
        "Horário de Início do Expediente",
        default=time(7, 0),
        help_text="Ex: 07:00 ou 08:00"
    )
    horario_termino = models.TimeField(
        "Horário de Término do Expediente",
        default=time(19, 0),
        help_text="Ex: 19:00 ou término de plantão"
    )

    vigilante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="fichas_preenchidas",
        verbose_name="Vigilante Responsável do Dia",
        help_text="Pessoa responsável por preencher a ficha naquele dia"
    )
    nome_vigilante = models.CharField(
        "Nome do Vigilante / Plantonista",
        max_length=150,
        help_text="Nome legível para assinatura da ficha física/digital"
    )

    status = models.CharField(
        "Status da Ficha",
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ABERTA
    )

    # Assinatura do Vigilante / Plantonista
    assinatura_vigilante = models.BooleanField(
        "Assinatura do Vigilante",
        default=False
    )
    vigilante_assinatura_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fichas_assinadas_vigilante",
        verbose_name="Assinado por (Vigilante)"
    )
    data_assinatura_vigilante = models.DateTimeField(
        "Data/Hora da Assinatura do Vigilante",
        null=True,
        blank=True
    )

    # Visto do Responsável pelas Viaturas
    visto_responsavel = models.BooleanField(
        "Visto do Responsável pelas Viaturas",
        default=False
    )
    responsavel_visto_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fichas_vistadas_responsavel",
        verbose_name="Assinado por (Responsável)"
    )
    data_visto_responsavel = models.DateTimeField(
        "Data/Hora do Visto do Responsável",
        null=True,
        blank=True
    )

    # Visto da Chefia
    visto_chefia = models.BooleanField(
        "Visto da Chefia",
        default=False
    )
    chefia_visto_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fichas_vistadas_chefia",
        verbose_name="Assinado por (Chefia)"
    )
    data_visto_chefia = models.DateTimeField(
        "Data/Hora do Visto da Chefia",
        null=True,
        blank=True
    )

    observacoes = models.TextField("Observações Gerais do Expediente", blank=True, null=True)

    encerrada_em = models.DateTimeField("Data de Encerramento", null=True, blank=True)
    encerrada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fichas_encerradas_pelo_usuario",
        verbose_name="Encerrada por"
    )

    data_criacao = models.DateTimeField("Data de Criação", auto_now_add=True)
    data_atualizacao = models.DateTimeField("Última Atualização", auto_now=True)

    class Meta:
        verbose_name = "Ficha de Controle Diário"
        verbose_name_plural = "Fichas de Controle Diário"
        ordering = ["-data_expediente"]

    def __str__(self):
        return f"Ficha {self.data_expediente.strftime('%d/%m/%Y')} - {self.get_status_display()}"

    @property
    def pode_editar(self):
        """Uma ficha encerrada não pode mais ser editada nem receber registros."""
        return self.status == self.STATUS_ABERTA

    def assinar_vigilante(self, usuario):
        """Aplica a assinatura eletrônica do vigilante/plantonista na ficha."""
        self.assinatura_vigilante = True
        self.vigilante_assinatura_usuario = usuario
        self.data_assinatura_vigilante = timezone.now()
        self.save(update_fields=[
            "assinatura_vigilante",
            "vigilante_assinatura_usuario",
            "data_assinatura_vigilante",
            "data_atualizacao",
        ])

    def encerrar_ficha(self, usuario):
        """
        Encerra formalmente a ficha do expediente.
        Ao encerrar, a assinatura eletrônica do vigilante é lançada automaticamente caso ainda não tenha sido aplicada.
        """
        if self.status == self.STATUS_ENCERRADA:
            return
        agora = timezone.now()
        self.status = self.STATUS_ENCERRADA
        self.encerrada_em = agora
        self.encerrada_por = usuario
        campos_atualizar = ["status", "encerrada_em", "encerrada_por", "data_atualizacao"]

        if not self.assinatura_vigilante:
            self.assinatura_vigilante = True
            self.vigilante_assinatura_usuario = usuario
            self.data_assinatura_vigilante = agora
            campos_atualizar.extend(["assinatura_vigilante", "vigilante_assinatura_usuario", "data_assinatura_vigilante"])

        self.save(update_fields=campos_atualizar)


class RegistroUso(models.Model):
    """
    Registro individual de movimentação (saída, chegada ou ambos) de viatura na ficha do dia.
    Cada ficha diária registra exclusivamente os lançamentos ocorridos no seu expediente.
    """
    STATUS_EM_TRANSITO = "EM_TRANSITO"
    STATUS_CONCLUIDO = "CONCLUIDO"
    STATUS_CANCELADO = "CANCELADO"

    STATUS_CHOICES = [
        (STATUS_EM_TRANSITO, "Em Trânsito / Aberto"),
        (STATUS_CONCLUIDO, "Concluído / Retornou"),
        (STATUS_CANCELADO, "Cancelado"),
    ]

    TIPO_SAIDA = "SAIDA"
    TIPO_CHEGADA = "CHEGADA"
    TIPO_COMPLETO = "COMPLETO"

    TIPO_CHOICES = [
        (TIPO_SAIDA, "Apenas Saída no Expediente"),
        (TIPO_CHEGADA, "Apenas Retorno/Entrada no Expediente"),
        (TIPO_COMPLETO, "Saída e Retorno no mesmo Expediente"),
    ]

    ficha = models.ForeignKey(
        FichaControle,
        on_delete=models.CASCADE,
        related_name="registros",
        verbose_name="Ficha Diária"
    )
    viatura = models.ForeignKey(
        Viatura,
        on_delete=models.PROTECT,
        related_name="registros_uso",
        verbose_name="Viatura"
    )
    tipo_movimentacao = models.CharField(
        "Tipo de Movimentação",
        max_length=15,
        choices=TIPO_CHOICES,
        default=TIPO_COMPLETO,
        help_text="Identifica se o registro é apenas de saída, apenas de retorno ou ambos"
    )
    condutor = models.CharField(
        "Condutor (Nome e Matrícula)",
        max_length=150,
        help_text="Servidor / Policial Federal condutor do veículo"
    )
    condutor_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="viagens_como_condutor",
        verbose_name="Usuário Cadastrado do Condutor"
    )
    destino = models.CharField(
        "Destino / Missão",
        max_length=200,
        help_text="Destino, itinerário ou operação"
    )

    # Dados de Saída (opcionais quando o lançamento nesta ficha for apenas de retorno)
    data_saida = models.DateField("Data de Saída", null=True, blank=True)
    horario_saida = models.TimeField("Horário de Saída", null=True, blank=True)
    odometro_saida = models.PositiveIntegerField("Odômetro de Saída (KM)", null=True, blank=True)

    # Dados de Chegada / Retorno
    data_chegada = models.DateField("Data de Chegada", null=True, blank=True)
    horario_chegada = models.TimeField("Horário de Chegada", null=True, blank=True)
    odometro_chegada = models.PositiveIntegerField("Odômetro de Chegada (KM)", null=True, blank=True)

    # Referência opcional à saída anterior quando o retorno ocorre em outra ficha
    registro_saida_origem = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros_retorno",
        verbose_name="Registro de Saída de Origem",
        help_text="Saída correspondente caso tenha ocorrido em ficha de outro expediente"
    )

    possui_avarias = models.BooleanField("Veículo Possui Avarias?", default=False)
    avarias_encontradas = models.TextField(
        "Espaço para Anotar as Avarias Encontradas",
        blank=True,
        null=True,
        help_text="Descreva avarias, amassados, arranhões ou problemas mecânicos encontrados"
    )

    status = models.CharField(
        "Status do Registro",
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_EM_TRANSITO
    )

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )
    data_criacao = models.DateTimeField("Data do Registro", auto_now_add=True)
    data_atualizacao = models.DateTimeField("Última Atualização", auto_now=True)

    class Meta:
        verbose_name = "Registro de Uso / Saída de Viatura"
        verbose_name_plural = "Registros de Uso de Viaturas"
        ordering = ["id"]

    def __str__(self):
        hora = self.horario_saida or self.horario_chegada or ""
        return f"{self.viatura.placa} - {self.get_tipo_movimentacao_display()} ({hora}) - {self.condutor}"

    @property
    def odometro_saida_efetivo(self):
        if self.odometro_saida is not None:
            return self.odometro_saida
        if self.registro_saida_origem and self.registro_saida_origem.odometro_saida is not None:
            return self.registro_saida_origem.odometro_saida
        return None

    @property
    def data_saida_efetiva(self):
        if self.data_saida:
            return self.data_saida
        if self.registro_saida_origem and self.registro_saida_origem.data_saida:
            return self.registro_saida_origem.data_saida
        return None

    @property
    def horario_saida_efetivo(self):
        if self.horario_saida:
            return self.horario_saida
        if self.registro_saida_origem and self.registro_saida_origem.horario_saida:
            return self.registro_saida_origem.horario_saida
        return None

    @property
    def km_percorrido(self):
        saida_km = self.odometro_saida_efetivo
        if self.odometro_chegada is not None and saida_km is not None:
            return max(0, self.odometro_chegada - saida_km)
        return 0

    @property
    def km_saida(self):
        return self.odometro_saida_efetivo

    @property
    def km_retorno(self):
        return self.odometro_chegada

    @property
    def horario_retorno(self):
        return self.horario_chegada

    def clean(self):
        # Validação de ficha encerrada
        try:
            if (
                getattr(self, "ficha_id", None)
                and self.ficha.status == FichaControle.STATUS_ENCERRADA
                and not self.pk
            ):
                msg = "Não é permitido inserir novos registros em uma ficha já encerrada."
                raise ValidationError(msg)
        except ObjectDoesNotExist:
            pass

        # Validação de dados mínimos: deve possuir dados de saída ou dados de chegada
        has_saida = bool(self.horario_saida or self.odometro_saida is not None)
        has_chegada = bool(self.horario_chegada or self.odometro_chegada is not None)

        if not has_saida and not has_chegada:
            raise ValidationError("O registro deve conter dados de saída ou dados de chegada.")

        # Validação de datas quando ambas presentes no mesmo registro
        d_saida = self.data_saida_efetiva
        h_saida = self.horario_saida_efetivo

        if self.data_chegada and d_saida:
            if self.data_chegada < d_saida:
                raise ValidationError({
                    "data_chegada": (
                        f"A data de chegada ({self.data_chegada.strftime('%d/%m/%Y')}) "
                        f"não pode ser anterior à data de saída ({d_saida.strftime('%d/%m/%Y')})."
                    )
                })

            if self.data_chegada == d_saida and self.horario_chegada and h_saida:
                if self.horario_chegada < h_saida:
                    raise ValidationError({
                        "horario_chegada": "O horário de chegada não pode ser anterior ao horário de saída."
                    })

        # Validação de odômetro
        saida_km = self.odometro_saida_efetivo
        if self.odometro_chegada is not None and saida_km is not None:
            if self.odometro_chegada < saida_km:
                raise ValidationError({
                    "odometro_chegada": (
                        f"Odômetro de chegada ({self.odometro_chegada} km) "
                        f"não pode ser menor que o de saída ({saida_km} km)."
                    )
                })

    def save(self, *args, **kwargs):
        old_viatura_id = None
        if self.pk:
            old_viatura_id = RegistroUso.objects.filter(pk=self.pk).values_list("viatura_id", flat=True).first()

        # Auto-determinação do tipo_movimentacao se não estiver explícito
        if not self.tipo_movimentacao or self.tipo_movimentacao == self.TIPO_COMPLETO:
            if self.horario_saida and self.horario_chegada:
                self.tipo_movimentacao = self.TIPO_COMPLETO
            elif self.horario_saida and not self.horario_chegada:
                self.tipo_movimentacao = self.TIPO_SAIDA
            elif not self.horario_saida and self.horario_chegada:
                self.tipo_movimentacao = self.TIPO_CHEGADA

        self.clean()
        super().save(*args, **kwargs)

        # Se houver registro_saida_origem e este registro for concluído, conclui a saída original também
        if self.registro_saida_origem and self.status == self.STATUS_CONCLUIDO:
            if self.registro_saida_origem.status != self.STATUS_CONCLUIDO:
                self.registro_saida_origem.status = self.STATUS_CONCLUIDO
                self.registro_saida_origem.save(update_fields=["status"])

        # Se trocou a viatura associada, libera a anterior se estiver em uso
        if old_viatura_id and old_viatura_id != self.viatura_id:
            old_v = Viatura.objects.filter(pk=old_viatura_id).first()
            if (
                old_v
                and old_v.status == Viatura.STATUS_EM_USO
                and not RegistroUso.objects.filter(viatura=old_v, status=self.STATUS_EM_TRANSITO).exists()
            ):
                old_v.status = Viatura.STATUS_DISPONIVEL
                old_v.save(update_fields=["status"])

        # Regras de atualização de estado da viatura
        v = self.viatura
        if self.status == self.STATUS_EM_TRANSITO:
            if v.status != Viatura.STATUS_EM_USO:
                v.status = Viatura.STATUS_EM_USO
                v.save(update_fields=["status"])
        elif self.status == self.STATUS_CONCLUIDO:
            # Atualiza odômetro atual da viatura
            if self.odometro_chegada and self.odometro_chegada > v.km_atual:
                v.km_atual = self.odometro_chegada
            # Se houver avaria grave registrada, pode ir para indisponível, caso contrário disponível
            if self.possui_avarias and "impeditiv" in (self.avarias_encontradas or "").lower():
                v.status = Viatura.STATUS_INDISPONIVEL
            else:
                v.status = Viatura.STATUS_DISPONIVEL
            v.save(update_fields=["km_atual", "status"])
        elif self.status == self.STATUS_CANCELADO and v.status == Viatura.STATUS_EM_USO:
            v.status = Viatura.STATUS_DISPONIVEL
            v.save(update_fields=["status"])

