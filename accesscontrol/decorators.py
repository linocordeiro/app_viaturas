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
                from .audit_service import registrar_log
                from .context import get_client_ip
                from .models import CodigoAcao, LogAcesso

                ip_cliente = get_client_ip(request)

                registrar_log(
                    codigo=CodigoAcao.SEC_ACESSO_NEGADO,
                    descricao=f"Acesso indevido bloqueado para a permissão '{codigo}'",
                    usuario=request.user if request.user.is_authenticated else None,
                    url=request.get_full_path() if hasattr(request, "get_full_path") else getattr(request, "path", ""),
                    metodo_http=getattr(request, "method", ""),
                    status_code=403,
                    ip=ip_cliente,
                    detalhes={"permissao_exigida": codigo, "view": view_func.__name__},
                )

                LogAcesso.objects.create(
                    tipo=LogAcesso.TIPO_NEGADO,
                    usuario=request.user if request.user.is_authenticated else None,
                    acao_tentada=codigo,
                    rota=getattr(request, "path", ""),
                    ip=ip_cliente,
                )
                raise PermissionDenied
            return view_func(request, *args, **kwargs)


        wrapper.codigo_permissao = codigo
        return wrapper

    return decorator
