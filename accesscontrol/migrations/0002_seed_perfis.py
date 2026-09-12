"""
Migration de seed: cria os módulos, submódulos, ações, perfis e
migra os usuários existentes do campo `perfil` legado para UsuarioPerfil.

Esta migration é idempotente via get_or_create.
"""

from django.db import migrations

from accesscontrol.seeders import ESTRUTURA, PERFIL_LEGADO_MAP, PERFIS, WIDGETS


def criar_estrutura(apps, schema_editor):
    """Cria módulos, submódulos, ações, perfis, widgets e migra usuários existentes."""
    Modulo = apps.get_model("accesscontrol", "Modulo")
    Submodulo = apps.get_model("accesscontrol", "Submodulo")
    Acao = apps.get_model("accesscontrol", "Acao")
    Perfil = apps.get_model("accesscontrol", "Perfil")
    UsuarioPerfil = apps.get_model("accesscontrol", "UsuarioPerfil")
    DashboardWidget = apps.get_model("accesscontrol", "DashboardWidget")
    Usuario = apps.get_model("usuarios", "Usuario")

    # ── 1. Criar módulos, submódulos e ações ──────────────────────────────────
    for estrutura_modulo in ESTRUTURA:
        modulo, _ = Modulo.objects.get_or_create(
            codigo=estrutura_modulo["codigo"],
            defaults={
                "nome": estrutura_modulo["nome"],
                "icone": estrutura_modulo.get("icone", "fas fa-cube"),
                "ordem": estrutura_modulo["ordem"],
                "ativo": True,
            },
        )

        for estrutura_sub in estrutura_modulo.get("submodulos", []):
            submodulo, _ = Submodulo.objects.get_or_create(
                modulo=modulo,
                codigo=estrutura_sub["codigo"],
                defaults={
                    "nome": estrutura_sub["nome"],
                    "ordem": estrutura_sub["ordem"],
                    "ativo": True,
                },
            )

            for codigo_acao, nome_acao, tipo_acao in estrutura_sub.get("acoes", []):
                codigo_completo = f"{modulo.codigo}.{submodulo.codigo}.{codigo_acao}"
                Acao.objects.get_or_create(
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

    # ── 2. Criar widgets do dashboard ─────────────────────────────────────────
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
            defaults={
                "nome": nome_w,
                "modulo": widget_modulo_map.get(codigo_w),
                "ordem": ordem_w,
                "ativo": True,
            },
        )

    # ── 3. Criar perfis e vincular ações ──────────────────────────────────────
    todas_as_acoes = list(Acao.objects.filter(ativo=True))
    todos_os_widgets = list(DashboardWidget.objects.filter(ativo=True))

    for nome_perfil, config in PERFIS.items():
        perfil, _ = Perfil.objects.get_or_create(
            nome=nome_perfil,
            defaults={"descricao": config["descricao"], "ativo": True},
        )

        if config["acoes"] == "__all__":
            acoes_do_perfil = todas_as_acoes
        else:
            acoes_do_perfil = [
                a for a in todas_as_acoes if a.codigo_completo in config["acoes"]
            ]
        perfil.acoes.set(acoes_do_perfil)

        if config["widgets"] == "__all__":
            widgets_do_perfil = todos_os_widgets
        else:
            widgets_do_perfil = [
                w for w in todos_os_widgets if w.codigo in config["widgets"]
            ]
        perfil.widgets.set(widgets_do_perfil)

    # ── 4. Migrar usuários existentes do campo legado para UsuarioPerfil ──────
    # Na migration usamos valores_list para acessar o campo que ainda existe no banco
    # (a migration 0002_remove_perfil_field só roda depois desta)
    for usuario in Usuario.objects.all():
        perfil_legado = getattr(usuario, "perfil", None)
        if not perfil_legado:
            continue

        nome_novo_perfil = PERFIL_LEGADO_MAP.get(perfil_legado)
        if not nome_novo_perfil:
            continue

        try:
            perfil_obj = Perfil.objects.get(nome=nome_novo_perfil)
            UsuarioPerfil.objects.get_or_create(
                usuario=usuario,
                perfil=perfil_obj,
                defaults={"ativo": True},
            )
        except Perfil.DoesNotExist:
            pass


def remover_estrutura(apps, schema_editor):
    """Reverte o seed (usado apenas no rollback da migration)."""
    from accesscontrol.seeders import ESTRUTURA as E
    from accesscontrol.seeders import PERFIS as P
    from accesscontrol.seeders import WIDGETS as W

    Modulo = apps.get_model("accesscontrol", "Modulo")
    Perfil = apps.get_model("accesscontrol", "Perfil")
    DashboardWidget = apps.get_model("accesscontrol", "DashboardWidget")

    Perfil.objects.filter(nome__in=P.keys()).delete()
    DashboardWidget.objects.filter(codigo__in=[c for c, _, _ in W]).delete()
    Modulo.objects.filter(codigo__in=[e["codigo"] for e in E]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accesscontrol", "0001_initial"),
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(criar_estrutura, remover_estrutura),
    ]
