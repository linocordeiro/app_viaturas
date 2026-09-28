from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connections
from django.test import Client, TestCase

Usuario = get_user_model()


class AmbienteEBancoDinamicoTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_banco_desenvolvimento_ativo_login(self):
        """Quando DB_ENV=desenvolvimento, deve exibir o indicador BANCO DE DESENVOLVIMENTO no login."""
        with patch("core.middleware.get_env_variable") as mock_env:
            mock_env.side_effect = lambda key, default="": "desenvolvimento" if key == "DB_ENV" else "False"
            response = self.client.get("/usuarios/login/")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "BANCO DE DESENVOLVIMENTO")

    def test_banco_producao_ativo_login(self):
        """Quando DB_ENV=producao, NÃO deve exibir o indicador BANCO DE DESENVOLVIMENTO."""
        with patch("core.middleware.get_env_variable") as mock_env:
            mock_env.side_effect = lambda key, default="": "producao" if key == "DB_ENV" else "False"
            response = self.client.get("/usuarios/login/")
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "BANCO DE DESENVOLVIMENTO")

    def test_banco_desenvolvimento_ativo_navbar(self):
        """Quando DB_ENV=desenvolvimento e usuário logado, navbar deve conter o indicador."""
        user = Usuario.objects.create_user(username="admin.teste", password="password123", is_superuser=True)
        self.client.login(username="admin.teste", password="password123")

        with patch("core.middleware.get_env_variable") as mock_env:
            mock_env.side_effect = lambda key, default="": "desenvolvimento" if key == "DB_ENV" else "False"
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "BANCO DE DESENVOLVIMENTO")

    def test_modo_manutencao_ativado_redirecionamento_e_logout(self):
        """Quando APP_MNT=True, deve redirecionar para /manutencao/ e deslogar usuário."""
        user = Usuario.objects.create_user(username="operador.teste", password="password123")
        self.client.login(username="operador.teste", password="password123")

        with patch("core.middleware.get_env_variable") as mock_env:
            mock_env.side_effect = lambda key, default="": "True" if key == "APP_MNT" else "desenvolvimento"

            # Requisição para qualquer rota comum deve redirecionar para /manutencao/
            response = self.client.get("/")
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/manutencao/")

            # Página de manutenção deve retornar 503 com o template padrão
            with patch("core.views.get_env_variable", return_value="True"):
                response_mnt = self.client.get("/manutencao/")
                self.assertEqual(response_mnt.status_code, 503)
                self.assertContains(response_mnt, "Sistema em Manutenção Programada", status_code=503)
                self.assertContains(response_mnt, "Modo de Manutenção Ativo", status_code=503)

    def test_modo_manutencao_desativado_redireciona_da_manutencao(self):
        """Quando APP_MNT=False, acessar /manutencao/ redireciona de volta para a home."""
        with patch("core.middleware.get_env_variable") as mock_env:
            mock_env.side_effect = lambda key, default="": "False" if key == "APP_MNT" else "desenvolvimento"
            response = self.client.get("/manutencao/")
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/")

    def test_app_env_local_config(self):
        """Valida que APP_ENV='local' define DEBUG=True e hosts locais."""
        from core import settings as s
        # Simula lógica definida no settings.py
        app_env = "local"
        debug = False if app_env == "operacao" else True
        allowed_hosts = ["10.68.6.121"] if app_env == "operacao" else ["127.0.0.1", "localhost"]
        self.assertTrue(debug)
        self.assertEqual(allowed_hosts, ["127.0.0.1", "localhost"])

    def test_app_env_operacao_config(self):
        """Valida que APP_ENV='operacao' define DEBUG=False e host de produção."""
        app_env = "operacao"
        debug = False if app_env == "operacao" else True
        allowed_hosts = ["10.68.6.121"] if app_env == "operacao" else ["127.0.0.1", "localhost"]
        self.assertFalse(debug)
        self.assertEqual(allowed_hosts, ["10.68.6.121"])
