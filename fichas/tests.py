from datetime import date, time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from fichas.models import FichaControle, RegistroUso
from services.relatorios_excel import gerar_excel_ficha
from services.relatorios_pdf import gerar_pdf_ficha
from veiculos.models import Setor, Viatura

Usuario = get_user_model()


class FichaControleTestCase(TestCase):
    def setUp(self):
        self.setor, _ = Setor.objects.get_or_create(sigla="GISE", defaults={"nome": "Grupo de Investigações Sensíveis"})
        self.vigilante = Usuario.objects.create_user(
            username="vigilante.teste",
            password="senha123",
            first_name="Vigilante",
            last_name="de Plantão",
            is_superuser=True,
        )
        self.responsavel = Usuario.objects.create_user(
            username="responsavel.teste",
            password="senha123",
            first_name="Agente",
            last_name="Responsável",
            is_superuser=True,
        )
        self.chefia = Usuario.objects.create_user(
            username="chefia.teste",
            password="senha123",
            first_name="Delegado",
            last_name="Chefe",
            is_superuser=True,
        )
        self.viatura = Viatura.objects.create(
            placa="PF-0505",
            marca="Toyota",
            modelo="Corolla Executivo",
            setor_pertencente=self.setor,
            km_atual=20000,
            status=Viatura.STATUS_DISPONIVEL
        )
        from django.utils import timezone
        hora_atual = timezone.localtime().time()
        if hora_atual >= time(19, 0) or hora_atual < time(7, 0):
            h_inicio = time(19, 0)
            h_termino = time(7, 0)
        else:
            h_inicio = time(7, 0)
            h_termino = time(19, 0)

        self.ficha = FichaControle.objects.create(
            data_expediente=date.today(),
            horario_inicio=h_inicio,
            horario_termino=h_termino,
            vigilante=self.vigilante,
            nome_vigilante="Vigilante de Plantão"
        )

    def test_fluxo_saida_viatura(self):
        """Ao registrar a saída de uma viatura, o status dela muda para EM_USO."""
        registro = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor="APF João Silva",
            destino="Aeroporto Internacional",
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
            condutor="APF João Silva",
            destino="Diligência Operacional",
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
            condutor="APF Carlos Lima",
            destino="Fórum Federal",
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
            condutor="APF Teste",
            destino="Missão Tardia",
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
            condutor="APF Marcos Rocha",
            destino="Tribunal Regional",
            horario_saida=time(14, 0),
            odometro_saida=20000,
            horario_chegada=time(16, 0),
            odometro_chegada=20045,
            status=RegistroUso.STATUS_CONCLUIDO,
            possui_avarias=True,
            avarias_encontradas="Pequeno risco no para-choque dianteiro direito."
        )

        pdf_bytes = gerar_pdf_ficha(self.ficha)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

        excel_bytes = gerar_excel_ficha(self.ficha)
        self.assertTrue(excel_bytes.startswith(b"PK\x03\x04"))

    def test_registro_editar_com_dados_chegada(self):
        """Verifica se a view registro_editar permite preencher/editar dados de chegada."""
        self.client.force_login(self.vigilante)
        registro = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor="APF Paulo Souza",
            destino="Operação Ronda",
            horario_saida=time(10, 0),
            odometro_saida=20000,
            status=RegistroUso.STATUS_EM_TRANSITO,
            registrado_por=self.vigilante
        )

        # GET na página de edição
        response = self.client.get(f"/fichas/registro/{registro.pk}/editar/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar Registro de Movimentação de Viatura")
        self.assertContains(response, "Dados de Chegada / Retorno e Avarias")

        # POST atualizando tanto saída quanto preenchendo a chegada
        post_data = {
            "viatura": self.viatura.pk,
            "condutor": "APF Paulo Souza (Mat. 9988)",
            "destino": "Operação Ronda - Centro",
            "data_saida": date.today().strftime("%Y-%m-%d"),
            "horario_saida": "10:00",
            "odometro_saida": 20000,
            "data_chegada": date.today().strftime("%Y-%m-%d"),
            "horario_chegada": "12:30",
            "odometro_chegada": 20060,
            "possui_avarias": True,
            "avarias_encontradas": "Farol de milha direito com lâmpada queimada.",
            "status": RegistroUso.STATUS_EM_TRANSITO  # Deve auto-ajustar para CONCLUIDO
        }
        post_resp = self.client.post(f"/fichas/registro/{registro.pk}/editar/", data=post_data)
        self.assertEqual(post_resp.status_code, 302)

        registro.refresh_from_db()
        self.assertEqual(registro.condutor, "APF Paulo Souza (Mat. 9988)")
        self.assertEqual(registro.horario_chegada, time(12, 30))
        self.assertEqual(registro.odometro_chegada, 20060)
        self.assertEqual(registro.km_percorrido, 60)
        self.assertTrue(registro.possui_avarias)
        self.assertEqual(registro.avarias_encontradas, "Farol de milha direito com lâmpada queimada.")
        self.assertEqual(registro.status, RegistroUso.STATUS_CONCLUIDO)

        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.status, Viatura.STATUS_DISPONIVEL)
        self.assertEqual(self.viatura.km_atual, 20060)

    def test_registro_saida_criar_view(self):
        """Verifica que a view registro_saida_criar não dispara RelatedObjectDoesNotExist."""
        self.client.force_login(self.vigilante)
        post_data = {
            "viatura": self.viatura.pk,
            "condutor": "APF Marcos Teste",
            "destino": "Diligência",
            "data_saida": date.today().strftime("%Y-%m-%d"),
            "horario_saida": "14:00",
            "odometro_saida": 20000,
        }
        response = self.client.post(f"/fichas/{self.ficha.pk}/saida/", data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RegistroUso.objects.filter(condutor="APF Marcos Teste").exists())

    def test_movimentacao_independente_entre_fichas(self):
        """
        Testa o fluxo completo:
        1. Ficha A: viatura sai e fica em trânsito.
        2. Ficha A é encerrada com a viatura ainda na rua.
        3. Ficha B: viatura retorna nesta nova ficha via chegada avulsa.
        4. O KM percorrido é calculado a partir da saída da Ficha A e a viatura volta a ficar DISPONIVEL.
        """
        from datetime import timedelta
        self.client.force_login(self.vigilante)

        # 1. Registra saída na Ficha A
        reg_saida = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor="APF Carlos Missão",
            destino="Operação Fronteira",
            data_saida=self.ficha.data_expediente,
            horario_saida=time(14, 0),
            odometro_saida=20000,
            tipo_movimentacao=RegistroUso.TIPO_SAIDA,
            status=RegistroUso.STATUS_EM_TRANSITO,
            registrado_por=self.vigilante,
        )
        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.status, Viatura.STATUS_EM_USO)

        # 2. Encerra a Ficha A (mesmo com viatura na rua)
        self.ficha.encerrar_ficha(self.vigilante)
        self.assertEqual(self.ficha.status, FichaControle.STATUS_ENCERRADA)
        self.assertFalse(self.ficha.pode_editar)

        # Ficha A deve registrar apenas a saída
        reg_saida.refresh_from_db()
        self.assertIsNone(reg_saida.horario_chegada)
        self.assertIsNone(reg_saida.odometro_chegada)

        # 3. Cria Ficha B no dia seguinte
        amanha = self.ficha.data_expediente + timedelta(days=1)
        ficha_b = FichaControle.objects.create(
            data_expediente=amanha,
            horario_inicio=time(7, 0),
            horario_termino=time(19, 0),
            vigilante=self.vigilante,
            nome_vigilante="Vigilante de Plantão 2",
            status=FichaControle.STATUS_ABERTA,
        )

        # 4. Registra retorno da viatura na Ficha B via chegada-avulsa
        post_data = {
            "viatura": self.viatura.pk,
            "registro_saida_origem": reg_saida.pk,
            "data_chegada": amanha.strftime("%Y-%m-%d"),
            "horario_chegada": "09:30",
            "odometro_chegada": 20180,
            "possui_avarias": False,
            "avarias_encontradas": "",
        }
        resp = self.client.post(f"/fichas/{ficha_b.pk}/chegada-avulsa/", data=post_data)
        self.assertEqual(resp.status_code, 302)

        # 5. Verifica os dados da Ficha B
        reg_chegada = ficha_b.registros.first()
        self.assertIsNotNone(reg_chegada)
        self.assertEqual(reg_chegada.tipo_movimentacao, RegistroUso.TIPO_CHEGADA)
        self.assertIsNone(reg_chegada.horario_saida)
        self.assertEqual(reg_chegada.registro_saida_origem, reg_saida)
        self.assertEqual(reg_chegada.odometro_chegada, 20180)
        self.assertEqual(reg_chegada.km_percorrido, 180)

        # 6. Verifica que a viatura voltou a ficar DISPONÍVEL com KM atualizado
        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.status, Viatura.STATUS_DISPONIVEL)
        self.assertEqual(self.viatura.km_atual, 20180)

        # 7. Verifica que a saída original na Ficha A foi marcada como concluída
        reg_saida.refresh_from_db()
        self.assertEqual(reg_saida.status, RegistroUso.STATUS_CONCLUIDO)

        # 8. Testa geração de relatórios de ambas as fichas sem exceções
        pdf_a = gerar_pdf_ficha(self.ficha)
        self.assertTrue(len(pdf_a) > 0)
        excel_a = gerar_excel_ficha(self.ficha)
        self.assertTrue(len(excel_a) > 0)

        pdf_b = gerar_pdf_ficha(ficha_b)
        self.assertTrue(len(pdf_b) > 0)
        excel_b = gerar_excel_ficha(ficha_b)
        self.assertTrue(len(excel_b) > 0)

    def test_ficha_controle_form_turno_diurno(self):
        """Testa abertura de ficha com turno Diurno (07:00 às 19:00)."""
        from fichas.forms import FichaControleForm
        from datetime import timedelta
        data_teste = date.today() + timedelta(days=10)
        form = FichaControleForm(
            data={
                "data_expediente": data_teste.strftime("%Y-%m-%d"),
                "turno": "DIURNO",
                "nome_vigilante": "Vigilante Diurno",
                "observacoes": "Plantão Diurno",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        ficha = form.save(commit=False)
        ficha.vigilante = self.vigilante
        ficha.save()
        self.assertEqual(ficha.horario_inicio, time(7, 0))
        self.assertEqual(ficha.horario_termino, time(19, 0))
        self.assertEqual(ficha.data_expediente, data_teste)

    def test_ficha_controle_form_turno_noturno(self):
        """Testa abertura de ficha com turno Noturno (19:00 às 07:00)."""
        from fichas.forms import FichaControleForm
        from datetime import timedelta
        data_teste = date.today() + timedelta(days=11)
        form = FichaControleForm(
            data={
                "data_expediente": data_teste.strftime("%Y-%m-%d"),
                "turno": "NOTURNO",
                "nome_vigilante": "Vigilante Noturno",
                "observacoes": "Plantão Noturno",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        ficha = form.save(commit=False)
        ficha.vigilante = self.vigilante
        ficha.save()
        self.assertEqual(ficha.horario_inicio, time(19, 0))
        self.assertEqual(ficha.horario_termino, time(7, 0))
        self.assertEqual(ficha.data_expediente, data_teste)

    def test_ficha_controle_form_data_preenchida_padrao(self):
        """Garante que o formulário é inicializado com a data do dia corrente."""
        from fichas.forms import FichaControleForm
        form = FichaControleForm()
        self.assertEqual(form.initial.get("data_expediente"), date.today())
        self.assertIn(form.initial.get("turno"), ["DIURNO", "NOTURNO"])

    def test_view_ficha_criar_com_turno(self):
        """Testa criação de ficha via view HTTP POST utilizando o campo turno."""
        from datetime import timedelta
        from django.urls import reverse
        self.client.login(username="vigilante.teste", password="senha123")
        data_teste = date.today() + timedelta(days=12)
        resp = self.client.post(reverse("fichas:criar"), {
            "data_expediente": data_teste.strftime("%Y-%m-%d"),
            "turno": "NOTURNO",
            "nome_vigilante": "Vigilante View Teste",
            "observacoes": "Obs Teste",
        })

        self.assertEqual(resp.status_code, 302)
        ficha_criada = FichaControle.objects.filter(data_expediente=data_teste, horario_inicio=time(19, 0)).first()
        self.assertIsNotNone(ficha_criada)
        self.assertEqual(ficha_criada.horario_termino, time(7, 0))
        self.assertEqual(ficha_criada.vigilante, self.vigilante)

    def test_movimentacao_unificada_saida(self):
        """Garante que a rota unificada /movimentacao/ registra a saída com sucesso."""
        from django.urls import reverse
        self.client.login(username="vigilante.teste", password="senha123")
        self.viatura.status = Viatura.STATUS_DISPONIVEL
        self.viatura.km_atual = 25000
        self.viatura.save()

        url = reverse("fichas:movimentacao_criar", kwargs={"ficha_pk": self.ficha.pk})
        post_data = {
            "viatura": self.viatura.pk,
            "tipo_movimentacao": "SAIDA",
            "condutor_saida": "Agente Silva PF001",
            "destino": "Operação Fronteira",
            "data_saida": date.today().strftime("%Y-%m-%d"),
            "horario_saida": "08:30",
            "odometro_saida": 25000,
        }
        resp = self.client.post(url, post_data)
        self.assertEqual(resp.status_code, 302)

        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.status, Viatura.STATUS_EM_USO)

        registro = self.ficha.registros.filter(viatura=self.viatura).first()
        self.assertIsNotNone(registro)
        self.assertEqual(registro.status, RegistroUso.STATUS_EM_TRANSITO)
        self.assertEqual(registro.condutor, "Agente Silva PF001")
        self.assertEqual(registro.odometro_saida, 25000)

    def test_movimentacao_unificada_retorno(self):
        """Garante que a rota unificada /movimentacao/ registra o retorno da viatura com sucesso."""
        from django.urls import reverse
        self.client.login(username="vigilante.teste", password="senha123")

        # Cria uma saída inicial na ficha
        reg_saida = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor="Agente Silva PF001",
            destino="Operação Fronteira",
            data_saida=date.today(),
            horario_saida=time(8, 30),
            odometro_saida=25000,
            tipo_movimentacao=RegistroUso.TIPO_SAIDA,
            status=RegistroUso.STATUS_EM_TRANSITO,
            registrado_por=self.vigilante,
        )
        self.viatura.status = Viatura.STATUS_EM_USO
        self.viatura.km_atual = 25000
        self.viatura.save()

        url = reverse("fichas:movimentacao_criar", kwargs={"ficha_pk": self.ficha.pk})
        post_data = {
            "viatura": self.viatura.pk,
            "tipo_movimentacao": "CHEGADA",
            "condutor_chegada": "Agente Silva PF001",
            "data_chegada": date.today().strftime("%Y-%m-%d"),
            "horario_chegada": "17:45",
            "odometro_chegada": 25150,
            "possui_avarias": False,
            "avarias_encontradas": "",
        }
        resp = self.client.post(url, post_data)
        self.assertEqual(resp.status_code, 302)

        self.viatura.refresh_from_db()
        self.assertEqual(self.viatura.status, Viatura.STATUS_DISPONIVEL)
        self.assertEqual(self.viatura.km_atual, 25150)

        reg_saida.refresh_from_db()
        self.assertEqual(reg_saida.status, RegistroUso.STATUS_CONCLUIDO)
        self.assertEqual(reg_saida.odometro_chegada, 25150)
        self.assertEqual(reg_saida.km_percorrido, 150)

    def test_registro_editar_chegada_avulsa_exibe_dados_saida_origem(self):
        """Garante que a edição de registro de chegada avulsa carrega e exibe os dados da saída de origem."""
        from django.urls import reverse
        from fichas.forms import RegistroEdicaoForm

        self.client.login(username="vigilante.teste", password="senha123")
        reg_saida = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            condutor="Condutor Original PF",
            destino="Missão Original",
            data_saida=date(2026, 9, 12),
            horario_saida=time(17, 30),
            odometro_saida=12000,
            tipo_movimentacao=RegistroUso.TIPO_SAIDA,
            status=RegistroUso.STATUS_CONCLUIDO,
            registrado_por=self.vigilante,
        )

        reg_chegada = RegistroUso.objects.create(
            ficha=self.ficha,
            viatura=self.viatura,
            registro_saida_origem=reg_saida,
            condutor="Condutor Chegada",
            destino="",
            data_chegada=date(2026, 9, 27),
            horario_chegada=time(18, 0),
            odometro_chegada=12150,
            tipo_movimentacao=RegistroUso.TIPO_CHEGADA,
            status=RegistroUso.STATUS_CONCLUIDO,
            registrado_por=self.vigilante,
        )

        form = RegistroEdicaoForm(instance=reg_chegada)
        self.assertEqual(form.initial.get("data_saida"), "2026-09-12")
        self.assertEqual(form.initial.get("horario_saida"), "17:30")
        self.assertEqual(form.initial.get("odometro_saida"), 12000)
        self.assertTrue(form.fields["data_saida"].disabled)
        self.assertTrue(form.fields["horario_saida"].disabled)
        self.assertTrue(form.fields["odometro_saida"].disabled)

        # Testa a view HTTP GET
        url = reverse("fichas:registro_editar", kwargs={"pk": reg_chegada.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "2026-09-12")
        self.assertContains(resp, "17:30")


class AssinaturaVigilanteTestCase(TestCase):
    def setUp(self):
        from django.urls import reverse
        from accesscontrol.models import Acao, Modulo, Perfil, Submodulo, UsuarioPerfil

        self.reverse = reverse
        self.setor = Setor.objects.create(sigla="DREX", nome="Delegacia Regional")
        self.vigilante = Usuario.objects.create_user(
            username="vigilante.plantao",
            password="senhaVigilante123",
            first_name="Sebastião",
            last_name="Silva",
            is_superuser=False,
        )
        self.outro_usuario = Usuario.objects.create_user(
            username="chefe.plantao",
            password="senhaChefe123",
            first_name="Carlos",
            last_name="Supervisor",
            is_superuser=False,
        )

        mod_operacao, _ = Modulo.objects.get_or_create(codigo="operacao_diaria", defaults={"nome": "Operação Diária"})
        sub_fichas, _ = Submodulo.objects.get_or_create(modulo=mod_operacao, codigo="fichas", defaults={"nome": "Fichas"})

        acao_ver, _ = Acao.objects.get_or_create(
            codigo_completo="operacao_diaria.fichas.visualizar",
            defaults={"modulo": mod_operacao, "submodulo": sub_fichas, "codigo": "visualizar", "nome": "Ver fichas"}
        )
        acao_assinar, _ = Acao.objects.get_or_create(
            codigo_completo="operacao_diaria.fichas.assinar_vigilante",
            defaults={"modulo": mod_operacao, "submodulo": sub_fichas, "codigo": "assinar_vigilante", "nome": "Assinar vigilante"}
        )
        acao_encerrar, _ = Acao.objects.get_or_create(
            codigo_completo="operacao_diaria.fichas.encerrar",
            defaults={"modulo": mod_operacao, "submodulo": sub_fichas, "codigo": "encerrar", "nome": "Encerrar ficha"}
        )

        perfil_vigilante, _ = Perfil.objects.get_or_create(nome="vigilante", defaults={"ativo": True})
        perfil_vigilante.acoes.set([acao_ver, acao_assinar, acao_encerrar])

        UsuarioPerfil.objects.create(usuario=self.vigilante, perfil=perfil_vigilante, ativo=True)
        UsuarioPerfil.objects.create(usuario=self.outro_usuario, perfil=perfil_vigilante, ativo=True)

        self.ficha = FichaControle.objects.create(
            data_expediente=date(2026, 9, 27),
            horario_inicio=time(7, 0),
            horario_termino=time(19, 0),
            vigilante=self.vigilante,
            nome_vigilante="Sebastião Silva",
        )

    def test_assinar_vigilante_manual(self):
        self.assertFalse(self.ficha.assinatura_vigilante)
        self.assertIsNone(self.ficha.vigilante_assinatura_usuario)

        self.ficha.assinar_vigilante(self.vigilante)
        self.ficha.refresh_from_db()

        self.assertTrue(self.ficha.assinatura_vigilante)
        self.assertEqual(self.ficha.vigilante_assinatura_usuario, self.vigilante)
        self.assertIsNotNone(self.ficha.data_assinatura_vigilante)

    def test_encerrar_ficha_lanca_assinatura_automaticamente(self):
        # Ficha ainda sem assinatura
        self.assertFalse(self.ficha.assinatura_vigilante)
        self.assertIsNone(self.ficha.vigilante_assinatura_usuario)

        # Ao encerrar a ficha pelo vigilante
        self.ficha.encerrar_ficha(self.vigilante)
        self.ficha.refresh_from_db()

        # Status deve ser encerrada
        self.assertEqual(self.ficha.status, FichaControle.STATUS_ENCERRADA)
        self.assertEqual(self.ficha.encerrada_por, self.vigilante)

        # Assinatura eletrônica DEVE ter sido lançada automaticamente
        self.assertTrue(self.ficha.assinatura_vigilante)
        self.assertEqual(self.ficha.vigilante_assinatura_usuario, self.vigilante)
        self.assertIsNotNone(self.ficha.data_assinatura_vigilante)

    def test_encerrar_ficha_preserva_assinatura_previa(self):
        # Vigilante assina previamente
        self.ficha.assinar_vigilante(self.vigilante)
        data_primeira_assinatura = self.ficha.data_assinatura_vigilante

        # Outro usuário encerra a ficha depois
        self.ficha.encerrar_ficha(self.outro_usuario)
        self.ficha.refresh_from_db()

        self.assertEqual(self.ficha.status, FichaControle.STATUS_ENCERRADA)
        self.assertEqual(self.ficha.encerrada_por, self.outro_usuario)
        # O signatário vigilante original é preservado
        self.assertEqual(self.ficha.vigilante_assinatura_usuario, self.vigilante)
        self.assertEqual(self.ficha.data_assinatura_vigilante, data_primeira_assinatura)

    def test_view_assinar_vigilante(self):
        self.client.login(username="vigilante.plantao", password="senhaVigilante123")
        url = self.reverse("fichas:assinar_vigilante", kwargs={"pk": self.ficha.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.ficha.refresh_from_db()
        self.assertTrue(self.ficha.assinatura_vigilante)
        self.assertEqual(self.ficha.vigilante_assinatura_usuario, self.vigilante)

    def test_view_detalhe_ficha_exibe_assinatura_pendente_e_depois_lancada(self):
        self.client.login(username="vigilante.plantao", password="senhaVigilante123")
        url_detalhe = self.reverse("fichas:detalhe", kwargs={"pk": self.ficha.pk})

        # 1. Antes de assinar: exibe botão "Assinar Ficha"
        resp1 = self.client.get(url_detalhe)
        self.assertEqual(resp1.status_code, 200)
        self.assertContains(resp1, "Assinar Ficha")
        self.assertContains(resp1, "VIGILANTE DO DIA")

        # 2. Após encerramento: assinatura é lançada automaticamente e exibida
        url_encerrar = self.reverse("fichas:encerrar", kwargs={"pk": self.ficha.pk})
        self.client.post(url_encerrar)

        resp2 = self.client.get(url_detalhe)
        self.assertEqual(resp2.status_code, 200)
        self.assertContains(resp2, "Assinatura Lançada")
        self.assertContains(resp2, "Sebastião Silva")
        self.assertContains(resp2, "Assinado eletronicamente em")


class NutranRelatoriosTestCase(TestCase):
    def setUp(self):
        from django.urls import reverse
        from accesscontrol.models import Acao, Modulo, Perfil, Submodulo, UsuarioPerfil

        self.reverse = reverse
        self.setor = Setor.objects.create(sigla="NUTRAN", nome="Núcleo de Transportes")
        self.usuario_nutran = Usuario.objects.create_user(
            username="agente.nutran",
            password="senhaNutran123",
            first_name="Agente",
            last_name="Nutran",
            is_superuser=False,
        )

        mod_operacao, _ = Modulo.objects.get_or_create(codigo="operacao_diaria", defaults={"nome": "Operação Diária"})
        sub_fichas, _ = Submodulo.objects.get_or_create(modulo=mod_operacao, codigo="fichas", defaults={"nome": "Fichas"})

        acoes_nutran = []
        for cod, nome in [
            ("visualizar", "Ver fichas"),
            ("exportar_pdf", "Exportar PDF"),
            ("exportar_excel", "Exportar Excel"),
            ("apor_visto_nutran", "Visto Nutran"),
        ]:
            a, _ = Acao.objects.get_or_create(
                codigo_completo=f"operacao_diaria.fichas.{cod}",
                defaults={"modulo": mod_operacao, "submodulo": sub_fichas, "codigo": cod, "nome": nome}
            )
            acoes_nutran.append(a)

        perfil_nutran, _ = Perfil.objects.get_or_create(nome="nutran", defaults={"ativo": True})
        perfil_nutran.acoes.set(acoes_nutran)
        UsuarioPerfil.objects.create(usuario=self.usuario_nutran, perfil=perfil_nutran, ativo=True)

        self.ficha = FichaControle.objects.create(
            data_expediente=date(2026, 9, 27),
            horario_inicio=time(7, 0),
            horario_termino=time(19, 0),
            vigilante=self.usuario_nutran,
            nome_vigilante="Agente Nutran",
        )

    def test_nutran_pode_gerar_relatorio_pdf_ficha(self):
        self.client.login(username="agente.nutran", password="senhaNutran123")
        url_pdf = self.reverse("fichas:exportar_pdf", kwargs={"pk": self.ficha.pk})
        response = self.client.get(url_pdf)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_nutran_pode_gerar_relatorio_excel_ficha(self):
        self.client.login(username="agente.nutran", password="senhaNutran123")
        url_excel = self.reverse("fichas:exportar_excel", kwargs={"pk": self.ficha.pk})
        response = self.client.get(url_excel)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"PK\x03\x04"))

    def test_nutran_visualiza_botoes_de_relatorio_no_detalhe(self):
        self.client.login(username="agente.nutran", password="senhaNutran123")
        url_detalhe = self.reverse("fichas:detalhe", kwargs={"pk": self.ficha.pk})
        response = self.client.get(url_detalhe)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Imprimir PDF Oficial")
        self.assertContains(response, "Planilha Excel")







