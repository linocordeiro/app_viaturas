from datetime import date, time, timedelta, datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from veiculos.models import Setor, Viatura, Manutencao
from fichas.models import FichaControle, RegistroUso

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais e realistas da Polícia Federal'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Iniciando carga de dados iniciais do APP_VIATURAS..."))

        # 1. Setores
        setores_data = [
            ('NUTRAN', 'Núcleo de Operações de Transporte e Trânsito', 'Agente Rocha', '(61) 2024-8100'),
            ('DREX', 'Delegacia Regional Executiva', 'Delegado Almeida', '(61) 2024-8200'),
            ('DELEPAT', 'Delegacia de Repressão a Crimes Contra o Patrimônio', 'Delegado Santos', '(61) 2024-8300'),
            ('GISE', 'Grupo de Investigações Sensíveis', 'Agente Carvalho', '(61) 2024-8400'),
            ('GPI', 'Grupo de Pronta Intervenção', 'Agente Mendes', '(61) 2024-8500'),
            ('PORTARIA', 'Portaria Principal e Segurança Orgânica', 'Vigilante Silva', '(61) 2024-8010'),
        ]

        setores = {}
        for sigla, nome, resp, ramal in setores_data:
            s, created = Setor.objects.get_or_create(
                sigla=sigla,
                defaults={'nome': nome, 'responsavel': resp, 'ramal': ramal}
            )
            setores[sigla] = s

        self.stdout.write(self.style.SUCCESS(f"Setores carregados: {len(setores)}"))

        # 2. Usuários
        usuarios_data = [
            ('admin', 'admin123', 'Carlos', 'Administrador', 'admin@pf.gov.br', '00.001-A', 'Chefe de TI', 'NUTRAN', Usuario.PERFIL_ADMIN, True),
            ('vigilante.silva', 'pf123456', 'Sebastião', 'Silva', 'vigilante.silva@pf.gov.br', '19.420-V', 'Vigilante Plantonista', 'PORTARIA', Usuario.PERFIL_VIGILANTE, False),
            ('agente.rocha', 'pf123456', 'Marcelo', 'Rocha', 'marcelo.rocha@pf.gov.br', '15.823-R', 'Chefe do Setor de Viaturas', 'NUTRAN', Usuario.PERFIL_RESPONSAVEL, False),
            ('delegado.almeida', 'pf123456', 'Roberto', 'Almeida', 'roberto.almeida@pf.gov.br', '12.301-D', 'Delegado Regional Executivo', 'DREX', Usuario.PERFIL_CHEFIA, False),
            ('perito.costa', 'pf123456', 'Fernanda', 'Costa', 'fernanda.costa@pf.gov.br', '21.504-P', 'Perita Criminal Federal', 'DREX', Usuario.PERFIL_VIGILANTE, False),
        ]

        users = {}
        for username, pwd, fname, lname, email, mat, cargo, setor, perfil, is_super in usuarios_data:
            u = Usuario.objects.filter(username=username).first()
            if not u:
                u = Usuario.objects.create_user(
                    username=username,
                    password=pwd,
                    first_name=fname,
                    last_name=lname,
                    email=email,
                    matricula=mat,
                    cargo=cargo,
                    setor=setor,
                    perfil=perfil,
                    is_superuser=is_super,
                    is_staff=is_super
                )
            users[username] = u

        self.stdout.write(self.style.SUCCESS(f"Usuários carregados: {len(users)}"))

        # 3. Viaturas
        viaturas_data = [
            ('BRA2E19', 'Toyota', 'Hilux SW4 4x4', 2023, 2023, 'Preta', Viatura.TIPO_OSTENSIVA, '9BR8348278241', Viatura.STATUS_DISPONIVEL, 'NUTRAN', 32450, 40000, date(2026, 12, 10)),
            ('RIO1A23', 'Chevrolet', 'Trailblazer V6 4x4', 2022, 2023, 'Preta', Viatura.TIPO_OSTENSIVA, '9BG8329182390', Viatura.STATUS_EM_USO, 'GPI', 48900, 50000, date(2026, 9, 20)),
            ('BRA9F88', 'Toyota', 'Corolla Altis Hybrid', 2024, 2024, 'Prata', Viatura.TIPO_DESCARACTERIZADA, '9BR9283918231', Viatura.STATUS_DISPONIVEL, 'GISE', 14200, 20000, date(2026, 11, 15)),
            ('DPF3C45', 'Ford', 'Ranger XLT 3.2 4x4', 2022, 2022, 'Preta', Viatura.TIPO_OSTENSIVA, '9BF9283918299', Viatura.STATUS_DISPONIVEL, 'DELEPAT', 61200, 60000, date(2026, 8, 30)), # Revisão vencida por KM e Data!
            ('DPF5E67', 'Mitsubishi', 'L200 Triton Sport', 2023, 2023, 'Preta', Viatura.TIPO_OSTENSIVA, '9BM9283918288', Viatura.STATUS_DISPONIVEL, 'DREX', 29400, 30000, date(2026, 9, 18)), # Revisão próxima por KM!
            ('DPF7A89', 'Renault', 'Duster 1.3 Turbo', 2023, 2024, 'Branca', Viatura.TIPO_ADMINISTRATIVA, '9BR8392819200', Viatura.STATUS_MANUTENCAO, 'NUTRAN', 42100, 45000, date(2026, 10, 5)),
        ]

        viaturas = {}
        for placa, marca, modelo, fab, mod, cor, tipo, chassi, status, setor_sigla, km, prox_km, prox_data in viaturas_data:
            v, created = Viatura.objects.get_or_create(
                placa=placa,
                defaults={
                    'marca': marca,
                    'modelo': modelo,
                    'ano_fabricacao': fab,
                    'ano_modelo': mod,
                    'cor': cor,
                    'tipo': tipo,
                    'chassi': chassi,
                    'status': status,
                    'setor_pertencente': setores[setor_sigla],
                    'responsavel_tipo': Viatura.RESP_TIPO_SETOR,
                    'responsavel_setor': setor_sigla,
                    'km_atual': km,
                    'proxima_manutencao_km': prox_km,
                    'proxima_manutencao_data': prox_data,
                }
            )
            viaturas[placa] = v

        self.stdout.write(self.style.SUCCESS(f"Viaturas cadastradas: {len(viaturas)}"))

        # 4. Registros de Manutenção
        manut_data = [
            (viaturas['BRA2E19'], Manutencao.TIPO_REVISAO, date(2026, 4, 15), 30000, 'Kurumá Concessionária Toyota', 'OS-4921', 'Revisão periódica dos 30.000 km, alinhamento e balanceamento.', 'Óleo sintético 5W30, filtro de óleo, filtro de combustível', 1450.00),
            (viaturas['DPF3C45'], Manutencao.TIPO_CORRETIVA, date(2026, 5, 20), 55000, 'Auto Mecânica Especializada Federal', 'OS-8834', 'Substituição das pastilhas e discos de freio dianteiros após operação.', 'Jogo de pastilhas de freio cerâmica, discos dianteiros', 2340.00),
            (viaturas['DPF7A89'], Manutencao.TIPO_CORRETIVA, date(2026, 9, 1), 42100, 'Oficina Credenciada DF', 'OS-9102', 'Manutenção no sistema de suspensão e amortecedores.', 'Amortecedores dianteiros, batentes e buchas', 3120.00),
        ]

        for viat, tipo, dt, km, ofi, os_num, desc, pecas, val in manut_data:
            m, created = Manutencao.objects.get_or_create(
                viatura=viat,
                numero_ordem_servico=os_num,
                defaults={
                    'tipo': tipo,
                    'data_manutencao': dt,
                    'km_no_momento': km,
                    'fornecedor_oficina': ofi,
                    'descricao_servico': desc,
                    'pecas_substituidas': pecas,
                    'valor_total': val,
                    'registrado_por': users['agente.rocha']
                }
            )

        self.stdout.write(self.style.SUCCESS("Registros de manutenção carregados."))

        # 5. Fichas de Controle
        hoje = date.today()
        ontem = hoje - timedelta(days=1)

        # 5.1. Ficha de Ontem (Aberta, movimentações inseridas e depois encerrada com vistos)
        ficha_ontem, created = FichaControle.objects.get_or_create(
            data_expediente=ontem,
            defaults={
                'horario_inicio': time(7, 0),
                'horario_termino': time(19, 0),
                'vigilante': users['vigilante.silva'],
                'nome_vigilante': 'Sebastião Silva (Vigilante)',
                'status': FichaControle.STATUS_ABERTA,
                'observacoes': 'Plantão sem intercorrências graves. Todas as viaturas retornaram abastecidas.'
            }
        )

        if created:
            RegistroUso.objects.create(
                ficha=ficha_ontem,
                viatura=viaturas['BRA2E19'],
                condutor='APF João Marcos (Matrícula 18.231)',
                condutor_usuario=users['agente.rocha'],
                destino='Cumprimento de mandado em Taguatinga/DF',
                horario_saida=time(8, 30),
                odometro_saida=32300,
                horario_chegada=time(12, 45),
                odometro_chegada=32380,
                possui_avarias=False,
                status=RegistroUso.STATUS_CONCLUIDO,
                registrado_por=users['vigilante.silva']
            )
            RegistroUso.objects.create(
                ficha=ficha_ontem,
                viatura=viaturas['BRA9F88'],
                condutor='EPF Renata Souza (Matrícula 22.109)',
                destino='Diligência de intimação no Lago Sul/DF',
                horario_saida=time(14, 0),
                odometro_saida=14120,
                horario_chegada=time(17, 30),
                odometro_chegada=14180,
                possui_avarias=False,
                status=RegistroUso.STATUS_CONCLUIDO,
                registrado_por=users['vigilante.silva']
            )

            # Aplica vistos e encerra formalmente a ficha de ontem
            ficha_ontem.visto_responsavel = True
            ficha_ontem.responsavel_visto_usuario = users['agente.rocha']
            ficha_ontem.data_visto_responsavel = timezone.now() - timedelta(hours=18)
            ficha_ontem.visto_chefia = True
            ficha_ontem.chefia_visto_usuario = users['delegado.almeida']
            ficha_ontem.data_visto_chefia = timezone.now() - timedelta(hours=16)
            ficha_ontem.status = FichaControle.STATUS_ENCERRADA
            ficha_ontem.encerrada_em = timezone.now() - timedelta(hours=14)
            ficha_ontem.encerrada_por = users['vigilante.silva']
            ficha_ontem.save()

        # 5.2. Ficha de Hoje (Aberta com registros)
        ficha_hoje, created = FichaControle.objects.get_or_create(
            data_expediente=hoje,
            defaults={
                'horario_inicio': time(7, 0),
                'horario_termino': time(19, 0),
                'vigilante': users['vigilante.silva'],
                'nome_vigilante': 'Sebastião Silva (Vigilante)',
                'status': FichaControle.STATUS_ABERTA,
                'observacoes': 'Expediente diário em andamento.'
            }
        )

        if created:
            # Registro Concluído hoje cedo
            RegistroUso.objects.create(
                ficha=ficha_hoje,
                viatura=viaturas['BRA2E19'],
                condutor='DPF Ricardo Medeiros (Matrícula 11.234)',
                destino='Audiência Judicial no TRF-1',
                horario_saida=time(8, 15),
                odometro_saida=32380,
                horario_chegada=time(11, 30),
                odometro_chegada=32450,
                possui_avarias=False,
                status=RegistroUso.STATUS_CONCLUIDO,
                registrado_por=users['vigilante.silva']
            )
            # Registro Em Trânsito (Na rua neste momento!)
            RegistroUso.objects.create(
                ficha=ficha_hoje,
                viatura=viaturas['RIO1A23'],
                condutor='APF Bruno Alencar (Matrícula 17.552)',
                destino='Operação de Escolta Tática - Aeroporto de Brasília',
                horario_saida=time(13, 10),
                odometro_saida=48900,
                possui_avarias=False,
                status=RegistroUso.STATUS_EM_TRANSITO,
                registrado_por=users['vigilante.silva']
            )

        self.stdout.write(self.style.SUCCESS("Fichas de controle carregadas com sucesso."))
        self.stdout.write(self.style.SUCCESS("\n[PRONTO] Base de dados populada com sucesso!"))
        self.stdout.write("Usuários disponíveis para teste:")
        self.stdout.write(" - Administrador: admin / admin123")
        self.stdout.write(" - Vigilante:     vigilante.silva / pf123456")
        self.stdout.write(" - Responsável:   agente.rocha / pf123456")
        self.stdout.write(" - Chefia:        delegado.almeida / pf123456")
