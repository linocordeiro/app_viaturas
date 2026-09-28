from django.conf import settings
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.db import connections
from django.shortcuts import redirect

from .db_router import set_current_db
from .env_utils import get_env_variable


class DynamicDatabaseMiddleware:
    """
    Verifica a cada requisição a variável DB_ENV no arquivo .env
    e direciona as operações para 'desenvolvimento' (db_dev.sqlite3)
    ou 'producao' (db_prod.sqlite3).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        db_env_raw = get_env_variable("DB_ENV", "desenvolvimento").strip().lower()
        is_prod = db_env_raw in ("producao", "production", "prod")
        target_alias = "producao" if is_prod else "desenvolvimento"

        # Define no roteador dinâmico thread-safe
        set_current_db(target_alias)
        request.is_db_desenvolvimento = not is_prod
        request.db_env = target_alias

        # Sincroniza a conexão 'default' em ambiente normal (preserva banco isolado de testes)
        if target_alias in settings.DATABASES:
            target_path = settings.DATABASES[target_alias]["NAME"]
            conn = connections["default"]
            curr_name = str(conn.settings_dict.get("NAME", ""))
            is_test_db = ":memory:" in curr_name or "test_" in curr_name or "memorydb" in curr_name

            if not is_test_db and conn.settings_dict.get("NAME") != target_path:
                conn.close()
                conn.settings_dict["NAME"] = target_path

        return self.get_response(request)


class ManutencaoMiddleware:
    """
    Verifica a cada requisição se o modo de manutenção (APP_MNT) está ativado no arquivo .env.
    Se True, encerra todas as sessões ativas e redireciona qualquer requisição
    para a página de manutenção /manutencao/ (mantendo apenas arquivos estáticos liberados).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        val_mnt = get_env_variable("APP_MNT", "False").strip().lower()
        is_mnt = val_mnt in ("true", "1", "yes")

        if is_mnt:
            # 1. Encerra a sessão do usuário atual
            if hasattr(request, "user") and request.user.is_authenticated:
                logout(request)

            if hasattr(request, "session"):
                request.session.flush()

            # 2. Purga sessões ativas na base de dados
            try:
                Session.objects.all().delete()
            except Exception:
                pass

            # 3. Permite acesso a arquivos estáticos e à própria tela de manutenção
            if (
                not request.path.startswith(settings.STATIC_URL)
                and request.path != "/manutencao/"
            ):
                return redirect("/manutencao/")
        else:
            # Se tentar acessar a rota de manutenção e ela não estiver ativa, redireciona para a home
            if request.path == "/manutencao/":
                return redirect("/")

        return self.get_response(request)
