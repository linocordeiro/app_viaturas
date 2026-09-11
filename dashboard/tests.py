from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from fichas.models import FichaControle, RegistroUso
from veiculos.models import Setor, Viatura

Usuario = get_user_model()


class DashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "operador.dashboard"
        self.password = "SenhaForte@PF2026"
        self.user = Usuario.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="Operador",
            last_name="Frota",
            matricula="PF77777",
            perfil=Usuario.PERFIL_RESPONSAVEL,
        )
        self.setor = Setor.objects.create(sigla="DREX", nome="Delegacia Regional Executiva")

        # Viaturas de teste com status variados
        self.v1 = Viatura.objects.create(
            placa="PF-1111",
            marca="Toyota",
            modelo="Hilux",
            setor_pertencente=self.setor,
            km_atual=10000,
            status=Viatura.STATUS_DISPONIVEL,
            ativo=True,
        )
        self.v2 = Viatura.objects.create(
            placa="PF-2222",
            marca="Toyota",
            modelo="Corolla",
            setor_pertencente=self.setor,
            km_atual=20000,
            status=Viatura.STATUS_EM_USO,
            ativo=True,
        )
        self.v3 = Viatura.objects.create(
            placa="PF-3333",
            marca="Chevrolet",
            modelo="Trailblazer",
            setor_pertencente=self.setor,
            km_atual=30000,
            status=Viatura.STATUS_MANUTENCAO,
            ativo=True,
        )

    def test_dashboard_requer_login(self):
        url = reverse("dashboard:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)

    def test_dashboard_usuario_autenticado(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("dashboard:home")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/index.html")

        # Verifica consistência das métricas calculadas na agregação
        self.assertEqual(response.context["total_viaturas"], 3)
        self.assertEqual(response.context["disponiveis"], 1)
        self.assertEqual(response.context["em_uso"], 1)
        self.assertEqual(response.context["manutencao"], 1)
        self.assertEqual(response.context["indisponiveis"], 0)

        # Gráficos dos 7 dias
        self.assertEqual(len(response.context["dias_grafico"]), 7)
        self.assertEqual(len(response.context["km_grafico"]), 7)

    def test_dashboard_km_grafico_com_dados(self):
        """Verifica que a agregação dos 7 dias soma corretamente os km rodados."""
        hoje = date.today()
        ficha = FichaControle.objects.create(
            data_expediente=hoje,
            horario_inicio=time(8, 0),
            horario_termino=time(18, 0),
            vigilante=self.user,
            nome_vigilante="Operador Frota",
        )
        RegistroUso.objects.create(
            ficha=ficha,
            viatura=self.v1,
            condutor="Agente Silva (PF11111)",
            destino="Operação Policial",
            horario_saida=time(9, 0),
            odometro_saida=10000,
            horario_chegada=time(12, 0),
            odometro_chegada=10150,  # 150 km
            status=RegistroUso.STATUS_CONCLUIDO,
        )


        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        # O último elemento do gráfico (hoje) deve refletir os 150 km
        self.assertEqual(response.context["km_grafico"][-1], 150)
