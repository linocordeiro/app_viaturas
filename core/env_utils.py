from pathlib import Path

from django.conf import settings
from dotenv import dotenv_values


def get_env_values():
    """
    Lê diretamente o arquivo .env em disco para obter os valores em tempo real,
    sem depender de reinicialização do processo.
    """
    env_path = getattr(settings, "BASE_DIR", Path(__file__).resolve().parent.parent) / ".env"
    if env_path.exists():
        return dotenv_values(env_path)
    return {}


def get_env_variable(var_name: str, default: str = "") -> str:
    """
    Retorna o valor de uma variável diretamente do arquivo .env em tempo real.
    """
    vals = get_env_values()
    val = vals.get(var_name)
    if val is not None:
        return str(val).strip()
    return default
