"""
Middlewares de controle de acesso e auditoria.
"""

import traceback
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404

from .audit_service import registrar_log
from .context import clear_current_request, get_client_ip, set_current_request
from .models import CodigoAcao, LogAcesso
from .services import tem_permissao

# Nomes de URL que não passam pela verificação de permissão
ROTAS_ISENTAS = frozenset(
    {
        "usuarios:login",
        "usuarios:logout",
    }
)


class AuditoriaContextMiddleware:
    """
    Middleware que gerencia o contexto da requisição atual para auditoria
    e intercepta exceções não tratadas para registro de erros de sistema (HTTP 500).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        try:
            response = self.get_response(request)
            return response
        finally:
            clear_current_request()

    def process_exception(self, request, exception):
        """Registra erro 500 para exceções não tratadas (excluindo 403 e 404)."""
        if isinstance(exception, (PermissionDenied, Http404)):
            return None

        tb_text = traceback.format_exc()
        try:
            registrar_log(
                codigo=CodigoAcao.SYS_ERRO_500,
                descricao=f"Instabilidade no servidor: {type(exception).__name__}: {str(exception)}",
                url=request.get_full_path() if hasattr(request, "get_full_path") else request.path,
                metodo_http=request.method,
                status_code=500,
                detalhes={
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "traceback": tb_text[:4000],  # Limita para não estourar payload
                },
            )
        except Exception:
            # Nunca impede a propagação da exceção se o log falhar
            pass

        return None


class PermissaoMiddleware:
    """
    Middleware genérico de autorização.
    Lê o atributo `codigo_permissao` da view resolvida.
    Registra tentativa de acesso negado no LogAuditoria (código 2001) e LogAcesso legado.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        match = request.resolver_match

        if match is not None:
            # Monta o identificador da rota no formato app:nome
            rota_id = f"{match.app_name}:{match.url_name}" if match.app_name else match.url_name

            if rota_id not in ROTAS_ISENTAS:
                # Suporte a function-based e class-based views
                view = match.func
                view_class = getattr(view, "view_class", None)
                codigo = getattr(view_class or view, "codigo_permissao", None)

                if codigo:
                    if not request.user.is_authenticated:
                        return redirect_to_login(request.get_full_path())

                    if not tem_permissao(request.user, codigo):
                        ip_cliente = get_client_ip(request)

                        # 1. Registro no novo modelo unificado de auditoria
                        registrar_log(
                            codigo=CodigoAcao.SEC_ACESSO_NEGADO,
                            descricao=f"Acesso indevido bloqueado para a permissão '{codigo}'",
                            usuario=request.user,
                            url=request.get_full_path(),
                            metodo_http=request.method,
                            status_code=403,
                            ip=ip_cliente,
                            detalhes={
                                "permissao_exigida": codigo,
                                "rota_id": rota_id,
                                "caminho": request.path,
                            },
                        )

                        # 2. Registro no modelo legado LogAcesso
                        LogAcesso.objects.create(
                            tipo=LogAcesso.TIPO_NEGADO,
                            usuario=request.user,
                            acao_tentada=codigo,
                            rota=request.path,
                            ip=ip_cliente,
                        )
                        raise PermissionDenied

        return self.get_response(request)
