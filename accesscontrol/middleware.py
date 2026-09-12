"""
Middleware de controle de acesso por permissão.

Intercepta todas as requisições e verifica se o usuário autenticado tem
permissão para acessar a rota, lendo o atributo `codigo_permissao` da view.

Rotas sem esse atributo são consideradas públicas (somente login_required protege).
"""

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .services import tem_permissao

# Nomes de URL que não passam pela verificação de permissão
ROTAS_ISENTAS = frozenset(
    {
        "usuarios:login",
        "usuarios:logout",
    }
)


class PermissaoMiddleware:
    """
    Middleware genérico de autorização.
    Não conhece regras de negócio — apenas lê o atributo `codigo_permissao`
    da view resolvida. Novas views não exigem alterar este middleware.
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
                        from .models import LogAcesso

                        LogAcesso.objects.create(
                            tipo=LogAcesso.TIPO_NEGADO,
                            usuario=request.user if request.user.is_authenticated else None,
                            acao_tentada=codigo,
                            rota=request.path,
                            ip=self._get_ip(request),
                        )
                        raise PermissionDenied

        return self.get_response(request)

    @staticmethod
    def _get_ip(request) -> str | None:
        """Extrai o IP real do cliente, considerando proxies."""
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
