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

    def test_usuario_form_senha_padrao_mudar123(self):
        """Novo usuário cadastrado sem preencher senha recebe a senha padrão mudar@123."""
        from accesscontrol.models import Perfil
        perfil, _ = Perfil.objects.get_or_create(nome="Vigilante", defaults={"ativo": True})
        form = UsuarioForm(
            data={
                "username": "novo.vigilante",
                "first_name": "Novo",
                "last_name": "Vigilante",
                "matricula": "PF99999",
                "cargo": "Vigilante",
                "setor": "Portaria",
                "perfis": [perfil.pk],
                "is_active": True,
                "password": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        novo_user = form.save()
        self.assertTrue(novo_user.check_password("mudar@123"))

    def test_usuario_form_validacao_senha_muito_curta(self):
        """Senha informada menor que 6 caracteres deve falhar na validação."""
        from accesscontrol.models import Perfil
        perfil, _ = Perfil.objects.get_or_create(nome="Vigilante", defaults={"ativo": True})
        form = UsuarioForm(
            data={
                "username": "novo.agente",
                "first_name": "Novo",
                "last_name": "Agente",
                "matricula": "PF99999",
                "cargo": "Agente",
                "setor": "DREX",
                "perfis": [perfil.pk],
                "is_active": True,
                "password": "123",  # Menos de 6 caracteres
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_usuario_resetar_senha(self):
        """Garante que a ação de resetar senha define a senha do usuário para mudar@123."""
        self.user.is_superuser = True
        self.user.save()

        outro_usuario = Usuario.objects.create_user(
            username="usuario.alvo",
            password="SenhaAntiga@123",
            first_name="Alvo",
            last_name="Reset",
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("usuarios:resetar_senha", kwargs={"pk": outro_usuario.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        outro_usuario.refresh_from_db()
        self.assertTrue(outro_usuario.check_password("mudar@123"))

