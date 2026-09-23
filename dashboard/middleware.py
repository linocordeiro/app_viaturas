import os
from pathlib import Path

from django.conf import settings
from django.db import connections
from dotenv import load_dotenv


def apply_environment(override=True):
    """
    Recarrega as variáveis de ambiente do arquivo .env e atualiza as configurações
    ativas do Django (APP_ENV, DEBUG, base de dados e conexão do banco).
    """
    base_dir = Path(settings.BASE_DIR)
    env_file = base_dir / ".env"

    if env_file.exists():
        try:
            load_dotenv(str(env_file), override=override)
        except (PermissionError, OSError):
            pass

    DB_ENV = os.environ.get("DB_ENV", "development").strip().lower()
    if DB_ENV == "production":
        debug = False
        db_name = str(base_dir / "database" / "db_prod.sqlite3")
    else:
        DB_ENV = "development"
        debug = True
        db_name = str(base_dir / "database" / "db_dev.sqlite3")

    settings.DB_ENV = DB_ENV
    settings.DEBUG = debug
    settings.DATABASES["default"]["NAME"] = db_name

    # Sincroniza a conexão ativa do banco de dados (fecha conexão anterior se o arquivo mudou)
    if "default" in connections.databases:
        default_conn = connections["default"]
        if default_conn.settings_dict.get("NAME") != db_name:
            default_conn.close()
            default_conn.settings_dict["NAME"] = db_name

    return DB_ENV, debug, db_name


class EnvReloadMiddleware:
    """
    Middleware executado a cada requisição HTTP para assegurar que as variáveis de ambiente
    do .env estejam sempre atualizadas sem necessidade de reiniciar manualmente o servidor.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        apply_environment(override=True)
        return self.get_response(request)


class RealIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        real_ip = request.META.get("HTTP_X_REAL_IP") or request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )
        if real_ip:
            # X-Forwarded-For pode conter uma lista "cliente, proxy1, proxy2" — pega o primeiro
            request.META["REMOTE_ADDR"] = real_ip.split(",")[0].strip()
        return self.get_response(request)
