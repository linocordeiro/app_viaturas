"""
Contexto de requisição thread-safe e async-safe baseado em contextvars.
Permite aos signals e models acessarem a requisição HTTP atual (usuário, URL, IP).
"""

from contextvars import ContextVar
from typing import Any, Optional

_request_ctx: ContextVar[Optional[Any]] = ContextVar("current_request", default=None)


def set_current_request(request: Any) -> None:
    """Armazena o request atual no contexto da thread/task."""
    _request_ctx.set(request)


def get_current_request() -> Optional[Any]:
    """Recupera o request atual do contexto."""
    return _request_ctx.get()


def clear_current_request() -> None:
    """Limpa o contexto de requisição."""
    _request_ctx.set(None)


def get_client_ip(request: Optional[Any] = None) -> Optional[str]:
    """Extrai o IP real do cliente considerando proxies (X-Forwarded-For)."""
    req = request or get_current_request()
    if not req:
        return None
    xff = req.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return req.META.get("REMOTE_ADDR")
