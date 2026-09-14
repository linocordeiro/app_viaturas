"""
Serviço centralizado para registro de logs de auditoria.
Preenche automaticamente os dados de contexto (usuário, URL, IP, método) caso não fornecidos.
"""

from typing import Any, Optional

from .context import get_client_ip, get_current_request
from .models import CodigoAcao, LogAuditoria


def registrar_log(
    codigo: int,
    descricao: Optional[str] = None,
    usuario: Optional[Any] = None,
    url: Optional[str] = None,
    metodo_http: Optional[str] = None,
    status_code: Optional[int] = None,
    ip: Optional[str] = None,
    objeto_repr: Optional[str] = None,
    objeto_id: Optional[str] = None,
    tabela_afetada: Optional[str] = None,
    detalhes: Optional[dict] = None,
) -> LogAuditoria:
    """Registra uma entrada na tabela de auditoria."""
    request = get_current_request()

    # Preenche usuário se não informado
    if usuario is None and request and hasattr(request, "user") and request.user.is_authenticated:
        usuario = request.user

    usuario_repr = ""
    if usuario:
        nome = getattr(usuario, "get_full_name", lambda: "")() or getattr(usuario, "username", str(usuario))
        matricula = getattr(usuario, "matricula", "")
        usuario_repr = f"{nome} ({matricula})" if matricula else str(nome)
    elif request and hasattr(request, "user") and request.user.is_anonymous:
        usuario_repr = "Anônimo / Visitante"
    else:
        usuario_repr = "Sistema / Processo Automático"

    # Preenche URL se não informada
    if url is None and request:
        url = request.get_full_path() if hasattr(request, "get_full_path") else getattr(request, "path", "")

    # Preenche método HTTP
    if metodo_http is None and request:
        metodo_http = getattr(request, "method", "")

    # Preenche IP
    if ip is None:
        ip = get_client_ip(request)

    # Preenche descrição padrão a partir do código se não informada
    if not descricao:
        descricao = CodigoAcao.obter_descricao(codigo)

    categoria = CodigoAcao.obter_categoria(codigo)

    return LogAuditoria.objects.create(
        codigo=codigo,
        descricao=descricao,
        categoria=categoria,
        usuario=usuario if (usuario and hasattr(usuario, "pk") and usuario.is_authenticated) else None,
        usuario_repr=usuario_repr,
        url=url or "",
        metodo_http=metodo_http or "",
        status_code=status_code,
        ip=ip,
        objeto_repr=str(objeto_repr) if objeto_repr is not None else "",
        objeto_id=str(objeto_id) if objeto_id is not None else "",
        tabela_afetada=tabela_afetada or "",
        detalhes=detalhes or {},
    )
