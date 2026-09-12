"""
Comando: python manage.py setup_permissoes

Cria ou atualiza toda a estrutura de módulos, submódulos, ações, perfis e
widgets do dashboard com as permissões padrão do sistema.

Este comando é idempotente — pode ser executado múltiplas vezes sem efeitos colaterais.
Útil para:
  - Setup inicial após deploy
  - Restaurar permissões padrão após alterações indevidas
  - Adicionar novas ações a perfis existentes
"""

from django.core.management.base import BaseCommand

from accesscontrol.migrations.seeders import ESTRUTURA, PERFIS, WIDGETS


class Command(BaseCommand):
    help = "Cria/atualiza módulos, ações e perfis padrão do sistema"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove e recria todas as ações de todos os perfis (atenção: desfaz customizações manuais)",
        )

    def handle(self, *args, **options):
        from accesscontrol.models import Acao, DashboardWidget, Modulo, Perfil, Submodulo

        self.stdout.write(self.style.MIGRATE_HEADING("=== Setup de Permissões — App Viaturas PF ==="))

        # ── Criar módulos, submódulos e ações ─────────────────────────────────
        total_acoes = 0
        for estrutura_modulo in ESTRUTURA:
            modulo, criado = Modulo.objects.get_or_create(
                codigo=estrutura_modulo["codigo"],
                defaults={
                    "nome": estrutura_modulo["nome"],
                    "icone": estrutura_modulo.get("icone", "fas fa-cube"),
                    "ordem": estrutura_modulo["ordem"],
                    "ativo": True,
                },
            )
            prefixo = self.style.SUCCESS("  [CRIADO]") if criado else "  [OK]"
            self.stdout.write(f"{prefixo} Módulo: {modulo.nome}")

            for estrutura_sub in estrutura_modulo.get("submodulos", []):
                submodulo, _ = Submodulo.objects.get_or_create(
                    modulo=modulo,
                    codigo=estrutura_sub["codigo"],
                    defaults={"nome": estrutura_sub["nome"], "ordem": estrutura_sub["ordem"], "ativo": True},
                )

                for codigo_acao, nome_acao, tipo_acao in estrutura_sub.get("acoes", []):
                    codigo_completo = f"{modulo.codigo}.{submodulo.codigo}.{codigo_acao}"
                    _, criado_acao = Acao.objects.get_or_create(
                        codigo_completo=codigo_completo,
                        defaults={
                            "modulo": modulo,
                            "submodulo": submodulo,
                            "nome": nome_acao,
                            "codigo": codigo_acao,
                            "tipo": tipo_acao,
                            "ativo": True,
                        },
                    )
                    total_acoes += 1

        self.stdout.write(f"\n  Total de ações: {total_acoes}")

        # ── Criar/atualizar widgets ────────────────────────────────────────────
        modulo_operacao = Modulo.objects.filter(codigo="operacao_diaria").first()
        modulo_frota = Modulo.objects.filter(codigo="frota").first()
        widget_modulo_map = {
            "ficha_hoje": modulo_operacao,
            "viaturas_em_transito": modulo_operacao,
            "metricas_frota": modulo_frota,
            "alertas_manutencao": modulo_frota,
            "grafico_km_7dias": modulo_frota,
            "total_saidas_mes": modulo_operacao,
        }
        for codigo_w, nome_w, ordem_w in WIDGETS:
            DashboardWidget.objects.get_or_create(
                codigo=codigo_w,
                defaults={"nome": nome_w, "modulo": widget_modulo_map.get(codigo_w), "ordem": ordem_w, "ativo": True},
            )

        # ── Criar/atualizar perfis e suas ações ───────────────────────────────
        todas_as_acoes = list(Acao.objects.filter(ativo=True))
        todos_os_widgets = list(DashboardWidget.objects.filter(ativo=True))

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Perfis ==="))
        for nome_perfil, config in PERFIS.items():
            perfil, criado = Perfil.objects.get_or_create(
                nome=nome_perfil,
                defaults={"descricao": config["descricao"], "ativo": True},
            )
            prefixo = self.style.SUCCESS("  [CRIADO]") if criado else "  [OK]"

            if options["reset"] or criado:
                if config["acoes"] == "__all__":
                    acoes_do_perfil = todas_as_acoes
                else:
                    acoes_do_perfil = [a for a in todas_as_acoes if a.codigo_completo in config["acoes"]]
                perfil.acoes.set(acoes_do_perfil)

                if config["widgets"] == "__all__":
                    widgets_do_perfil = todos_os_widgets
                else:
                    widgets_do_perfil = [w for w in todos_os_widgets if w.codigo in config["widgets"]]
                perfil.widgets.set(widgets_do_perfil)

                self.stdout.write(f"{prefixo} {nome_perfil} — {perfil.acoes.count()} ações, {perfil.widgets.count()} widgets")
            else:
                self.stdout.write(f"  [SKIP] {nome_perfil} (já existe — use --reset para sobrescrever ações)")

        self.stdout.write(self.style.SUCCESS("\n✓ Setup de permissões concluído com sucesso!"))
