from datetime import date, time, datetime
from django import forms
from .models import FichaControle, RegistroUso
from veiculos.models import Viatura


class FichaControleForm(forms.ModelForm):
    class Meta:
        model = FichaControle
        fields = ['data_expediente', 'horario_inicio', 'horario_termino', 'nome_vigilante', 'observacoes']
        widgets = {
            'data_expediente': forms.DateInput(attrs={'class': 'pf-input', 'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'class': 'pf-input', 'type': 'time'}),
            'horario_termino': forms.TimeInput(attrs={'class': 'pf-input', 'type': 'time'}),
            'nome_vigilante': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Nome completo do vigilante do dia'}),
            'observacoes': forms.Textarea(attrs={'class': 'pf-textarea', 'rows': 2, 'placeholder': 'Observações do plantão / expediente...'}),
        }

    def clean_data_expediente(self):
        data_exp = self.cleaned_data.get('data_expediente')
        # Verifica se já existe outra ficha para este dia
        qs = FichaControle.objects.filter(data_expediente=data_exp)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'Já existe uma Ficha de Controle cadastrada para a data {data_exp.strftime("%d/%m/%Y")}. Não é permitido duplicar fichas no mesmo dia.')
        return data_exp


class RegistroSaidaForm(forms.ModelForm):
    class Meta:
        model = RegistroUso
        fields = ['viatura', 'condutor', 'destino', 'horario_saida', 'odometro_saida']
        widgets = {
            'viatura': forms.Select(attrs={'class': 'pf-select'}),
            'condutor': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Nome e matrícula do condutor'}),
            'destino': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Destino / Missão / Operação'}),
            'horario_saida': forms.TimeInput(attrs={'class': 'pf-input', 'type': 'time'}),
            'odometro_saida': forms.NumberInput(attrs={'class': 'pf-input', 'placeholder': 'KM de saída'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permite selecionar apenas viaturas ativas e disponíveis (ou a viatura já associada se for edição)
        if self.instance.pk:
            self.fields['viatura'].queryset = Viatura.objects.filter(ativo=True)
        else:
            self.fields['viatura'].queryset = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_DISPONIVEL)
            # Define hora atual padrão
            self.initial['horario_saida'] = datetime.now().strftime('%H:%M')


class RegistroChegadaForm(forms.ModelForm):
    class Meta:
        model = RegistroUso
        fields = ['horario_chegada', 'odometro_chegada', 'possui_avarias', 'avarias_encontradas']
        widgets = {
            'horario_chegada': forms.TimeInput(attrs={'class': 'pf-input', 'type': 'time'}),
            'odometro_chegada': forms.NumberInput(attrs={'class': 'pf-input', 'placeholder': 'KM de retorno'}),
            'possui_avarias': forms.CheckboxInput(attrs={'class': 'pf-checkbox'}),
            'avarias_encontradas': forms.Textarea(attrs={'class': 'pf-textarea', 'rows': 3, 'placeholder': 'Descreva detalhadamente arranhões, amassados, itens faltantes ou falhas mecânicas...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.horario_chegada:
            self.initial['horario_chegada'] = datetime.now().strftime('%H:%M')
        if not self.instance.odometro_chegada and self.instance.odometro_saida:
            self.initial['odometro_chegada'] = self.instance.odometro_saida

    def clean(self):
        cleaned_data = super().clean()
        horario_chegada = cleaned_data.get('horario_chegada')
        odometro_chegada = cleaned_data.get('odometro_chegada')
        possui_avarias = cleaned_data.get('possui_avarias')
        avarias = cleaned_data.get('avarias_encontradas')

        if not horario_chegada:
            self.add_error('horario_chegada', 'Informe o horário de retorno da viatura.')
        if odometro_chegada is None:
            self.add_error('odometro_chegada', 'Informe o odômetro de retorno da viatura.')
        elif self.instance.odometro_saida and odometro_chegada < self.instance.odometro_saida:
            self.add_error('odometro_chegada', f"Odômetro de chegada ({odometro_chegada} km) não pode ser inferior ao de saída ({self.instance.odometro_saida} km).")

        if possui_avarias and not avarias:
            self.add_error('avarias_encontradas', 'Ao marcar que o veículo possui avarias, é obrigatório preencher o espaço para anotar as avarias encontradas.')

        return cleaned_data
