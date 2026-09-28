from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from accesscontrol.models import CodigoAcao, LogAuditoria
from fichas.models import FichaControle, RegistroUso
from veiculos.models import Setor, Viatura

Usuario = get_user_model()


class RegistroUsoAuditoriaTestCase(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="vigilante.auditoria",
            password="password123",
            first_name="Plantonista",
            is_superuser=True,
        )
        self.setor = Setor.objects.create(sigla="DREX", nome="Delegacia Regional")
        self.viatura = Viatura.objects.create(
            placa="ABC-1234",
            marca="Toyota",
            modelo="Corolla",
            setor_pertencente=self.setor,
            km_atual=10000,
            status=Viatura.STATUS_DISPONIVEL,
        )
        self.ficha = FichaControle.objects.create(
            data_expediente=date.today(),
            horario_inicio=time(7, 0),
            horario_termino=time(19, 0),
            vigilante=self.user,
            nome_vigilante="Plantonista",
        )

    def test_registro_uso_saida_auditoria(self):
        reg = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor="APF Silva",
            destino="Operação X",
            data_saida=date.today(),
            horario_saida=time(8, 30),
            odometro_saida=10000,
            status=RegistroUso.STATUS_EM_TRANSITO,
        )
        log = LogAuditoria.objects.filter(objeto_id=str(reg.pk), codigo=CodigoAcao.FICH_SAIDA_REGISTRADA).first()
        self.assertIsNotNone(log)
        self.assertIn("Registro de saída da viatura ABC-1234", log.descricao)
        self.assertEqual(log.detalhes["odometro_saida"], 10000)

    def test_registro_uso_chegada_auditoria(self):
        reg = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor="APF Silva",
            destino="Operação X",
            data_saida=date.today(),
            horario_saida=time(8, 30),
            odometro_saida=10000,
            status=RegistroUso.STATUS_EM_TRANSITO,
        )
        # Concluir chegada
        reg.data_chegada = date.today()
        reg.horario_chegada = time(12, 0)
        reg.odometro_chegada = 10150
        reg.status = RegistroUso.STATUS_CONCLUIDO
        reg.save()

        log = LogAuditoria.objects.filter(objeto_id=str(reg.pk), codigo=CodigoAcao.FICH_RETORNO_REGISTRADO).first()
        self.assertIsNotNone(log)
        self.assertIn("Registro de retorno da viatura ABC-1234", log.descricao)
        self.assertEqual(log.detalhes["odometro_chegada"], 10150)
        self.assertEqual(reg.horario_retorno, time(12, 0))
        self.assertEqual(reg.km_retorno, 10150)
        self.assertEqual(reg.km_saida, 10000)

    def test_registro_chegada_concluir_post_view(self):
        self.client.login(username="vigilante.auditoria", password="password123")
        reg = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor="APF Silva",
            destino="Operação X",
            data_saida=date.today(),
            horario_saida=time(8, 30),
            odometro_saida=10000,
            status=RegistroUso.STATUS_EM_TRANSITO,
        )
        response = self.client.post(
            f"/fichas/registro/{reg.pk}/chegada/",
            {
                "data_chegada": date.today().strftime("%Y-%m-%d"),
                "horario_chegada": "12:30",
                "odometro_chegada": 10120,
                "possui_avarias": False,
                "avarias_encontradas": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        reg.refresh_from_db()
        self.assertEqual(reg.status, RegistroUso.STATUS_CONCLUIDO)
        self.assertEqual(reg.odometro_chegada, 10120)

        log = LogAuditoria.objects.filter(objeto_id=str(reg.pk), codigo=CodigoAcao.FICH_RETORNO_REGISTRADO).first()
        self.assertIsNotNone(log)
