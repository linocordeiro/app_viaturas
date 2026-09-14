"""
Views para visualização e filtragem dos logs de auditoria do sistema.
Acesso restrito a administradores através da permissão 'auditoria.logs.visualizar'.
"""

from datetime import datetime, time
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .decorators import requer_permissao
from .models import CodigoAcao, LogAuditoria


@requer_permissao("auditoria.logs.visualizar")
def auditoria_lista(request):
    """
    Exibe a listagem dos logs de auditoria com filtros avançados por
    data, horário, código de ação numérico, usuário e busca textual.
    """
    queryset = LogAuditoria.objects.select_related("usuario").all()

    # 1. Filtros recebidos via GET
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()
    hora_inicio = request.GET.get("hora_inicio", "").strip()
    hora_fim = request.GET.get("hora_fim", "").strip()
    codigo_filtro = request.GET.get("codigo", "").strip()
    usuario_filtro = request.GET.get("usuario", "").strip()
    q = request.GET.get("q", "").strip()

    # 2. Aplicação dos filtros de data
    if data_inicio:
        try:
            dt_ini = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            queryset = queryset.filter(criado_em__date__gte=dt_ini)
        except ValueError:
            pass

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            queryset = queryset.filter(criado_em__date__lte=dt_fim)
        except ValueError:
            pass

    # 3. Aplicação dos filtros de horário (hora:minuto)
    if hora_inicio:
        try:
            partes = hora_inicio.split(":")
            h_ini = time(int(partes[0]), int(partes[1]))
            queryset = queryset.filter(criado_em__time__gte=h_ini)
        except (ValueError, IndexError):
            pass

    if hora_fim:
        try:
            partes = hora_fim.split(":")
            # Se fornecido até o minuto, abrange até o último segundo do minuto
            h_fim = time(int(partes[0]), int(partes[1]), 59)
            queryset = queryset.filter(criado_em__time__lte=h_fim)
        except (ValueError, IndexError):
            pass

    # 4. Filtro por código numérico
    if codigo_filtro:
        try:
            cod_num = int(codigo_filtro)
            queryset = queryset.filter(codigo=cod_num)
        except ValueError:
            pass

    # 5. Filtro por usuário
    if usuario_filtro:
        queryset = queryset.filter(
            Q(usuario__username__icontains=usuario_filtro)
            | Q(usuario__first_name__icontains=usuario_filtro)
            | Q(usuario__last_name__icontains=usuario_filtro)
            | Q(usuario_repr__icontains=usuario_filtro)
        )

    # 6. Busca textual abrangente
    if q:
        queryset = queryset.filter(
            Q(descricao__icontains=q)
            | Q(url__icontains=q)
            | Q(objeto_repr__icontains=q)
            | Q(ip__icontains=q)
        )

    # Métricas para cards informativos do topo
    hoje = timezone.localdate()
    total_registros = queryset.count()
    total_hoje = LogAuditoria.objects.filter(criado_em__date=hoje).count()
    total_bloqueados = LogAuditoria.objects.filter(codigo=CodigoAcao.SEC_ACESSO_NEGADO).count()
    total_erros = LogAuditoria.objects.filter(codigo=CodigoAcao.SYS_ERRO_500).count()

    # Paginação (50 registros por página)
    paginator = Paginator(queryset, 50)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Constrói query_string limpa sem o parâmetro 'page' para paginação
    params = request.GET.copy()
    if "page" in params:
        del params["page"]
    query_string = params.urlencode()

    context = {
        "page_obj": page_obj,
        "query_string": query_string,
        "total_registros": total_registros,
        "total_hoje": total_hoje,
        "total_bloqueados": total_bloqueados,
        "total_erros": total_erros,
        # Filtros para manter o estado do formulário
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "hora_inicio": hora_inicio,
        "hora_fim": hora_fim,
        "codigo_filtro": codigo_filtro,
        "usuario_filtro": usuario_filtro,
        "q": q,
        # Opções do catálogo de códigos
        "codigos_opcoes": CodigoAcao.CHOICES,
    }

    return render(request, "accesscontrol/auditoria_lista.html", context)


@requer_permissao("auditoria.logs.visualizar")
def auditoria_detalhes_json(request, pk):
    """
    Retorna os detalhes completos de um registro de auditoria em JSON
    para renderização no modal de inspeção.
    """
    log = get_object_or_404(LogAuditoria, pk=pk)
    data = {
        "id": log.pk,
        "codigo": log.codigo,
        "descricao": log.descricao,
        "categoria": log.categoria,
        "usuario": log.usuario_repr,
        "url": log.url,
        "metodo_http": log.metodo_http,
        "status_code": log.status_code,
        "ip": log.ip,
        "objeto_repr": log.objeto_repr,
        "objeto_id": log.objeto_id,
        "tabela_afetada": log.tabela_afetada,
        "detalhes": log.detalhes,
        "criado_em": log.criado_em.strftime("%d/%m/%Y às %H:%M:%S"),
    }
    return JsonResponse(data)
