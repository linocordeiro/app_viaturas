from datetime import datetime

from django import forms

from veiculos.models import Viatura

from .models import FichaControle, RegistroUso


class FichaControleForm(forms.ModelForm):
    class Meta:
        model = FichaControle
        fields = ["data_expediente", "horario_inicio", "horario_termino", "nome_vigilante", "observacoes"]
        widgets = {
            "data_expediente": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "horario_inicio": forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
            "horario_termino": forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
            "nome_vigilante": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nome completo do vigilante do dia"}),
            "observacoes": forms.Textarea(attrs={"class": "pf-textarea", "rows": 2, "placeholder": "Observações do plantão / expediente..."}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_exp = cleaned_data.get("data_expediente")
        h_inicio = cleaned_data.get("horario_inicio")

        if data_exp and h_inicio:
            # Verifica se já existe ficha para a mesma data e mesmo turno/horário de início
            qs = FichaControle.objects.filter(data_expediente=data_exp, horario_inicio=h_inicio)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                msg = (
                    f"Já existe uma Ficha de Controle cadastrada para a data "
                    f"{data_exp.strftime('%d/%m/%Y')} no horário de {h_inicio.strftime('%H:%M')}."
                )
                self.add_error("horario_inicio", msg)
        return cleaned_data


class RegistroSaidaForm(forms.ModelForm):
    class Meta:
        model = RegistroUso
        fields = ["viatura", "condutor", "destino", "data_saida", "horario_saida", "odometro_saida"]
        widgets = {
            "viatura": forms.Select(attrs={"class": "pf-select"}),
            "condutor": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nome e matrícula do condutor"}),
            "destino": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Destino / Missão / Operação"}),
            "data_saida": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "horario_saida": forms.TimeInput(attrs={"class": "pf-input", "type": "time"}),
            "odometro_saida": forms.NumberInput(attrs={"class": "pf-input", "placeholder": "KM de saída"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permite selecionar apenas viaturas ativas e disponíveis (ou a viatura já associada se for edição)
        if self.instance.pk:
            self.fields["viatura"].queryset = Viatura.objects.filter(ativo=True)
        else:
            self.fields["viatura"].queryset = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_DISPONIVEL)
            # Define hora atual padrão
            self.initial["data_saida"] = datetime.now().strftime("%Y-%m-%d")
            self.initial["horario_saida"] = datetime.now().strftime("%H:%M")


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

        if bloquear_saida:
            campos_saida = ["viatura", "condutor", "destino", "data_saida", "horario_saida", "odometro_saida"]
            for c in campos_saida:
                self.fields[c].disabled = True

        if self.instance.data_saida and hasattr(self.instance.data_saida, "strftime"):
            self.initial["data_saida"] = self.instance.data_saida.strftime("%Y-%m-%d")
        if self.instance.horario_saida and hasattr(self.instance.horario_saida, "strftime"):
            self.initial["horario_saida"] = self.instance.horario_saida.strftime("%H:%M")
        
        if self.instance.data_chegada and hasattr(self.instance.data_chegada, "strftime"):
            self.initial["data_chegada"] = self.instance.data_chegada.strftime("%Y-%m-%d")
        if self.instance.horario_chegada and hasattr(self.instance.horario_chegada, "strftime"):
            self.initial["horario_chegada"] = self.instance.horario_chegada.strftime("%H:%M")

    def clean(self):
        cleaned_data = super().clean()
        data_saida = cleaned_data.get("data_saida")
        odometro_saida = cleaned_data.get("odometro_saida")
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

