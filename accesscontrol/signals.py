"""
Signals para invalidação automática do cache de permissões.
Conectados em AccessControlConfig.ready() via apps.py.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .services import invalidar_cache, invalidar_cache_perfil


@receiver(post_save, sender="accesscontrol.UsuarioPerfil")
def on_usuario_perfil_save(sender, instance, **kwargs):
    """Invalida cache quando um perfil é atribuído ou (des)ativado para um usuário."""
    invalidar_cache(instance.usuario_id)


@receiver(post_delete, sender="accesscontrol.UsuarioPerfil")
def on_usuario_perfil_delete(sender, instance, **kwargs):
    """Invalida cache quando um vínculo de perfil é removido."""
    invalidar_cache(instance.usuario_id)


def conectar_signal_m2m():
    """
    Conecta o signal m2m_changed para Perfil.acoes após o app estar carregado.
    Chamado explicitamente em AccessControlConfig.ready() depois das apps estarem prontas.
    """
    from django.db.models.signals import m2m_changed

    from .models import Perfil

    def on_perfil_acoes_changed(sender, instance, action, **kwargs):
        if action in ("post_add", "post_remove", "post_clear"):
            invalidar_cache_perfil(instance.pk)

    m2m_changed.connect(on_perfil_acoes_changed, sender=Perfil.acoes.through)
