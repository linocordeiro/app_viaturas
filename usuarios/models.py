from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado para o sistema APP_VIATURAS da Polícia Federal.
    """
    PERFIL_VIGILANTE = "VIGILANTE"
    PERFIL_RESPONSAVEL = "RESPONSAVEL_VIATURAS"
    PERFIL_CHEFIA = "CHEFIA"
    PERFIL_ADMIN = "ADMINISTRADOR"

    PERFIL_CHOICES = [
        (PERFIL_VIGILANTE, "Vigilante / Portaria"),
        (PERFIL_RESPONSAVEL, "Responsável pelas Viaturas"),
        (PERFIL_CHEFIA, "Chefia"),
        (PERFIL_ADMIN, "Administrador do Sistema"),
    ]

    matricula = models.CharField(
        "Matrícula / Identificação",
        max_length=30,
        blank=True,
        null=True,
        help_text="Matrícula funcional do servidor ou identificação do vigilante"
    )
    cargo = models.CharField(
        "Cargo / Função",
        max_length=100,
        blank=True,
        default="Vigilante"
    )
    setor = models.CharField(
        "Setor / Unidade",
        max_length=100,
        blank=True,
        default="Portaria Principal"
    )
    telefone = models.CharField(
        "Telefone / Ramal",
        max_length=20,
        blank=True,
        null=True
    )
    perfil = models.CharField(
        "Perfil de Acesso",
        max_length=30,
        choices=PERFIL_CHOICES,
        default=PERFIL_VIGILANTE
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["first_name", "last_name", "username"]

    def __str__(self):
        nome = self.get_full_name()
        return f"{nome or self.username} ({self.get_perfil_display()})"

    @property
    def is_vigilante(self):
        return self.perfil == self.PERFIL_VIGILANTE or self.is_superuser

    @property
    def is_responsavel_viaturas(self):
        return self.perfil in [self.PERFIL_RESPONSAVEL, self.PERFIL_ADMIN] or self.is_superuser

    @property
    def is_chefia(self):
        return self.perfil in [self.PERFIL_CHEFIA, self.PERFIL_ADMIN] or self.is_superuser

    @property
    def is_admin_user(self):
        return self.perfil == self.PERFIL_ADMIN or self.is_superuser
