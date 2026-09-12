"""
Context processors que injetam dados de permissão em todos os templates.

Registrado em settings.py → TEMPLATES → context_processors.
"""

from .models import Modulo
from .services import obter_codigos_permissao, obter_widgets_dashboard, tem_permissao


def menu_context(request):
    """
    Injeta no contexto de todos os templates:
      - modulos_menu: lista de módulos com ao menos uma ação permitida ao usuário
        (usado para montar o menu lateral dinamicamente, sem {% if perfil == X %})
      - codigos_permissao: set de todos os códigos de ação do usuário (uso interno)
      - widgets_dashboard: lista de códigos de widgets visíveis ao usuário
      - tem_permissao_fn: função callable direto no template (uso avançado)
    """
    if not request.user.is_authenticated:
        return {}

    codigos = obter_codigos_permissao(request.user)
    is_super = getattr(request.user, "is_superuser", False)

    # Filtra módulos com ao menos uma ação permitida ao usuário
    if is_super:
        modulos_menu = list(Modulo.objects.filter(ativo=True).prefetch_related("submodulos"))
    else:
        modulos_qs = (
            Modulo.objects.filter(ativo=True)
            .prefetch_related("acoes", "submodulos__acoes")
        )
        modulos_menu = [
            m for m in modulos_qs
            if any(a.codigo_completo in codigos for a in m.acoes.all())
        ]

    widgets = obter_widgets_dashboard(request.user)

    return {
        "modulos_menu": modulos_menu,
        "codigos_permissao": codigos,
        "widgets_dashboard": widgets,
        # Função callable para verificação pontual no template via call
        "tem_permissao_fn": lambda codigo: tem_permissao(request.user, codigo),
    }
