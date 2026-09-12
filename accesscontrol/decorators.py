"""
Decorator @requer_permissao para views Django.

Uso em function-based views:
    @requer_permissao("frota.viaturas.editar")
    def editar_viatura(request, pk): ...

Uso em class-based views:
    class EditarViaturaView(UpdateView):
        codigo_permissao = "frota.viaturas.editar"
"""

from functools import wraps

from django.core.exceptions import PermissionDenied

from .services import tem_permissao


def requer_permissao(codigo: str):
    """
    Decorator que verifica se o usuário possui o código de permissão indicado.
    Também define o atributo `codigo_permissao` na view para que o middleware
    possa ler sem precisar de mapeamento de URLs.

    Lança PermissionDenied (HTTP 403) se o usuário não possuir a permissão.
    """

    def decorator(view_func):
        # Permite que o middleware leia a permissão exigida sem mapeamento de URLs
        view_func.codigo_permissao = codigo

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not tem_permissao(request.user, codigo):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        wrapper.codigo_permissao = codigo
        return wrapper

    return decorator
