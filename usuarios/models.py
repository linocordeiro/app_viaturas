from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado para o sistema APP_VIATURAS da Polícia Federal.

    Os perfis de acesso são gerenciados pelo app `accesscontrol` via UsuarioPerfil.
    Um usuário pode ter múltiplos perfis. A permissão efetiva é a união das ações
    de todos os perfis ativos.
    """

    matricula = models.CharField(
        "Matrícula / Identificação",
        max_length=30,
        blank=True,
        null=True,
        help_text="Matrícula funcional do servidor ou identificação do vigilante",
    )
    cargo = models.CharField(
        "Cargo / Função",
        max_length=100,
        blank=True,
        default="Vigilante",
    )
    setor = models.CharField(
        "Setor / Unidade",
        max_length=100,
        blank=True,
        default="Portaria Principal",
    )
    telefone = models.CharField(
        "Telefone / Ramal",
        max_length=20,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["first_name", "last_name", "username"]

    def __str__(self):
        nome = self.get_full_name()
        perfis = self.listar_perfis()
        if perfis:
            return f"{nome or self.username} ({', '.join(perfis)})"
        return nome or self.username

    def listar_perfis(self) -> list[str]:
        """Retorna os nomes dos perfis ativos do usuário."""
        return list(
            self.perfis_atribuidos.filter(ativo=True).values_list("perfil__nome", flat=True)
        )

    def tem_permissao(self, codigo: str) -> bool:
        """
        Verifica se o usuário possui a permissão indicada.
        Delega ao serviço central (com cache) do app accesscontrol.
        """
        from accesscontrol.services import tem_permissao

        return tem_permissao(self, codigo)
