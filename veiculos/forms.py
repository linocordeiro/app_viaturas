from django import forms
from .models import Viatura, Manutencao, Setor


class ViaturaForm(forms.ModelForm):
    class Meta:
        model = Viatura
        fields = [
            'placa', 'marca', 'modelo', 'ano_fabricacao', 'ano_modelo',
            'cor', 'tipo', 'chassi', 'status', 'setor_pertencente',
            'responsavel_tipo', 'responsavel_setor', 'responsavel_pessoa',
            'km_atual', 'proxima_manutencao_km', 'proxima_manutencao_data',
            'observacoes', 'ativo'
        ]
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: BRA2E19 ou ABC-1234', 'style': 'text-transform: uppercase;'}),
            'marca': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: Toyota, Chevrolet, Ford'}),
            'modelo': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: Hilux 4x4, Trailblazer'}),
            'ano_fabricacao': forms.NumberInput(attrs={'class': 'pf-input'}),
            'ano_modelo': forms.NumberInput(attrs={'class': 'pf-input'}),
            'cor': forms.TextInput(attrs={'class': 'pf-input'}),
            'tipo': forms.Select(attrs={'class': 'pf-select'}),
            'chassi': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Número do Chassi'}),
            'status': forms.Select(attrs={'class': 'pf-select'}),
            'setor_pertencente': forms.Select(attrs={'class': 'pf-select'}),
            'responsavel_tipo': forms.Select(attrs={'class': 'pf-select'}),
            'responsavel_setor': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Setor ou divisão responsável'}),
            'responsavel_pessoa': forms.Select(attrs={'class': 'pf-select'}),
            'km_atual': forms.NumberInput(attrs={'class': 'pf-input'}),
            'proxima_manutencao_km': forms.NumberInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: 50000'}),
            'proxima_manutencao_data': forms.DateInput(attrs={'class': 'pf-input', 'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'class': 'pf-textarea', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'pf-checkbox'}),
        }

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '').strip().upper()
        return placa


class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = [
            'tipo', 'data_manutencao', 'km_no_momento', 'fornecedor_oficina',
            'numero_ordem_servico', 'descricao_servico', 'pecas_substituidas',
            'valor_total', 'proxima_revisao_km', 'proxima_revisao_data'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'pf-select'}),
            'data_manutencao': forms.DateInput(attrs={'class': 'pf-input', 'type': 'date'}),
            'km_no_momento': forms.NumberInput(attrs={'class': 'pf-input'}),
            'fornecedor_oficina': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Oficina / Concessionária'}),
            'numero_ordem_servico': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Nº da OS ou NF'}),
            'descricao_servico': forms.Textarea(attrs={'class': 'pf-textarea', 'rows': 3, 'placeholder': 'Serviços executados...'}),
            'pecas_substituidas': forms.Textarea(attrs={'class': 'pf-textarea', 'rows': 2, 'placeholder': 'Pastilhas, óleo, filtros...'}),
            'valor_total': forms.NumberInput(attrs={'class': 'pf-input', 'step': '0.01'}),
            'proxima_revisao_km': forms.NumberInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: 60000'}),
            'proxima_revisao_data': forms.DateInput(attrs={'class': 'pf-input', 'type': 'date'}),
        }
