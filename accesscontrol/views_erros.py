"""
Views customizadas para renderização das páginas de erro no padrão Frontline PF.
"""

from django.shortcuts import render


def erro_400(request, exception=None):
    """Renderiza a página de erro 400 (Bad Request)."""
    return render(request, "400.html", status=400)


def erro_403(request, exception=None):
    """Renderiza a página de erro 403 (Acesso Negado / Permissão Insuficiente)."""
    return render(request, "403.html", status=403)


def erro_404(request, exception=None):
    """Renderiza a página de erro 404 (Não Encontrado)."""
    return render(request, "404.html", status=404)


def erro_500(request):
    """Renderiza a página de erro 500 (Erro Interno do Servidor)."""
    return render(request, "500.html", status=500)
