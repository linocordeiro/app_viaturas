from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuário / Matrícula',
        widget=forms.TextInput(attrs={
            'class': 'pf-input',
            'placeholder': 'Digite seu usuário ou matrícula',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Senha de Acesso',
        widget=forms.PasswordInput(attrs={
            'class': 'pf-input',
            'placeholder': 'Digite sua senha'
        })
    )


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha Provisória',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'pf-input',
            'placeholder': 'Obrigatória apenas para novos usuários'
        }),
        help_text='Mínimo de 6 caracteres'
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'matricula', 'cargo', 'setor', 'telefone', 'perfil', 'is_active'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'login.funcional'}),
            'first_name': forms.TextInput(attrs={'class': 'pf-input'}),
            'last_name': forms.TextInput(attrs={'class': 'pf-input'}),
            'email': forms.EmailInput(attrs={'class': 'pf-input', 'placeholder': 'nome.sobrenome@pf.gov.br'}),
            'matricula': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: 19.824-X'}),
            'cargo': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: Agente de Polícia Federal, Vigilante'}),
            'setor': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: NUTRAN, DREX, Portaria'}),
            'telefone': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: (61) 2024-8000'}),
            'perfil': forms.Select(attrs={'class': 'pf-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'pf-checkbox'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.instance.pk and not password:
            raise forms.ValidationError('É obrigatório informar uma senha provisória para novos usuários.')
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
