from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from .models import Usuario


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário / Matrícula",
        widget=forms.TextInput(attrs={
            "class": "pf-input",
            "placeholder": "Digite seu usuário ou matrícula",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Senha de Acesso",
        widget=forms.PasswordInput(attrs={
            "class": "pf-input",
            "placeholder": "Digite sua senha",
        }),
    )


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha Provisória",
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "pf-input",
            "placeholder": "Obrigatória apenas para novos usuários",
        }),
        help_text="Mínimo de 6 caracteres",
    )

    # Campo para atribuição de perfis ao salvar o usuário
    # Lazy import para evitar dependência circular durante migrações
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from accesscontrol.models import Perfil

            self.fields["perfis"] = forms.ModelMultipleChoiceField(
                label="Perfis de Acesso",
                queryset=Perfil.objects.filter(ativo=True).order_by("nome"),
                required=True,
                widget=forms.CheckboxSelectMultiple(attrs={"class": "pf-checkbox-group"}),
                help_text="Selecione um ou mais perfis para o usuário.",
            )
            # Preenche os perfis atuais se for edição
            if self.instance.pk:
                self.fields["perfis"].initial = Perfil.objects.filter(
                    usuarioperfil__usuario=self.instance,
                    usuarioperfil__ativo=True,
                )
        except Exception:
            # Ignora erros durante migrações quando a tabela ainda não existe
            pass

    class Meta:
        model = Usuario
        fields = [
            "username", "first_name", "last_name", "email",
            "matricula", "cargo", "setor", "telefone", "is_active",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "pf-input", "placeholder": "login.funcional"}),
            "first_name": forms.TextInput(attrs={"class": "pf-input"}),
            "last_name": forms.TextInput(attrs={"class": "pf-input"}),
            "email": forms.EmailInput(attrs={"class": "pf-input", "placeholder": "nome.sobrenome@pf.gov.br"}),
            "matricula": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: 19.824-X"}),
            "cargo": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: Agente de Polícia Federal, Vigilante"}),
            "setor": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: NUTRAN, DREX, Portaria"}),
            "telefone": forms.TextInput(attrs={"class": "pf-input", "placeholder": "Ex: (61) 2024-8000"}),
            "is_active": forms.CheckboxInput(attrs={"class": "pf-checkbox"}),
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.instance.pk and not password:
            msg = "É obrigatório informar uma senha provisória para novos usuários."
            raise forms.ValidationError(msg)
        if password:
            validate_password(password, user=self.instance)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self._salvar_perfis(user)
        return user

    def _salvar_perfis(self, user):
        """Atualiza os vínculos de UsuarioPerfil após salvar o usuário."""
        try:
            from accesscontrol.models import Perfil, UsuarioPerfil

            perfis_selecionados = self.cleaned_data.get("perfis", Perfil.objects.none())

            # Desativa perfis que foram desmarcados
            UsuarioPerfil.objects.filter(usuario=user).exclude(
                perfil__in=perfis_selecionados
            ).update(ativo=False)

            # Ativa ou cria vínculos para os perfis selecionados
            for perfil in perfis_selecionados:
                UsuarioPerfil.objects.update_or_create(
                    usuario=user,
                    perfil=perfil,
                    defaults={"ativo": True},
                )
        except Exception:
            pass
