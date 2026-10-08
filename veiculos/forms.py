from django import forms

from .models import Manutencao, Viatura


class ViaturaForm(forms.ModelForm):
    class Meta:
        model = Viatura
        fields = [
            "placa", "marca", "modelo", "ano_fabricacao", "ano_modelo",
            "cor", "tipo", "chassi", "status", "setor_pertencente",
            "responsavel_tipo", "responsavel_setor", "responsavel_pessoa",
            "km_atual", "proxima_manutencao_km", "proxima_manutencao_data",
            "observacoes", "ativo"
        ]
        widgets = {
            "placa": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: BRA2E19 ou ABC-1234", "style": "text-transform: uppercase;"}),
            "marca": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: Toyota, Chevrolet, Ford"}),
            "modelo": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: Hilux 4x4, Trailblazer"}),
            "ano_fabricacao": forms.NumberInput(attrs={"class": "pf-input"}),
            "ano_modelo": forms.NumberInput(attrs={"class": "pf-input"}),
            "cor": forms.TextInput(attrs={"class": "pf-input"}),
            "tipo": forms.Select(attrs={"class": "pf-select"}),
            "chassi": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Número do Chassi"}),
            "status": forms.Select(attrs={"class": "pf-select"}),
            "setor_pertencente": forms.Select(attrs={"class": "pf-select"}),
            "responsavel_tipo": forms.Select(attrs={"class": "pf-select"}),
            "responsavel_setor": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Setor ou divisão responsável"}),
            "responsavel_pessoa": forms.Select(attrs={"class": "pf-select"}),
            "km_atual": forms.NumberInput(attrs={"class": "pf-input"}),
            "proxima_manutencao_km": forms.NumberInput(attrs={"class": "pf-input", "placeholder": "Ex: 50000"}),
            "proxima_manutencao_data": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "observacoes": forms.Textarea(attrs={"class": "pf-textarea", "rows": 3}),
            "ativo": forms.CheckboxInput(attrs={"class": "pf-checkbox"}),
        }

    def clean_placa(self):
        return self.cleaned_data.get("placa", "").strip().upper()



class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = [
            "tipo", "data_manutencao", "km_no_momento", "fornecedor_oficina",
            "numero_ordem_servico", "descricao_servico", "pecas_substituidas",
            "valor_total", "proxima_revisao_km", "proxima_revisao_data"
        ]
        widgets = {
            "tipo": forms.Select(attrs={"class": "pf-select"}),
            "data_manutencao": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
            "km_no_momento": forms.NumberInput(attrs={"class": "pf-input"}),
            "fornecedor_oficina": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Oficina / Concessionária"}),
            "numero_ordem_servico": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nº da OS ou NF"}),
            "descricao_servico": forms.Textarea(attrs={"class": "pf-textarea", "rows": 3, "placeholder": "Serviços executados..."}),
            "pecas_substituidas": forms.Textarea(attrs={"class": "pf-textarea", "rows": 2, "placeholder": "Pastilhas, óleo, filtros..."}),
            "valor_total": forms.NumberInput(attrs={"class": "pf-input", "step": "0.01"}),
            "proxima_revisao_km": forms.NumberInput(attrs={"class": "pf-input", "placeholder": "Ex: 60000"}),
            "proxima_revisao_data": forms.DateInput(attrs={"class": "pf-input", "type": "date"}),
        }


