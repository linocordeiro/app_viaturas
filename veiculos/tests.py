from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from veiculos.models import Setor, Viatura, Manutencao
from services.relatorios_pdf import gerar_pdf_viaturas, gerar_pdf_manutencoes_viatura
from services.relatorios_excel import gerar_excel_viaturas, gerar_excel_manutencoes

Usuario = get_user_model()


class VeiculosModelTestCase(TestCase):
    def setUp(self):
        self.setor = Setor.objects.create(
            sigla='DREX',
            nome='Delegacia Regional Executiva',
            responsavel='Delegado Regional'
        )
        self.usuario = Usuario.objects.create_user(
            username='policial.teste',
            password='senha123',
            first_name='Policial',
            last_name='de Teste',
            matricula='PF99999',
            perfil=Usuario.PERFIL_RESPONSAVEL
        )
        self.viatura = Viatura.objects.create(
            placa='PF-0101',
            marca='Toyota',
            modelo='Hilux 4x4',
            ano_fabricacao=2023,
            ano_modelo=2023,
            cor='Preta',
            tipo=Viatura.TIPO_OSTENSIVA,
            status=Viatura.STATUS_DISPONIVEL,
            setor_pertencente=self.setor,
            responsavel_tipo=Viatura.RESP_TIPO_SETOR,
            responsavel_setor='DREX',
            km_atual=30000,
            proxima_manutencao_km=40000,
            proxima_manutencao_data=date.today() + timedelta(days=90)
        )

    def test_str_representations(self):
        self.assertEqual(str(self.setor), "DREX - Delegacia Regional Executiva")
        self.assertIn("PF-0101", str(self.viatura))
        self.assertEqual(self.viatura.identificacao_responsavel, "DREX")

    def test_responsavel_pessoa(self):
        self.viatura.responsavel_tipo = Viatura.RESP_TIPO_PESSOA
        self.viatura.responsavel_pessoa = self.usuario
        self.viatura.save()
        self.assertEqual(self.viatura.identificacao_responsavel, "Policial de Teste")

    def test_alerta_manutencao_regular(self):
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta['status'], 'regular')

    def test_alerta_manutencao_proxima_km(self):
        # 40000 - 39500 = 500 km restantes (proxima)
        self.viatura.km_atual = 39500
        self.viatura.save()
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta['status'], 'proxima')

    def test_alerta_manutencao_vencida_km(self):
        # 40500 > 40000 (vencida)
        self.viatura.km_atual = 40500
        self.viatura.save()
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta['status'], 'vencida')

    def test_alerta_manutencao_proxima_data(self):
        self.viatura.proxima_manutencao_km = None
        self.viatura.proxima_manutencao_data = date.today() + timedelta(days=10)
        self.viatura.save()
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta['status'], 'proxima')

    def test_alerta_manutencao_vencida_data(self):
        self.viatura.proxima_manutencao_km = None
        self.viatura.proxima_manutencao_data = date.today() - timedelta(days=2)
        self.viatura.save()
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta['status'], 'vencida')

    def test_criacao_manutencao_atualiza_viatura(self):
        nova_data_revisao = date.today() + timedelta(days=180)
        manutencao = Manutencao.objects.create(
            viatura=self.viatura,
            tipo=Manutencao.TIPO_PREVENTIVA,
            data_manutencao=date.today(),
            km_no_momento=35000,
            fornecedor_oficina='Concessionária Autorizada',
            descricao_servico='Troca de óleo e filtros',
            valor_total=850.00,
            proxima_revisao_km=45000,
            proxima_revisao_data=nova_data_revisao,
            registrado_por=self.usuario
        )
        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.proxima_manutencao_km, 45000)
        self.assertEqual(self.viatura.proxima_manutencao_data, nova_data_revisao)
        self.assertIn("Troca de óleo", manutencao.descricao_servico)


class RelatoriosVeiculosTestCase(TestCase):
    def setUp(self):
        self.setor = Setor.objects.create(sigla='GPI', nome='Grupo de Pronta Intervenção')
        self.viatura = Viatura.objects.create(
            placa='PF-0202',
            marca='Chevrolet',
            modelo='Trailblazer Blindada',
            ano_fabricacao=2024,
            ano_modelo=2024,
            setor_pertencente=self.setor,
            km_atual=15000
        )
        self.manutencao = Manutencao.objects.create(
            viatura=self.viatura,
            tipo=Manutencao.TIPO_REVISAO,
            km_no_momento=10000,
            fornecedor_oficina='Oficina Central PF',
            descricao_servico='Revisão de 10.000 KM'
        )

    def test_gerar_pdf_frota(self):
        viaturas = Viatura.objects.all()
        pdf_bytes = gerar_pdf_viaturas(viaturas)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_gerar_excel_frota(self):
        viaturas = Viatura.objects.all()
        excel_bytes = gerar_excel_viaturas(viaturas)
        # Validação do cabeçalho de arquivo ZIP / XLSX PK\x03\x04
        self.assertTrue(excel_bytes.startswith(b'PK\x03\x04'))

    def test_gerar_pdf_historico_manutencao(self):
        manutencoes = self.viatura.manutenções.all()
        pdf_bytes = gerar_pdf_manutencoes_viatura(self.viatura, manutencoes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_gerar_excel_historico_manutencao(self):
        manutencoes = self.viatura.manutenções.all()
        excel_bytes = gerar_excel_manutencoes(self.viatura, manutencoes)
        self.assertTrue(excel_bytes.startswith(b'PK\x03\x04'))

