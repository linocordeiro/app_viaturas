from datetime import date, datetime, time

from django import forms

from services.consulta_placa import consultar_placa, normalizar_placa, validar_formato_placa
from veiculos.models import Viatura

from .models import FichaControle, RegistroUso


class FichaControleForm(forms.ModelForm):
    TURNO_DIURNO = "DIURNO"
    TURNO_NOTURNO = "NOTURNO"
    TURNO_CHOICES = [
        (TURNO_DIURNO, "Diurno - 07:00 às 19:00"),
        (TURNO_NOTURNO, "Noturno - 19:00 às 07:00"),
    ]

    turno = forms.ChoiceField(
        label="Turno do Expediente",
        choices=TURNO_CHOICES,
        widget=forms.Select(attrs={"class": "pf-select"}),
        help_text="Selecione o turno correspondente ao plantão",
        required=True,
    )

    class Meta:
        model = FichaControle
        fields = ["data_expediente", "nome_vigilante", "observacoes"]
        widgets = {
            "data_expediente": forms.DateInput(
                attrs={"class": "pf-input", "type": "date"},
                format="%Y-%m-%d"
            ),
            "nome_vigilante": forms.TextInput(
                attrs={"class": "pf-input", "placeholder": "Nome completo do vigilante do dia"}
            ),
            "observacoes": forms.Textarea(
                attrs={"class": "pf-textarea", "rows": 2, "placeholder": "Observações do plantão / expediente..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O campo data deve ser editável mas vir preenchido com a data do dia por padrão
        if not self.initial.get("data_expediente") and (not self.instance or not self.instance.pk):
            self.initial["data_expediente"] = date.today()

        # Determina o turno inicial caso seja edição ou já possua valores
        if self.instance and self.instance.pk and self.instance.horario_inicio:
            if self.instance.horario_inicio >= time(19, 0) or self.instance.horario_inicio < time(7, 0):
                self.initial["turno"] = self.TURNO_NOTURNO
            else:
                self.initial["turno"] = self.TURNO_DIURNO
        elif not self.initial.get("turno"):
            hora_atual = datetime.now().time()
            if hora_atual >= time(19, 0) or hora_atual < time(7, 0):
                self.initial["turno"] = self.TURNO_NOTURNO
            else:
                self.initial["turno"] = self.TURNO_DIURNO

    def clean(self):
        cleaned_data = super().clean()
        turno = cleaned_data.get("turno")
        data_exp = cleaned_data.get("data_expediente")

        if turno == self.TURNO_NOTURNO:
            h_inicio = time(19, 0)
            h_termino = time(7, 0)
        else:
            h_inicio = time(7, 0)
            h_termino = time(19, 0)

        cleaned_data["horario_inicio"] = h_inicio
        cleaned_data["horario_termino"] = h_termino

        if data_exp and h_inicio:
            # Verifica se já existe ficha para a mesma data e mesmo turno
            qs = FichaControle.objects.filter(data_expediente=data_exp, horario_inicio=h_inicio)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                turno_desc = "Diurno (07:00 às 19:00)" if turno == self.TURNO_DIURNO else "Noturno (19:00 às 07:00)"
                msg = (
                    f"Já existe uma Ficha de Controle cadastrada para a data "
                    f"{data_exp.strftime('%d/%m/%Y')} no turno {turno_desc}."
                )
                self.add_error("turno", msg)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if "horario_inicio" in self.cleaned_data:
            instance.horario_inicio = self.cleaned_data["horario_inicio"]
        if "horario_termino" in self.cleaned_data:
            instance.horario_termino = self.cleaned_data["horario_termino"]
        if commit:
            instance.save()
        return instance


class RegistroSaidaForm(forms.ModelForm):
    placa = forms.CharField(
        label="Placa do Veículo",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={"class": "pf-input", "id": "id_placa_saida", "placeholder": "Ex: BRA2E19 ou ABC-1234", "style": "text-transform: uppercase;"}),
    )
    marca = forms.CharField(label="Marca", max_length=50, required=False, widget=forms.TextInput(attrs={"class": "pf-input", "id": "id_marca_saida"}))
    modelo = forms.CharField(label="Modelo", max_length=80, required=False, widget=forms.TextInput(attrs={"class": "pf-input", "id": "id_modelo_saida"}))
    cor = forms.CharField(label="Cor", max_length=30, required=False, widget=forms.TextInput(attrs={"class": "pf-input", "id": "id_cor_saida"}))

    class Meta:
        model = RegistroUso
        fields = ["viatura", "condutor", "destino", "data_saida", "horario_saida", "odometro_saida"]
        widgets = {
            "viatura": forms.Select(attrs={"class": "pf-select", "id": "id_select_viatura"}),
            "condutor": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nome e matrícula do condutor"}),
            "destino": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Destino / Missão / Operação"}),
            "data_saida": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "horario_saida": forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
            "odometro_saida": forms.NumberInput(attrs={"class": "pf-input", "placeholder": "KM de saída"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["viatura"].required = False
        # Permite selecionar apenas viaturas ativas e disponíveis (ou a viatura já associada se for edição)
        if self.instance.pk:
            self.fields["viatura"].queryset = Viatura.objects.filter(ativo=True)
            if self.instance.viatura:
                self.initial["placa"] = self.instance.viatura.placa
                self.initial["marca"] = self.instance.viatura.marca
                self.initial["modelo"] = self.instance.viatura.modelo
                self.initial["cor"] = self.instance.viatura.cor
        else:
            self.fields["viatura"].queryset = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_DISPONIVEL)
            # Define hora atual padrão
            self.initial["data_saida"] = datetime.now().strftime("%Y-%m-%d")
            self.initial["horario_saida"] = datetime.now().strftime("%H:%M")

    def clean(self):
        cleaned_data = super().clean()
        viatura = cleaned_data.get("viatura")
        placa = normalizar_placa(cleaned_data.get("placa") or "")

        if not viatura and placa:
            if not validar_formato_placa(placa):
                self.add_error("placa", "Formato de placa inválido. Use o padrão Mercosul (ex: BRA2E19) ou antigo (ABC1234).")
                return cleaned_data

            viatura = Viatura.objects.filter(placa=placa).first()
            if not viatura:
                marca = (cleaned_data.get("marca") or "").strip()
                modelo = (cleaned_data.get("modelo") or "").strip()
                cor = (cleaned_data.get("cor") or "").strip()

                if not (marca and modelo):
                    res = consultar_placa(placa)
                    if res.sucesso:
                        marca = res.marca
                        modelo = res.modelo
                        cor = res.cor or cor

                if not (marca and modelo):
                    self.add_error("marca", "Marca e modelo não identificados. Preencha os campos manualmente para contingência.")
                    return cleaned_data

                viatura = Viatura.objects.create(
                    placa=placa,
                    marca=marca.title(),
                    modelo=modelo,
                    cor=cor or "Preta",
                    classificacao=Viatura.CLASSIFICACAO_PENDENTE,
                    origem_dados=Viatura.ORIGEM_API if marca else Viatura.ORIGEM_MANUAL,
                    status=Viatura.STATUS_DISPONIVEL,
                )

            cleaned_data["viatura"] = viatura
            self.instance.viatura = viatura

        if not cleaned_data.get("viatura"):
            self.add_error("placa", "Informe a placa do veículo ou selecione uma viatura cadastrada.")

        return cleaned_data


class RegistroChegadaForm(forms.ModelForm):
    class Meta:
        model = RegistroUso
        fields = ["data_chegada", "horario_chegada", "odometro_chegada", "possui_avarias", "avarias_encontradas"]
        widgets = {
            "data_chegada": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "horario_chegada": forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
            "odometro_chegada": forms.NumberInput(attrs={"class": "pf-input", "placeholder": "KM de retorno"}),
            "possui_avarias": forms.CheckboxInput(attrs={"class": "pf-checkbox"}),
            "avarias_encontradas": forms.Textarea(attrs={"class": "pf-textarea", "rows": 3, "placeholder": "Descreva detalhadamente arranhões, amassados, itens faltantes ou falhas mecânicas..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.data_chegada:
            self.initial["data_chegada"] = datetime.now().strftime("%Y-%m-%d")
        if not self.instance.horario_chegada:
            self.initial["horario_chegada"] = datetime.now().strftime("%H:%M")
        if not self.instance.odometro_chegada and self.instance.odometro_saida:
            self.initial["odometro_chegada"] = self.instance.odometro_saida

    def clean(self):
        cleaned_data = super().clean()
        data_chegada = cleaned_data.get("data_chegada")
        horario_chegada = cleaned_data.get("horario_chegada")
        odometro_chegada = cleaned_data.get("odometro_chegada")
        possui_avarias = cleaned_data.get("possui_avarias")
        avarias = cleaned_data.get("avarias_encontradas")

        if not data_chegada:
            self.add_error("data_chegada", "Informe a data de retorno da viatura.")
        if not horario_chegada:
            self.add_error("horario_chegada", "Informe o horário de retorno da viatura.")
        if odometro_chegada is None:
            self.add_error("odometro_chegada", "Informe o odômetro de retorno da viatura.")
        elif self.instance.odometro_saida and odometro_chegada < self.instance.odometro_saida:
            self.add_error("odometro_chegada", f"Odômetro de chegada ({odometro_chegada} km) não pode ser inferior ao de saída ({self.instance.odometro_saida} km).")

        if possui_avarias and not avarias:
            self.add_error("avarias_encontradas", "Ao marcar que o veículo possui avarias, é obrigatório preencher o espaço para anotar as avarias encontradas.")

        return cleaned_data


class RegistroChegadaAvulsaForm(forms.ModelForm):
    """
    Formulário para lançamento de retorno/chegada de viatura em um novo expediente,
    quando a saída ocorreu em ficha/plantão anterior.
    """
    class Meta:
        model = RegistroUso
        fields = [
            "viatura", "registro_saida_origem", "condutor", "destino",
            "data_chegada", "horario_chegada", "odometro_chegada",
            "possui_avarias", "avarias_encontradas"
        ]
        widgets = {
            "viatura": forms.Select(attrs={"class": "pf-select", "id": "id_viatura_chegada"}),
            "registro_saida_origem": forms.HiddenInput(),
            "condutor": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nome e matrícula do condutor que devolveu a viatura"}),
            "destino": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Destino / Missão cumprida"}),
            "data_chegada": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "horario_chegada": forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
            "odometro_chegada": forms.NumberInput(attrs={"class": "pf-input", "placeholder": "KM de retorno no odômetro"}),
            "possui_avarias": forms.CheckboxInput(attrs={"class": "pf-checkbox"}),
            "avarias_encontradas": forms.Textarea(attrs={"class": "pf-textarea", "rows": 3, "placeholder": "Descreva avarias, amassados, arranhões ou problemas mecânicos encontrados..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permite selecionar viaturas que estão atualmente em trânsito (em uso)
        self.fields["viatura"].queryset = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_EM_USO)
        self.fields["registro_saida_origem"].required = False
        self.fields["condutor"].required = False
        self.fields["destino"].required = False

        if not self.initial.get("data_chegada"):
            self.initial["data_chegada"] = datetime.now().strftime("%Y-%m-%d")
        if not self.initial.get("horario_chegada"):
            self.initial["horario_chegada"] = datetime.now().strftime("%H:%M")

    def clean(self):
        cleaned_data = super().clean()
        viatura = cleaned_data.get("viatura")
        condutor = cleaned_data.get("condutor")
        destino = cleaned_data.get("destino")
        odometro_chegada = cleaned_data.get("odometro_chegada")
        data_chegada = cleaned_data.get("data_chegada")
        horario_chegada = cleaned_data.get("horario_chegada")
        possui_avarias = cleaned_data.get("possui_avarias")
        avarias = cleaned_data.get("avarias_encontradas")

        saida_origem = None
        if viatura:
            saida_origem = RegistroUso.objects.filter(
                viatura=viatura,
                status=RegistroUso.STATUS_EM_TRANSITO
            ).order_by("-data_saida", "-horario_saida", "-id").first()

        if not condutor:
            if saida_origem and saida_origem.condutor:
                cleaned_data["condutor"] = saida_origem.condutor
            else:
                self.add_error("condutor", "Informe o nome e matrícula do condutor responsável pela devolução.")

        if not destino and saida_origem and saida_origem.destino:
            cleaned_data["destino"] = saida_origem.destino

        if not data_chegada:
            self.add_error("data_chegada", "Informe a data de chegada da viatura.")
        if not horario_chegada:
            self.add_error("horario_chegada", "Informe o horário de chegada da viatura.")
        if odometro_chegada is None:
            self.add_error("odometro_chegada", "Informe o odômetro de chegada da viatura.")
        elif viatura:
            km_min = saida_origem.odometro_saida if saida_origem and saida_origem.odometro_saida is not None else viatura.km_atual
            if km_min and odometro_chegada < km_min:
                self.add_error("odometro_chegada", f"Odômetro de chegada ({odometro_chegada} km) não pode ser inferior ao odômetro de saída ({km_min} km).")

            if saida_origem and saida_origem.data_saida and data_chegada:
                if data_chegada < saida_origem.data_saida:
                    self.add_error("data_chegada", f"A data de chegada não pode ser anterior à data de saída ({saida_origem.data_saida.strftime('%d/%m/%Y')}).")

        if possui_avarias and not avarias:
            self.add_error("avarias_encontradas", "Ao marcar que o veículo possui avarias, descreva os danos encontrados.")

        return cleaned_data


class RegistroEdicaoForm(forms.ModelForm):
    """
    Formulário para edição completa do registro de uso de viatura,
    permitindo alterar dados de saída, dados de retorno/chegada e o status.
    """
    class Meta:
        model = RegistroUso
        fields = [
            "viatura", "condutor", "destino", "data_saida", "horario_saida", "odometro_saida",
            "data_chegada", "horario_chegada", "odometro_chegada", "possui_avarias", "avarias_encontradas",
            "status"
        ]
        widgets = {
            "viatura": forms.Select(attrs={"class": "pf-select"}),
            "condutor": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nome e matrícula do condutor"}),
            "destino": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Destino / Missão / Operação"}),
            "data_saida": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "horario_saida": forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
            "odometro_saida": forms.NumberInput(attrs={"class": "pf-input", "placeholder": "KM de saída"}),
            "data_chegada": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "horario_chegada": forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
            "odometro_chegada": forms.NumberInput(attrs={"class": "pf-input", "placeholder": "KM de retorno"}),
            "possui_avarias": forms.CheckboxInput(attrs={"class": "pf-checkbox"}),
            "avarias_encontradas": forms.Textarea(attrs={"class": "pf-textarea", "rows": 3, "placeholder": "Descreva avarias, problemas mecânicos ou avarias encontradas..."}),
            "status": forms.Select(attrs={"class": "pf-select"}),
        }

    def __init__(self, *args, bloquear_saida=False, **kwargs):
        super().__init__(*args, **kwargs)
        # Permite selecionar qualquer viatura ativa no pátio
        self.fields["viatura"].queryset = Viatura.objects.filter(ativo=True)
        # Campos de chegada podem ser vazios caso a viatura ainda esteja em trânsito
        self.fields["data_chegada"].required = False
        self.fields["horario_chegada"].required = False
        self.fields["odometro_chegada"].required = False
        self.fields["avarias_encontradas"].required = False

        saida_origem = getattr(self.instance, "registro_saida_origem", None)
        if saida_origem:
            bloquear_saida = True

        data_saida_efetiva = self.instance.data_saida or (saida_origem.data_saida if saida_origem else None)
        horario_saida_efetivo = self.instance.horario_saida or (saida_origem.horario_saida if saida_origem else None)
        odometro_saida_efetivo = self.instance.odometro_saida if self.instance.odometro_saida is not None else (saida_origem.odometro_saida if saida_origem else None)
        condutor_efetivo = self.instance.condutor or (saida_origem.condutor if saida_origem else "")
        destino_efetivo = self.instance.destino or (saida_origem.destino if saida_origem else "")

        if data_saida_efetiva and hasattr(data_saida_efetiva, "strftime"):
            self.initial["data_saida"] = data_saida_efetiva.strftime("%Y-%m-%d")
        if horario_saida_efetivo and hasattr(horario_saida_efetivo, "strftime"):
            self.initial["horario_saida"] = horario_saida_efetivo.strftime("%H:%M")
        if odometro_saida_efetivo is not None:
            self.initial["odometro_saida"] = odometro_saida_efetivo
        if condutor_efetivo and not self.initial.get("condutor"):
            self.initial["condutor"] = condutor_efetivo
        if destino_efetivo and not self.initial.get("destino"):
            self.initial["destino"] = destino_efetivo

        if bloquear_saida:
            campos_saida = ["viatura", "condutor", "destino", "data_saida", "horario_saida", "odometro_saida"]
            for c in campos_saida:
                self.fields[c].disabled = True
                self.fields[c].required = False

        if self.instance.data_chegada and hasattr(self.instance.data_chegada, "strftime"):
            self.initial["data_chegada"] = self.instance.data_chegada.strftime("%Y-%m-%d")
        if self.instance.horario_chegada and hasattr(self.instance.horario_chegada, "strftime"):
            self.initial["horario_chegada"] = self.instance.horario_chegada.strftime("%H:%M")

    def clean(self):
        cleaned_data = super().clean()
        saida_origem = getattr(self.instance, "registro_saida_origem", None)

        data_saida = cleaned_data.get("data_saida") or (saida_origem.data_saida if saida_origem else None)
        horario_saida = cleaned_data.get("horario_saida") or (saida_origem.horario_saida if saida_origem else None)
        odometro_saida = cleaned_data.get("odometro_saida") if cleaned_data.get("odometro_saida") is not None else (saida_origem.odometro_saida if saida_origem else None)

        data_chegada = cleaned_data.get("data_chegada")
        horario_chegada = cleaned_data.get("horario_chegada")
        odometro_chegada = cleaned_data.get("odometro_chegada")
        possui_avarias = cleaned_data.get("possui_avarias")
        avarias = cleaned_data.get("avarias_encontradas")
        status = cleaned_data.get("status")

        # Se informou apenas horário, apenas data, ou apenas odômetro de chegada
        has_chegada = data_chegada or horario_chegada or odometro_chegada is not None
        if has_chegada:
            if not data_chegada:
                self.add_error("data_chegada", "Ao informar o retorno da viatura, informe a data de chegada.")
            if not horario_chegada:
                self.add_error("horario_chegada", "Ao informar o retorno da viatura, informe o horário de chegada.")
            if odometro_chegada is None:
                self.add_error("odometro_chegada", "Ao informar o retorno da viatura, informe também o odômetro de chegada.")

        # Validação do odômetro
        if (
            odometro_saida is not None
            and odometro_chegada is not None
            and odometro_chegada < odometro_saida
        ):
            self.add_error(
                "odometro_chegada",
                f"Odômetro de chegada ({odometro_chegada} km) não pode ser inferior ao de saída ({odometro_saida} km).",
            )

        # Validação de avarias
        if possui_avarias and not avarias:
            self.add_error(
                "avarias_encontradas",
                "Ao marcar que o veículo possui avarias, é obrigatório preencher a descrição das avarias encontradas.",
            )

        # Sincronização de status
        if (
            data_chegada
            and horario_chegada
            and odometro_chegada is not None
            and status == RegistroUso.STATUS_EM_TRANSITO
        ):
            cleaned_data["status"] = RegistroUso.STATUS_CONCLUIDO
        elif (
            not data_chegada
            and not horario_chegada
            and odometro_chegada is None
            and status == RegistroUso.STATUS_CONCLUIDO
        ):
            cleaned_data["status"] = RegistroUso.STATUS_EM_TRANSITO

        return cleaned_data

    def save(self, commit=True):
        reg = super().save(commit=False)
        # Se for um registro de chegada referenciando saída original, preserva nulidade dos campos de saída da ficha atual
        if reg.registro_saida_origem and reg.tipo_movimentacao == RegistroUso.TIPO_CHEGADA:
            reg.data_saida = None
            reg.horario_saida = None
            reg.odometro_saida = None
        if commit:
            reg.save()
        return reg



class RegistroMovimentacaoForm(forms.Form):
    """
    Formulário unificado e inteligente para lançamento de movimentação de viatura.
    Permite registrar tanto a Saída quanto o Retorno em uma única interface amigável.
    """
    TIPO_SAIDA = "SAIDA"
    TIPO_CHEGADA = "CHEGADA"
    TIPO_CHOICES = [
        (TIPO_SAIDA, "Saída de Viatura"),
        (TIPO_CHEGADA, "Retorno / Entrada de Viatura"),
    ]

    viatura = forms.ModelChoiceField(
        label="Viatura da Frota",
        queryset=Viatura.objects.filter(ativo=True).order_by("status", "marca", "modelo"),
        widget=forms.Select(attrs={"class": "pf-select", "id": "id_viatura"}),
        help_text="Selecione da lista ou informe a placa abaixo",
        required=False,
    )
    placa = forms.CharField(
        label="Placa do Veículo",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={"class": "pf-input", "id": "id_placa_input", "placeholder": "Ex: BRA2E19 ou ABC-1234", "autocomplete": "off", "style": "text-transform: uppercase;"}),
        help_text="Digite a placa para preenchimento automático",
    )
    marca = forms.CharField(
        label="Marca",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "pf-input", "id": "id_marca_input", "placeholder": "Ex: Toyota, Chevrolet"}),
    )
    modelo = forms.CharField(
        label="Modelo",
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={"class": "pf-input", "id": "id_modelo_input", "placeholder": "Ex: Hilux 4x4, Trailblazer"}),
    )
    cor = forms.CharField(
        label="Cor",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "pf-input", "id": "id_cor_input", "placeholder": "Ex: Branca, Preta"}),
    )
    tipo_movimentacao = forms.ChoiceField(
        label="Tipo de Movimentação",
        choices=TIPO_CHOICES,
        widget=forms.HiddenInput(attrs={"id": "id_tipo_movimentacao"}),
        required=False,
    )

    # Campos de Saída
    condutor_saida = forms.CharField(
        label="Condutor Responsável (Saída)",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nome completo e matrícula do condutor"}),
    )
    destino = forms.CharField(
        label="Destino / Missão / Operação",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "pf-input", "placeholder": "Destino ou missão operacional..."}),
    )
    data_saida = forms.DateField(
        label="Data de Saída",
        required=False,
        widget=forms.DateInput(attrs={"class": "pf-input", "type": "date"}, format="%Y-%m-%d"),
    )
    horario_saida = forms.TimeField(
        label="Horário de Saída",
        required=False,
        widget=forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
    )
    odometro_saida = forms.IntegerField(
        label="Odômetro de Saída (KM)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "pf-input", "placeholder": "KM no painel do veículo"}),
    )

    # Campos de Retorno
    registro_saida_origem = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(attrs={"id": "id_registro_saida_origem"}),
    )
    condutor_chegada = forms.CharField(
        label="Condutor que Devolveu",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nome e matrícula do condutor que devolveu a viatura"}),
    )
    data_chegada = forms.DateField(
        label="Data de Chegada",
        required=False,
        widget=forms.DateInput(attrs={"class": "pf-input", "type": "date"}, format="%Y-%m-%d"),
    )
    horario_chegada = forms.TimeField(
        label="Horário de Chegada",
        required=False,
        widget=forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
    )
    odometro_chegada = forms.IntegerField(
        label="Odômetro de Retorno (KM)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "pf-input", "placeholder": "KM no painel do veículo"}),
    )
    possui_avarias = forms.BooleanField(
        label="Constatada alguma avaria?",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "pf-checkbox", "id": "id_possui_avarias"}),
    )
    avarias_encontradas = forms.CharField(
        label="Descrição Detalhada das Avarias",
        required=False,
        widget=forms.Textarea(attrs={"class": "pf-textarea", "rows": 3, "placeholder": "Descreva danos, avarias ou falhas mecânicas observadas..."}),
    )

    def __init__(self, *args, **kwargs):
        self.ficha = kwargs.pop("ficha", None)
        super().__init__(*args, **kwargs)
        self.fields["viatura"].required = False

        hoje_str = datetime.now().strftime("%Y-%m-%d")
        hora_str = datetime.now().strftime("%H:%M")

        if not self.initial.get("data_saida"):
            self.initial["data_saida"] = hoje_str
        if not self.initial.get("horario_saida"):
            self.initial["horario_saida"] = hora_str
        if not self.initial.get("data_chegada"):
            self.initial["data_chegada"] = hoje_str
        if not self.initial.get("horario_chegada"):
            self.initial["horario_chegada"] = hora_str

    def clean(self):
        cleaned_data = super().clean()
        viatura = cleaned_data.get("viatura")
        placa = normalizar_placa(cleaned_data.get("placa") or "")

        # Se a viatura não foi selecionada pelo select, resolve via placa informada
        if not viatura and placa:
            if not validar_formato_placa(placa):
                self.add_error("placa", "Formato de placa inválido. Use o padrão Mercosul (ex: BRA2E19) ou antigo (ABC1234).")
                return cleaned_data

            viatura = Viatura.objects.filter(placa=placa).first()
            if not viatura:
                marca = (cleaned_data.get("marca") or "").strip()
                modelo = (cleaned_data.get("modelo") or "").strip()
                cor = (cleaned_data.get("cor") or "").strip()

                if not (marca and modelo):
                    res = consultar_placa(placa)
                    if res.sucesso:
                        marca = res.marca
                        modelo = res.modelo
                        cor = res.cor or cor

                if not (marca and modelo):
                    self.add_error("marca", "Marca e modelo não identificados automaticamente. Preencha os campos para contingência.")
                    return cleaned_data

                viatura = Viatura.objects.create(
                    placa=placa,
                    marca=marca.title(),
                    modelo=modelo,
                    cor=cor or "Preta",
                    classificacao=Viatura.CLASSIFICACAO_PENDENTE,
                    origem_dados=Viatura.ORIGEM_API if marca else Viatura.ORIGEM_MANUAL,
                    status=Viatura.STATUS_DISPONIVEL,
                )

            cleaned_data["viatura"] = viatura

        if not viatura:
            self.add_error("placa", "Informe a placa do veículo ou selecione uma viatura cadastrada.")
            return cleaned_data

        tipo = cleaned_data.get("tipo_movimentacao")
        # Se tipo não foi informado, infere automaticamente pelo status da viatura
        if not tipo:
            tipo = self.TIPO_CHEGADA if viatura.status == Viatura.STATUS_EM_USO else self.TIPO_SAIDA
            cleaned_data["tipo_movimentacao"] = tipo

        if tipo == self.TIPO_SAIDA:
            condutor = cleaned_data.get("condutor_saida")
            destino = cleaned_data.get("destino")
            data_saida = cleaned_data.get("data_saida")
            horario_saida = cleaned_data.get("horario_saida")
            odometro_saida = cleaned_data.get("odometro_saida")

            if viatura.status == Viatura.STATUS_EM_USO:
                self.add_error("viatura", f"A viatura {viatura.placa} já está em trânsito (na rua). Para este veículo, deve ser registrado o Retorno.")

            if not condutor:
                self.add_error("condutor_saida", "Informe o nome e matrícula do condutor.")
            if not destino:
                self.add_error("destino", "Informe o destino ou missão.")
            if not data_saida:
                self.add_error("data_saida", "Informe a data de saída.")
            if not horario_saida:
                self.add_error("horario_saida", "Informe o horário de saída.")
            if odometro_saida is None:
                self.add_error("odometro_saida", "Informe o odômetro de saída.")
            elif viatura.km_atual and odometro_saida < viatura.km_atual:
                self.add_error("odometro_saida", f"O odômetro de saída ({odometro_saida} km) não pode ser inferior à quilometragem atual da viatura ({viatura.km_atual} km).")

        elif tipo == self.TIPO_CHEGADA:
            data_chegada = cleaned_data.get("data_chegada")
            horario_chegada = cleaned_data.get("horario_chegada")
            odometro_chegada = cleaned_data.get("odometro_chegada")
            possui_avarias = cleaned_data.get("possui_avarias")
            avarias = cleaned_data.get("avarias_encontradas")
            condutor = cleaned_data.get("condutor_chegada")

            saida_origem = RegistroUso.objects.filter(
                viatura=viatura,
                status=RegistroUso.STATUS_EM_TRANSITO
            ).order_by("-data_saida", "-horario_saida", "-id").first()

            if not condutor:
                if saida_origem and saida_origem.condutor:
                    cleaned_data["condutor_chegada"] = saida_origem.condutor
                else:
                    self.add_error("condutor_chegada", "Informe o nome e matrícula do condutor que devolveu a viatura.")

            if not data_chegada:
                self.add_error("data_chegada", "Informe a data de chegada.")
            if not horario_chegada:
                self.add_error("horario_chegada", "Informe o horário de chegada.")
            if odometro_chegada is None:
                self.add_error("odometro_chegada", "Informe o odômetro de retorno.")
            else:
                km_min = saida_origem.odometro_saida if (saida_origem and saida_origem.odometro_saida is not None) else viatura.km_atual
                if km_min and odometro_chegada < km_min:
                    self.add_error("odometro_chegada", f"Odômetro de retorno ({odometro_chegada} km) não pode ser inferior ao odômetro de saída ({km_min} km).")

            if possui_avarias and not avarias:
                self.add_error("avarias_encontradas", "Ao constatar avarias, descreva os danos encontrados.")

        return cleaned_data

    def save(self, ficha, usuario):
        cleaned_data = self.cleaned_data
        viatura = cleaned_data["viatura"]
        tipo = cleaned_data["tipo_movimentacao"]

        if tipo == self.TIPO_SAIDA:
            reg = RegistroUso.objects.create(
                ficha=ficha,
                viatura=viatura,
                condutor=cleaned_data["condutor_saida"],
                destino=cleaned_data["destino"],
                data_saida=cleaned_data["data_saida"],
                horario_saida=cleaned_data["horario_saida"],
                odometro_saida=cleaned_data["odometro_saida"],
                tipo_movimentacao=RegistroUso.TIPO_SAIDA,
                status=RegistroUso.STATUS_EM_TRANSITO,
                registrado_por=usuario,
            )
            viatura.status = Viatura.STATUS_EM_USO
            viatura.save(update_fields=["status"])
            return reg, "SAIDA"

        elif tipo == self.TIPO_CHEGADA:
            saida_origem = RegistroUso.objects.filter(
                viatura=viatura,
                status=RegistroUso.STATUS_EM_TRANSITO
            ).order_by("-data_saida", "-horario_saida", "-id").first()

            odometro_chegada = cleaned_data["odometro_chegada"]

            # Caso a saída tenha sido lançada NESTA MESMA FICHA e ainda esteja em trânsito
            if saida_origem and saida_origem.ficha_id == ficha.pk:
                saida_origem.data_chegada = cleaned_data["data_chegada"]
                saida_origem.horario_chegada = cleaned_data["horario_chegada"]
                saida_origem.odometro_chegada = odometro_chegada
                saida_origem.possui_avarias = cleaned_data["possui_avarias"]
                saida_origem.avarias_encontradas = cleaned_data.get("avarias_encontradas", "")
                saida_origem.status = RegistroUso.STATUS_CONCLUIDO
                saida_origem.tipo_movimentacao = RegistroUso.TIPO_COMPLETO
                saida_origem.save()

                viatura.km_atual = odometro_chegada
                viatura.status = Viatura.STATUS_DISPONIVEL
                viatura.save(update_fields=["km_atual", "status"])
                return saida_origem, "CHEGADA"
            else:
                # Saída ocorreu em outra ficha: cria registro de chegada avulsa nesta ficha
                reg = RegistroUso.objects.create(
                    ficha=ficha,
                    viatura=viatura,
                    registro_saida_origem=saida_origem,
                    condutor=cleaned_data.get("condutor_chegada") or (saida_origem.condutor if saida_origem else "Servidor"),
                    destino=saida_origem.destino if saida_origem else "Retorno",
                    data_chegada=cleaned_data["data_chegada"],
                    horario_chegada=cleaned_data["horario_chegada"],
                    odometro_chegada=odometro_chegada,
                    possui_avarias=cleaned_data["possui_avarias"],
                    avarias_encontradas=cleaned_data.get("avarias_encontradas", ""),
                    tipo_movimentacao=RegistroUso.TIPO_CHEGADA,
                    status=RegistroUso.STATUS_CONCLUIDO,
                    registrado_por=usuario,
                )
                if saida_origem:
                    saida_origem.status = RegistroUso.STATUS_CONCLUIDO
                    saida_origem.save(update_fields=["status"])

                viatura.km_atual = odometro_chegada
                viatura.status = Viatura.STATUS_DISPONIVEL
                viatura.save(update_fields=["km_atual", "status"])
                return reg, "CHEGADA"


