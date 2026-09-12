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

    def encerrar_ficha(self, usuario):
        """Encerra formalmente a ficha do expediente."""
        if self.status == self.STATUS_ENCERRADA:
            return
        self.status = self.STATUS_ENCERRADA
        self.encerrada_em = timezone.now()
        self.encerrada_por = usuario
        self.save(update_fields=["status", "encerrada_em", "encerrada_por", "data_atualizacao"])


class RegistroUso(models.Model):
    """
    Registro individual de movimentação (saída e chegada) de viatura na ficha do dia.
    """
    STATUS_EM_TRANSITO = "EM_TRANSITO"
    STATUS_CONCLUIDO = "CONCLUIDO"
    STATUS_CANCELADO = "CANCELADO"

    STATUS_CHOICES = [
        (STATUS_EM_TRANSITO, "Em Trânsito / Aberto"),
        (STATUS_CONCLUIDO, "Concluído / Retornou"),
        (STATUS_CANCELADO, "Cancelado"),
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

    data_saida = models.DateField("Data de Saída", default=timezone.now)
    horario_saida = models.TimeField("Horário de Saída")
    odometro_saida = models.PositiveIntegerField("Odômetro de Saída (KM)")

    data_chegada = models.DateField("Data de Chegada", null=True, blank=True)
    horario_chegada = models.TimeField("Horário de Chegada", null=True, blank=True)
    odometro_chegada = models.PositiveIntegerField("Odômetro de Chegada (KM)", null=True, blank=True)

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
        ordering = ["horario_saida", "id"]

    def __str__(self):
        return f"{self.viatura.placa} - Saída: {self.horario_saida} - {self.condutor}"

    @property
    def km_percorrido(self):
        if self.odometro_chegada and self.odometro_saida:
            return max(0, self.odometro_chegada - self.odometro_saida)
        return 0

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

        # Validação de datas
        if self.data_chegada and self.data_saida:
            if self.data_chegada < self.data_saida:
                raise ValidationError({
                    "data_chegada": (
                        f"A data de chegada ({self.data_chegada.strftime('%d/%m/%Y')}) "
                        f"não pode ser anterior à data de saída ({self.data_saida.strftime('%d/%m/%Y')})."
                    )
                })

            # Se for a mesma data, valida horário
            if (
                self.data_chegada == self.data_saida
                and self.horario_chegada
                and self.horario_saida
                and self.horario_chegada < self.horario_saida
            ):
                raise ValidationError({
                    "horario_chegada": "O horário de chegada não pode ser anterior ao horário de saída no mesmo dia."
                })

        # Validação de odômetro
        if (
            self.odometro_chegada is not None
            and self.odometro_saida is not None
            and self.odometro_chegada < self.odometro_saida
        ):
            raise ValidationError({
                "odometro_chegada": (
                    f"Odômetro de chegada ({self.odometro_chegada} km) "
                    f"não pode ser menor que o de saída ({self.odometro_saida} km)."
                )
            })

    def save(self, *args, **kwargs):
        old_viatura_id = None
        if self.pk:
            old_viatura_id = RegistroUso.objects.filter(pk=self.pk).values_list("viatura_id", flat=True).first()

        self.clean()
        super().save(*args, **kwargs)

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

