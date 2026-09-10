from datetime import date, time, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from veiculos.models import Setor, Viatura
from fichas.models import FichaControle, RegistroUso
from services.relatorios_pdf import gerar_pdf_ficha
from services.relatorios_excel import gerar_excel_ficha

Usuario = get_user_model()


class FichaControleTestCase(TestCase):
    def setUp(self):
        self.setor = Setor.objects.create(sigla='GISE', nome='Grupo de Investigações Sensíveis')
        self.vigilante = Usuario.objects.create_user(
            username='vigilante.teste',
            password='senha123',
            first_name='Vigilante',
            last_name='de Plantão',
            perfil=Usuario.PERFIL_VIGILANTE
        )
        self.responsavel = Usuario.objects.create_user(
            username='responsavel.teste',
            password='senha123',
            first_name='Agente',
            last_name='Responsável',
            perfil=Usuario.PERFIL_RESPONSAVEL
        )
        self.chefia = Usuario.objects.create_user(
            username='chefia.teste',
            password='senha123',
            first_name='Delegado',
            last_name='Chefe',
            perfil=Usuario.PERFIL_CHEFIA
        )
        self.viatura = Viatura.objects.create(
            placa='PF-0505',
            marca='Toyota',
            modelo='Corolla Executivo',
            setor_pertencente=self.setor,
            km_atual=20000,
            status=Viatura.STATUS_DISPONIVEL
        )
        self.ficha = FichaControle.objects.create(
            data_expediente=date.today(),
            horario_inicio=time(7, 0),
            horario_termino=time(19, 0),
            vigilante=self.vigilante,
            nome_vigilante='Vigilante de Plantão'
        )

    def test_data_expediente_unica(self):
        """Não pode haver mais de uma ficha por data de expediente."""
        with self.assertRaises(IntegrityError):
            FichaControle.objects.create(
                data_expediente=date.today(),
                horario_inicio=time(8, 0),
                horario_termino=time(20, 0),
                vigilante=self.vigilante,
                nome_vigilante='Outro Vigilante'
            )

    def test_fluxo_saida_viatura(self):
        """Ao registrar a saída de uma viatura, o status dela muda para EM_USO."""
        registro = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor='APF João Silva',
            destino='Aeroporto Internacional',
            horario_saida=time(8, 30),
            odometro_saida=20000,
            registrado_por=self.vigilante
        )
        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.status, Viatura.STATUS_EM_USO)
        self.assertEqual(registro.status, RegistroUso.STATUS_EM_TRANSITO)

    def test_fluxo_chegada_viatura(self):
        """Ao registrar a chegada válida, odômetro atualiza e status volta para DISPONIVEL."""
        registro = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor='APF João Silva',
            destino='Diligência Operacional',
            horario_saida=time(9, 0),
            odometro_saida=20000,
            registrado_por=self.vigilante
        )
        # Preenche chegada
        registro.horario_chegada = time(11, 30)
        registro.odometro_chegada = 20085
        registro.status = RegistroUso.STATUS_CONCLUIDO
        registro.save()

        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.status, Viatura.STATUS_DISPONIVEL)
        self.assertEqual(self.viatura.km_atual, 20085)
        self.assertEqual(registro.km_percorrido, 85)

    def test_validacao_odometro_chegada_menor_que_saida(self):
        """Odômetro de chegada menor que o de saída deve lançar ValidationError."""
        registro = RegistroUso(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor='APF Carlos Lima',
            destino='Fórum Federal',
            horario_saida=time(10, 0),
            odometro_saida=20000,
            horario_chegada=time(12, 0),
            odometro_chegada=19950,  # Inválido!
            status=RegistroUso.STATUS_CONCLUIDO
        )
        with self.assertRaises(ValidationError):
            registro.clean()

    def test_bloqueio_insercao_em_ficha_encerrada(self):
        """Não é permitido inserir novos registros de uso em uma ficha já encerrada."""
        self.ficha.encerrar_ficha(self.vigilante)
        self.assertEqual(self.ficha.status, FichaControle.STATUS_ENCERRADA)
        self.assertFalse(self.ficha.pode_editar)

        novo_registro = RegistroUso(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor='APF Teste',
            destino='Missão Tardia',
            horario_saida=time(20, 0),
            odometro_saida=20100
        )
        with self.assertRaises(ValidationError):
            novo_registro.clean()

    def test_vistos_e_assinaturas(self):
        """Testa o registro de vistos do responsável e da chefia."""
        self.ficha.visto_responsavel = True
        self.ficha.responsavel_visto_usuario = self.responsavel
        self.ficha.visto_chefia = True
        self.ficha.chefia_visto_usuario = self.chefia
        self.ficha.save()

        self.ficha.refresh_from_db()
        self.assertTrue(self.ficha.visto_responsavel)
        self.assertEqual(self.ficha.responsavel_visto_usuario, self.responsavel)
        self.assertTrue(self.ficha.visto_chefia)
        self.assertEqual(self.ficha.chefia_visto_usuario, self.chefia)

    def test_relatorios_ficha_pdf_e_excel(self):
        """Verifica a integridade da exportação da Ficha em PDF e Excel."""
        # Cria um registro de uso para compor a ficha
        RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor='APF Marcos Rocha',
            destino='Tribunal Regional',
            horario_saida=time(14, 0),
            odometro_saida=20000,
            horario_chegada=time(16, 0),
            odometro_chegada=20045,
            status=RegistroUso.STATUS_CONCLUIDO,
            possui_avarias=True,
            avarias_encontradas='Pequeno risco no para-choque dianteiro direito.'
        )

        pdf_bytes = gerar_pdf_ficha(self.ficha)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

        excel_bytes = gerar_excel_ficha(self.ficha)
        self.assertTrue(excel_bytes.startswith(b'PK\x03\x04'))

    def test_registro_editar_com_dados_chegada(self):
        """Verifica se a view registro_editar permite preencher/editar dados de chegada."""
        self.client.force_login(self.vigilante)
        registro = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor='APF Paulo Souza',
            destino='Operação Ronda',
            horario_saida=time(10, 0),
            odometro_saida=20000,
            status=RegistroUso.STATUS_EM_TRANSITO,
            registrado_por=self.vigilante
        )

        # GET na página de edição
        response = self.client.get(f'/fichas/registro/{registro.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar Registro de Movimentação de Viatura')
        self.assertContains(response, 'Dados de Chegada / Retorno e Avarias')

        # POST atualizando tanto saída quanto preenchendo a chegada
        post_data = {
            'viatura': self.viatura.pk,
            'condutor': 'APF Paulo Souza (Mat. 9988)',
            'destino': 'Operação Ronda - Centro',
            'horario_saida': '10:00',
            'odometro_saida': 20000,
            'horario_chegada': '12:30',
            'odometro_chegada': 20060,
            'possui_avarias': True,
            'avarias_encontradas': 'Farol de milha direito com lâmpada queimada.',
            'status': RegistroUso.STATUS_EM_TRANSITO  # Deve auto-ajustar para CONCLUIDO
        }
        post_resp = self.client.post(f'/fichas/registro/{registro.pk}/editar/', data=post_data)
        self.assertEqual(post_resp.status_code, 302)

        registro.refresh_from_db()
        self.assertEqual(registro.condutor, 'APF Paulo Souza (Mat. 9988)')
        self.assertEqual(registro.horario_chegada, time(12, 30))
        self.assertEqual(registro.odometro_chegada, 20060)
        self.assertEqual(registro.km_percorrido, 60)
        self.assertTrue(registro.possui_avarias)
        self.assertEqual(registro.avarias_encontradas, 'Farol de milha direito com lâmpada queimada.')
        self.assertEqual(registro.status, RegistroUso.STATUS_CONCLUIDO)

        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.status, Viatura.STATUS_DISPONIVEL)
        self.assertEqual(self.viatura.km_atual, 20060)

    def test_registro_saida_criar_view(self):
        """Verifica que a view registro_saida_criar não dispara RelatedObjectDoesNotExist."""
        self.client.force_login(self.vigilante)
        post_data = {
            'viatura': self.viatura.pk,
            'condutor': 'APF Marcos Teste',
            'destino': 'Diligência',
            'horario_saida': '14:00',
            'odometro_saida': 20000,
        }
        response = self.client.post(f'/fichas/{self.ficha.pk}/saida/', data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RegistroUso.objects.filter(condutor='APF Marcos Teste').exists())

