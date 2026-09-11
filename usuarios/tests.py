from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from usuarios.forms import UsuarioForm

Usuario = get_user_model()


class UsuariosAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "agente.teste"
        self.password = "SenhaForte@PF2026"
        self.user = Usuario.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="Agente",
            last_name="Federal",
            matricula="PF12345",
            perfil=Usuario.PERFIL_VIGILANTE,
        )

    def test_login_sucesso(self):
        url = reverse("usuarios:login")
        response = self.client.post(
            url,
            {"username": self.username, "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_login_credenciais_incorretas(self):
        url = reverse("usuarios:login")
        response = self.client.post(
            url,
            {"username": self.username, "password": "senha_errada"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuário ou senha incorretos")

    def test_prevencao_open_redirect(self):
        """Garante que tentativa de redirecionamento externo malicioso é neutralizada."""
        url = f"{reverse('usuarios:login')}?next=https://site-malicioso-externo.com/phishing"
        response = self.client.post(
            url,
            {"username": self.username, "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        # Deve redirecionar para a home segura, não para o site externo
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("usuarios:logout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("usuarios:login"))

    def test_usuario_form_validacao_senha_obrigatoria_novo_usuario(self):
        """Novo usuário requer senha provisória."""
        form = UsuarioForm(
            data={
                "username": "novo.agente",
                "first_name": "Novo",
                "last_name": "Agente",
                "matricula": "PF99999",
                "cargo": "Agente",
                "setor": "DREX",
                "perfil": Usuario.PERFIL_VIGILANTE,
                "is_active": True,
                "password": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_usuario_form_validacao_senha_muito_curta(self):
        """Senha que viola validadores padrão do Django deve falhar."""
        form = UsuarioForm(
            data={
                "username": "novo.agente",
                "first_name": "Novo",
                "last_name": "Agente",
                "matricula": "PF99999",
                "cargo": "Agente",
                "setor": "DREX",
                "perfil": Usuario.PERFIL_VIGILANTE,
                "is_active": True,
                "password": "123",  # Muito curta (menos de 8 caracteres)
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
