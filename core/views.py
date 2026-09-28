from django.shortcuts import redirect, render

from .env_utils import get_env_variable


def manutencao_view(request):
    """
    Exibe a página estática de manutenção do sistema no padrão Frontline PF.
    Se o modo de manutenção não estiver ativado, redireciona para a home.
    """
    val_mnt = get_env_variable("APP_MNT", "False").strip().lower()
    is_mnt = val_mnt in ("true", "1", "yes")

    if not is_mnt:
        return redirect("dashboard:home")

    return render(request, "manutencao.html", status=503)
