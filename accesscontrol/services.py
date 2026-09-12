"""
Serviço central de permissões com cache.

NUNCA espalhe queries de permissão pelo código.
Use sempre as funções deste módulo.
"""

from django.core.cache import cache

CACHE_TTL = 60 * 15  # 15 minutos


def _chave_cache(usuario_id: int) -> str:
    return f"permissoes:usuario:{usuario_id}"


def obter_codigos_permissao(usuario) -> set[str]:
    """
    Retorna o conjunto de códigos de ação permitidos para o usuário.
    Resultado é cacheado por 15 minutos.
    Para superusuários, retorna um sentinel especial tratado em tem_permissao().
    """
    if not getattr(usuario, "is_authenticated", False):
        return set()

    chave = _chave_cache(usuario.pk)
    codigos = cache.get(chave)

    if codigos is None:
        from .models import Acao

        codigos = set(
            Acao.objects.filter(
                perfis__usuarioperfil__usuario=usuario,
                perfis__usuarioperfil__ativo=True,
                ativo=True,
            ).values_list("codigo_completo", flat=True)
        )
        cache.set(chave, codigos, CACHE_TTL)

    return codigos


def tem_permissao(usuario, codigo: str) -> bool:
    """
    Verifica se o usuário possui a permissão indicada pelo código completo.
    Superusuário Django tem acesso irrestrito (bypass de infraestrutura).
    """
    if not getattr(usuario, "is_authenticated", False):
        return False
    if getattr(usuario, "is_superuser", False):
        return True
    return codigo in obter_codigos_permissao(usuario)


def invalidar_cache(usuario_id: int) -> None:
    """
    Invalida o cache de permissões de um usuário específico.
    Chamado automaticamente pelos signals ao alterar UsuarioPerfil ou Perfil.acoes.
    """
    cache.delete(_chave_cache(usuario_id))


def invalidar_cache_perfil(perfil_id: int) -> None:
    """
    Invalida o cache de permissões de TODOS os usuários de um perfil específico.
    Chamado quando as ações de um perfil são alteradas.
    """
    from .models import UsuarioPerfil

    ids = UsuarioPerfil.objects.filter(
        perfil_id=perfil_id,
        ativo=True,
    ).values_list("usuario_id", flat=True)

    for uid in ids:
        invalidar_cache(uid)


def obter_widgets_dashboard(usuario) -> list[str]:
    """
    Retorna os códigos de widgets do dashboard visíveis para o usuário.
    """
    if not getattr(usuario, "is_authenticated", False):
        return []
    if getattr(usuario, "is_superuser", False):
        from .models import DashboardWidget

        return list(DashboardWidget.objects.filter(ativo=True).values_list("codigo", flat=True))

    from .models import DashboardWidget

    return list(
        DashboardWidget.objects.filter(
            perfis__usuarioperfil__usuario=usuario,
            perfis__usuarioperfil__ativo=True,
            ativo=True,
        ).values_list("codigo", flat=True).distinct()
    )
