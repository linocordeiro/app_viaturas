from collections import defaultdict
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from fichas.models import FichaControle, RegistroUso
from veiculos.models import Viatura
from accesscontrol.services import obter_widgets_dashboard


@login_required
def home(request):
    hoje = date.today()
    meus_widgets = obter_widgets_dashboard(request.user)

    # Ficha de hoje
    ficha_hoje = FichaControle.objects.filter(data_expediente=hoje).first()

    # Viaturas em trânsito (registros de uso em aberto)
    registros_em_aberto = (
        RegistroUso.objects.filter(status=RegistroUso.STATUS_EM_TRANSITO)
        .select_related("viatura", "ficha")
        .order_by("-ficha__data_expediente", "-horario_saida")
    )

    # Métricas de Frota em consulta única consolidada
    metricas_frota = Viatura.objects.filter(ativo=True).aggregate(
        total=Count("pk"),
        disponiveis=Count("pk", filter=Q(status=Viatura.STATUS_DISPONIVEL)),
        em_uso=Count("pk", filter=Q(status=Viatura.STATUS_EM_USO)),
        manutencao=Count("pk", filter=Q(status=Viatura.STATUS_MANUTENCAO)),
        indisponiveis=Count("pk", filter=Q(status=Viatura.STATUS_INDISPONIVEL)),
    )
    total_viaturas = metricas_frota["total"]
    disponiveis = metricas_frota["disponiveis"]
    em_uso = metricas_frota["em_uso"]
    manutencao = metricas_frota["manutencao"]
    indisponiveis = metricas_frota["indisponiveis"]

    # Alertas de manutenção urgentes ou próximas
    todas_viaturas = Viatura.objects.filter(ativo=True).select_related("setor_pertencente")
    viaturas_alerta = []
    for v in todas_viaturas:
        alerta = v.get_alerta_manutencao()
        if alerta["status"] in ["vencida", "proxima"]:
            viaturas_alerta.append({
                "viatura": v,
                "alerta": alerta,
            })

    # Histórico de KM rodados nos últimos 7 dias em consulta única (sem N+1)
    data_inicio_7dias = hoje - timedelta(days=6)
    registros_periodo = (
        RegistroUso.objects.filter(
            ficha__data_expediente__gte=data_inicio_7dias,
            status=RegistroUso.STATUS_CONCLUIDO,
        )
        .select_related("ficha")
    )

    km_por_data = defaultdict(int)
    for reg in registros_periodo:
        km_por_data[reg.ficha.data_expediente] += reg.km_percorrido

    dias_grafico = []
    km_grafico = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        dias_grafico.append(dia.strftime("%d/%m"))
        km_grafico.append(km_por_data[dia])

    # Totais gerais do mês atual
    total_saidas_mes = RegistroUso.objects.filter(
        ficha__data_expediente__year=hoje.year,
        ficha__data_expediente__month=hoje.month,
    ).count()


    return render(request, "dashboard/index.html", {
        "hoje": hoje,
        "ficha_hoje": ficha_hoje,
        "registros_em_aberto": registros_em_aberto,
        "total_viaturas": total_viaturas,
        "disponiveis": disponiveis,
        "em_uso": em_uso,
        "manutencao": manutencao,
        "indisponiveis": indisponiveis,
        "viaturas_alerta": viaturas_alerta,
        "dias_grafico": dias_grafico,
        "km_grafico": km_grafico,
        "total_saidas_mes": total_saidas_mes,
        "meus_widgets": meus_widgets,
    })
