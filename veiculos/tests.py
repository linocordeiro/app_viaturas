from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from services.relatorios_excel import gerar_excel_manutencoes, gerar_excel_viaturas
from services.relatorios_pdf import (
    cabecalho_institucional,
    gerar_pdf_manutencoes_viatura,
    gerar_pdf_viaturas,
)
from veiculos.models import Manutencao, Setor, Viatura

Usuario = get_user_model()


class VeiculosModelTestCase(TestCase):
    def setUp(self):
        self.setor, _ = Setor.objects.get_or_create(
            sigla="DREX",
            defaults={
                "nome": "Delegacia Regional Executiva",
                "responsavel": "Delegado Regional"
            }
        )
        self.usuario = Usuario.objects.create_user(
            username="policial.teste",
            password="senha123",
            first_name="Policial",
            last_name="de Teste",
            matricula="PF99999",
            is_superuser=True,
        )
        self.viatura = Viatura.objects.create(
            placa="PF-0101",
            marca="Toyota",
            modelo="Hilux 4x4",
            ano_fabricacao=2023,
            ano_modelo=2023,
            cor="Preta",
            tipo=Viatura.TIPO_OSTENSIVA,
            status=Viatura.STATUS_DISPONIVEL,
            setor_pertencente=self.setor,
            responsavel_tipo=Viatura.RESP_TIPO_SETOR,
            responsavel_setor="DREX",
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
        self.assertEqual(alerta["status"], "regular")

    def test_alerta_manutencao_proxima_km(self):
        # 40000 - 39500 = 500 km restantes (proxima)
        self.viatura.km_atual = 39500
        self.viatura.save()
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta["status"], "proxima")

    def test_alerta_manutencao_vencida_km(self):
        # Cenário de KM excedido em relação ao limite previsto
        self.viatura.km_atual = 40500
        self.viatura.save()
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta["status"], "vencida")

    def test_alerta_manutencao_proxima_data(self):
        self.viatura.proxima_manutencao_km = None
        self.viatura.proxima_manutencao_data = date.today() + timedelta(days=10)
        self.viatura.save()
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta["status"], "proxima")

    def test_alerta_manutencao_vencida_data(self):
        self.viatura.proxima_manutencao_km = None
        self.viatura.proxima_manutencao_data = date.today() - timedelta(days=2)
        self.viatura.save()
        alerta = self.viatura.get_alerta_manutencao()
        self.assertEqual(alerta["status"], "vencida")

    def test_criacao_manutencao_atualiza_viatura(self):
        nova_data_revisao = date.today() + timedelta(days=180)
        manutencao = Manutencao.objects.create(
            viatura=self.viatura,
            tipo=Manutencao.TIPO_PREVENTIVA,
            data_manutencao=date.today(),
            km_no_momento=35000,
            fornecedor_oficina="Concessionária Autorizada",
            descricao_servico="Troca de óleo e filtros",
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
        self.setor, _ = Setor.objects.get_or_create(sigla="GPI", defaults={"nome": "Grupo de Pronta Intervenção"})
        self.viatura = Viatura.objects.create(
            placa="PF-0202",
            marca="Chevrolet",
            modelo="Trailblazer Blindada",
            ano_fabricacao=2024,
            ano_modelo=2024,
            setor_pertencente=self.setor,
            km_atual=15000
        )
        self.manutencao = Manutencao.objects.create(
            viatura=self.viatura,
            tipo=Manutencao.TIPO_REVISAO,
            km_no_momento=10000,
            fornecedor_oficina="Oficina Central PF",
            descricao_servico="Revisão de 10.000 KM"
        )

    def test_gerar_pdf_frota(self):
        viaturas = Viatura.objects.all()
        pdf_bytes = gerar_pdf_viaturas(viaturas)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_gerar_excel_frota(self):
        viaturas = Viatura.objects.all()
        excel_bytes = gerar_excel_viaturas(viaturas)
        # Validação do cabeçalho de arquivo ZIP / XLSX PK\x03\x04
        self.assertTrue(excel_bytes.startswith(b"PK\x03\x04"))

    def test_gerar_pdf_historico_manutencao(self):
        manutencoes = self.viatura.manutencoes.all()
        pdf_bytes = gerar_pdf_manutencoes_viatura(self.viatura, manutencoes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_gerar_excel_historico_manutencao(self):
        manutencoes = self.viatura.manutencoes.all()
        excel_bytes = gerar_excel_manutencoes(self.viatura, manutencoes)
        self.assertTrue(excel_bytes.startswith(b"PK\x03\x04"))

    def test_cabecalho_institucional_superintendencia(self):
        table = cabecalho_institucional("Documento Teste")
        cell_elements = table._cellvalues[0][-1]
        textos = [p.text for p in cell_elements if hasattr(p, "text")]
        self.assertIn("<b>DEPARTAMENTO DE POLÍCIA FEDERAL</b>", textos)
        idx_dpf = textos.index("<b>DEPARTAMENTO DE POLÍCIA FEDERAL</b>")
        self.assertTrue(
            any("SUPERINTEND" in t and "ACRE" in t for t in textos[idx_dpf + 1:]),
            "O texto da Superintendência Regional no Acre deve estar presente abaixo de DEPARTAMENTO DE POLÍCIA FEDERAL."
        )


class PermissoesChefiaVeiculosTestCase(TestCase):
    def setUp(self):
        from django.urls import reverse
        from accesscontrol.models import Acao, Modulo, Perfil, Submodulo, UsuarioPerfil

        self.reverse = reverse
        self.setor = Setor.objects.create(sigla="DREX", nome="Delegacia Regional Executiva")
        self.viatura = Viatura.objects.create(
            placa="BRA2E19",
            marca="Toyota",
            modelo="Hilux",
            ano_fabricacao=2023,
            ano_modelo=2023,
            setor_pertencente=self.setor,
            km_atual=30000,
        )

        mod_frota, _ = Modulo.objects.get_or_create(codigo="frota", defaults={"nome": "Gestão de Frota", "ordem": 2})
        sub_viaturas, _ = Submodulo.objects.get_or_create(modulo=mod_frota, codigo="viaturas", defaults={"nome": "Viaturas", "ordem": 1})
        sub_manutencao, _ = Submodulo.objects.get_or_create(modulo=mod_frota, codigo="manutencao", defaults={"nome": "Manutenção", "ordem": 2})

        # Ações de visualização (permitidas para chefia)
        acao_ver_viaturas, _ = Acao.objects.get_or_create(
            codigo_completo="frota.viaturas.visualizar",
            defaults={"modulo": mod_frota, "submodulo": sub_viaturas, "codigo": "visualizar", "nome": "Visualizar viaturas", "tipo": "tela"}
        )
        acao_ver_manutencao, _ = Acao.objects.get_or_create(
            codigo_completo="frota.manutencao.visualizar",
            defaults={"modulo": mod_frota, "submodulo": sub_manutencao, "codigo": "visualizar", "nome": "Visualizar manutenção", "tipo": "tela"}
        )

        # Ações de escrita (NÃO permitidas para chefia)
        Acao.objects.get_or_create(
            codigo_completo="frota.viaturas.criar",
            defaults={"modulo": mod_frota, "submodulo": sub_viaturas, "codigo": "criar", "nome": "Criar viatura", "tipo": "acao"}
        )
        Acao.objects.get_or_create(
            codigo_completo="frota.viaturas.editar",
            defaults={"modulo": mod_frota, "submodulo": sub_viaturas, "codigo": "editar", "nome": "Editar viatura", "tipo": "acao"}
        )
        Acao.objects.get_or_create(
            codigo_completo="frota.manutencao.criar",
            defaults={"modulo": mod_frota, "submodulo": sub_manutencao, "codigo": "criar", "nome": "Criar manutenção", "tipo": "acao"}
        )

        # Perfil Chefia com permissões estritamente de visualização/consulta e relatórios
        self.perfil_chefia, _ = Perfil.objects.get_or_create(nome="chefia", defaults={"descricao": "Perfil Chefia", "ativo": True})
        self.perfil_chefia.acoes.set([acao_ver_viaturas, acao_ver_manutencao])

        self.user_chefia = Usuario.objects.create_user(
            username="delegado.teste",
            password="senhaChefia123",
            first_name="Delegado",
            last_name="Regional",
            is_superuser=False,
        )
        UsuarioPerfil.objects.create(usuario=self.user_chefia, perfil=self.perfil_chefia, ativo=True)

    def test_chefia_lista_viaturas_sem_botoes_de_acao(self):
        self.client.login(username="delegado.teste", password="senhaChefia123")
        response = self.client.get(self.reverse("veiculos:lista"))
        self.assertEqual(response.status_code, 200)

        # Pode consultar os dados e relatórios
        self.assertContains(response, "Relatório PDF")
        self.assertContains(response, "Planilha Excel")
        self.assertContains(response, 'title="Ver Histórico Completo da Viatura"')
        self.assertContains(response, "BRA2E19")

        # NÃO pode ver botões de ação para criar ou editar
        self.assertNotContains(response, "Nova Viatura")
        self.assertNotContains(response, 'title="Editar Veículo"')

    def test_chefia_detalhe_viatura_sem_botoes_de_acao(self):
        self.client.login(username="delegado.teste", password="senhaChefia123")
        response = self.client.get(self.reverse("veiculos:detalhe", kwargs={"pk": self.viatura.pk}))
        self.assertEqual(response.status_code, 200)

        # Pode consultar relatórios
        self.assertContains(response, "PDF Manutenção")
        self.assertContains(response, "Excel Manutenção")
        self.assertContains(response, "BRA2E19")

        # NÃO pode ver botões de registrar manutenção nem de editar viatura
        self.assertNotContains(response, "Registrar Manutenção")
        self.assertNotContains(response, "Editar Viatura")
        self.assertNotContains(response, "Agendar / Nova Manutenção")
        self.assertNotContains(response, "Nova Manutenção")

    def test_chefia_bloqueada_em_urls_de_modificacao(self):
        self.client.login(username="delegado.teste", password="senhaChefia123")

        # Tentativa de criar viatura -> 403
        r_criar = self.client.get(self.reverse("veiculos:criar"))
        self.assertEqual(r_criar.status_code, 403)

        # Tentativa de editar viatura -> 403
        r_editar = self.client.get(self.reverse("veiculos:editar", kwargs={"pk": self.viatura.pk}))
        self.assertEqual(r_editar.status_code, 403)

        # Tentativa de registrar manutenção -> 403
        r_manut = self.client.get(self.reverse("veiculos:manutencao_criar", kwargs={"viatura_pk": self.viatura.pk}))
        self.assertEqual(r_manut.status_code, 403)

    def test_chefia_pode_gerar_relatorios(self):
        self.client.login(username="delegado.teste", password="senhaChefia123")

        # Relatório PDF de Viaturas
        r_pdf_v = self.client.get(self.reverse("veiculos:exportar_pdf"))
        self.assertEqual(r_pdf_v.status_code, 200)
        self.assertEqual(r_pdf_v["Content-Type"], "application/pdf")

        # Relatório Excel de Viaturas
        r_xls_v = self.client.get(self.reverse("veiculos:exportar_excel"))
        self.assertEqual(r_xls_v.status_code, 200)

        # Relatório PDF de Manutenções da Viatura
        r_pdf_m = self.client.get(self.reverse("veiculos:exportar_manutencoes_pdf", kwargs={"pk": self.viatura.pk}))
        self.assertEqual(r_pdf_m.status_code, 200)
        self.assertEqual(r_pdf_m["Content-Type"], "application/pdf")

        # Relatório Excel de Manutenções da Viatura
        r_xls_m = self.client.get(self.reverse("veiculos:exportar_manutencoes_excel", kwargs={"pk": self.viatura.pk}))
        self.assertEqual(r_xls_m.status_code, 200)


class RegistroAbertoPlacaTestCase(TestCase):
    def setUp(self):
        self.setor, _ = Setor.objects.get_or_create(sigla="NUTRAN", defaults={"nome": "Núcleo de Transportes"})
        self.admin = Usuario.objects.create_user(
            username="admin.teste",
            password="senhaAdmin123",
            first_name="Admin",
            matricula="PF00001",
            is_superuser=True,
        )

    def test_normalizacao_e_validacao_placa(self):
        from services.consulta_placa import normalizar_placa, validar_formato_placa

        self.assertEqual(normalizar_placa("rio-2a18"), "RIO2A18")
        self.assertEqual(normalizar_placa("abc-1234"), "ABC1234")
        self.assertTrue(validar_formato_placa("RIO2A18"))
        self.assertTrue(validar_formato_placa("ABC1234"))
        self.assertFalse(validar_formato_placa("123"))
        self.assertFalse(validar_formato_placa("INVALIDA"))

    def test_orquestrador_consulta_catalogo_e_cache(self):
        from services.consulta_placa import consultar_placa
        from veiculos.models import PlacaConsultada

        # Consulta placa conhecida no catálogo
        res = consultar_placa("RIO2A18", forcar_api=True)
        self.assertTrue(res.sucesso)
        self.assertEqual(res.marca, "Toyota")
        self.assertIn("Hilux", res.modelo)

        # Verifica se alimentou o cache
        cache = PlacaConsultada.objects.filter(placa="RIO2A18").first()
        self.assertIsNotNone(cache)
        self.assertEqual(cache.marca, "Toyota")

        # Segunda consulta sem forçar API deve vir do cache
        res_cache = consultar_placa("RIO2A18", forcar_api=False)
        self.assertTrue(res_cache.sucesso)
        self.assertEqual(res_cache.origem, "CACHE")

    def test_classificacao_nutran(self):
        # Cria veículo pendente registrado a partir de entrada/saída
        v = Viatura.objects.create(
            placa="RIO2A18",
            marca="Toyota",
            modelo="Hilux SW4",
            classificacao=Viatura.CLASSIFICACAO_PENDENTE,
            origem_dados=Viatura.ORIGEM_API,
            status=Viatura.STATUS_DISPONIVEL,
        )

        from django.urls import reverse
        self.client.login(username="admin.teste", password="senhaAdmin123")

        # 1. Acesso à listagem de classificação
        r_lista = self.client.get(reverse("veiculos:classificacao_lista"))
        self.assertEqual(r_lista.status_code, 200)
        self.assertContains(r_lista, "RIO2A18")
        self.assertContains(r_lista, "Pendente de Classificação")

        # 2. Definição pelo NUTRAN: marca como Frota da Unidade, define setor e responsável (nome e cargo)
        r_post = self.client.post(
            reverse("veiculos:classificacao_definir", kwargs={"pk": v.pk}),
            {
                "classificacao": Viatura.CLASSIFICACAO_FROTA,
                "setor_pertencente": self.setor.pk,
                "responsavel_nome": "Agente Carlos Silva",
                "responsavel_cargo": "Agente de Polícia Federal",
                "tipo": Viatura.TIPO_OSTENSIVA,
                "cor": "Preta",
                "ano_fabricacao": 2023,
                "ano_modelo": 2023,
                "chassi": "9BRXXXXXXXXXX",
                "observacoes": "Classificada formalmente pela DTI/NUTRAN.",
            },
            follow=True,
        )
        self.assertEqual(r_post.status_code, 200)

        v.refresh_from_db()
        self.assertEqual(v.classificacao, Viatura.CLASSIFICACAO_FROTA)
        self.assertEqual(v.setor_pertencente, self.setor)
        self.assertEqual(v.responsavel_nome, "Agente Carlos Silva")
        self.assertEqual(v.responsavel_cargo, "Agente de Polícia Federal")
        self.assertEqual(v.identificacao_responsavel, "Agente Carlos Silva (Agente de Polícia Federal)")
        self.assertEqual(v.classificado_por, self.admin)

    def test_configuracao_consulta_placa_view_e_teste(self):
        from django.urls import reverse
        self.client.login(username="admin.teste", password="senhaAdmin123")

        # 1. Acesso à tela de configuração
        r_cfg = self.client.get(reverse("veiculos:configuracao_placa"))
        self.assertEqual(r_cfg.status_code, 200)
        self.assertContains(r_cfg, "Integração de Consulta de Placas")

        # 2. Alteração de parâmetros: escolhe SERPRO e define proxy institucional
        r_post = self.client.post(
            reverse("veiculos:configuracao_placa"),
            {
                "consulta_habilitada": "on",
                "provedor_ativo": "SERPRO",
                "proxy_url": "http://proxy.pf.gov.br:8080",
                "timeout_segundos": 4,
                "cache_dias": 60,
                "serpro_url_token": "https://gateway.apiserpro.serpro.gov.br/token",
                "serpro_url_consulta": "https://gateway.apiserpro.serpro.gov.br/consulta-veiculo/v1/veiculo/{placa}",
                "serpro_consumer_key": "chave_teste_123",
                "serpro_consumer_secret": "segredo_teste_456",
            },
            follow=True,
        )
        self.assertEqual(r_post.status_code, 200)

        from veiculos.models import ConfiguracaoConsultaPlaca
        cfg = ConfiguracaoConsultaPlaca.obter_configuracao()
        self.assertEqual(cfg.provedor_ativo, "SERPRO")
        self.assertEqual(cfg.proxy_url, "http://proxy.pf.gov.br:8080")
        self.assertEqual(cfg.timeout_segundos, 4)

        # 3. Teste do endpoint AJAX de teste de placa
        r_ajax = self.client.get(f"{reverse('veiculos:configuracao_placa_testar')}?placa=RIO2A18")
        self.assertEqual(r_ajax.status_code, 200)
        dados = r_ajax.json()
        self.assertIn("sucesso", dados)
        self.assertIn("tempo_resposta_ms", dados)

    def test_reconciliacao_sinaliza_divergencia(self):
        from django.core.management import call_command
        # Veículo criado manualmente com dados divergentes da API para testar a sinalização
        v = Viatura.objects.create(
            placa="RIO2A18",
            marca="Fiat",
            modelo="Uno Mille",
            origem_dados=Viatura.ORIGEM_MANUAL,
            classificacao=Viatura.CLASSIFICACAO_PENDENTE,
        )

        call_command("reconciliar_placas", placa="RIO2A18")

        v.refresh_from_db()
        self.assertTrue(bool(v.divergencia_dados))
        self.assertIn("Divergência detectada", v.divergencia_dados)
        self.assertIn("Fiat", v.divergencia_dados)
        self.assertIn("Toyota", v.divergencia_dados)