class ClassificacaoViaturaForm(forms.ModelForm):
    """
    Formulário para o usuário com perfil NUTRAN classificar os veículos identificados
    a partir dos registros de entrada e saída (definir se é frota ou veículo externo,
    atribuir o setor de lotação e os dados do servidor responsável - nome e cargo).
    """
    class Meta:
        model = Viatura
        fields = [
            "classificacao",
            "setor_pertencente",
            "responsavel_nome",
            "responsavel_cargo",
            "tipo",
            "cor",
            "ano_fabricacao",
            "ano_modelo",
            "chassi",
            "observacoes",
        ]
        widgets = {
            "classificacao": forms.Select(attrs={"class": "pf-select", "id": "id_classificacao"}),
            "setor_pertencente": forms.Select(attrs={"class": "pf-select", "id": "id_setor_pertencente"}),
            "responsavel_nome": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Nome completo do servidor responsável"}),
            "responsavel_cargo": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: Agente de Polícia Federal, Perito, Escrivão, Chefe de Setor"}),
            "tipo": forms.Select(attrs={"class": "pf-select"}),
            "cor": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Cor predominante"}),
            "ano_fabricacao": forms.NumberInput(attrs={"class": "pf-input"}),
            "ano_modelo": forms.NumberInput(attrs={"class": "pf-input"}),
            "chassi": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Número do chassi (opcional)"}),
            "observacoes": forms.Textarea(attrs={"class": "pf-textarea", "rows": 3, "placeholder": "Observações sobre a viatura ou órgão de origem (se externo)"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        classificacao = cleaned_data.get("classificacao")
        setor = cleaned_data.get("setor_pertencente")
        resp_nome = cleaned_data.get("responsavel_nome")

        if classificacao == Viatura.CLASSIFICACAO_FROTA:
            if not setor:
                self.add_error("setor_pertencente", "Para viaturas da frota da unidade, a definição do Setor de Lotação é obrigatória.")
            if not resp_nome:
                self.add_error("responsavel_nome", "Para viaturas da frota da unidade, informe o nome do servidor responsável.")

        return cleaned_data


class ConfiguracaoConsultaPlacaForm(forms.ModelForm):
    """
    Formulário administrativo para configuração da integração de consulta de placas,
    alternando graficamente entre o Provedor Gratuito e a API SERPRO / SENATRAN,
    além de definir o proxy institucional corporativo.
    """
    class Meta:
        from .models import ConfiguracaoConsultaPlaca
        model = ConfiguracaoConsultaPlaca
        fields = [
            "consulta_habilitada",
            "provedor_ativo",
            "proxy_url",
            "timeout_segundos",
            "cache_dias",
            "gratuito_url",
            "gratuito_token",
            "gratuito_cabecalho",
            "gratuito_prefixo",
            "serpro_url_token",
            "serpro_url_consulta",
            "serpro_consumer_key",
            "serpro_consumer_secret",
        ]
        widgets = {
            "consulta_habilitada": forms.CheckboxInput(attrs={"class": "pf-checkbox"}),
            "provedor_ativo": forms.Select(attrs={"class": "pf-select", "id": "id_provedor_ativo"}),
            "proxy_url": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: http://proxy.pf.gov.br:8080 (vazio usa HTTPS_PROXY do servidor)"}),
            "timeout_segundos": forms.NumberInput(attrs={"class": "pf-input", "min": 1, "max": 30}),
            "cache_dias": forms.NumberInput(attrs={"class": "pf-input", "min": 1, "max": 365}),
            "gratuito_url": forms.TextInput(attrs={"class": "pf-input", "placeholder": "https://api.exemplo.com.br/veiculo/{placa}"}),
            "gratuito_token": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Token ou chave de API (opcional)"}),
            "gratuito_cabecalho": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Authorization"}),
            "gratuito_prefixo": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Bearer "}),
            "serpro_url_token": forms.TextInput(attrs={"class": "pf-input", "placeholder": "https://gateway.apiserpro.serpro.gov.br/token"}),
            "serpro_url_consulta": forms.TextInput(attrs={"class": "pf-input", "placeholder": "https://gateway.apiserpro.serpro.gov.br/consulta-veiculo/v1/veiculo/{placa}"}),
            "serpro_consumer_key": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Consumer Key fornecida pelo SERPRO"}),
            "serpro_consumer_secret": forms.PasswordInput(render_value=True, attrs={"class": "pf-input", "placeholder": "Consumer Secret fornecido pelo SERPRO"}),
        }

