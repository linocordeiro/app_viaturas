from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from veiculos.models import Viatura, Manutencao
from fichas.models import FichaControle, RegistroUso


@login_required
def home(request):
    hoje = date.today()

    # Ficha de hoje
    ficha_hoje = FichaControle.objects.filter(data_expediente=hoje).first()

    # Viaturas em trânsito (registros de uso em aberto)
    registros_em_aberto = RegistroUso.objects.filter(
        status=RegistroUso.STATUS_EM_TRANSITO
    ).select_related('viatura', 'ficha').order_by('-ficha__data_expediente', '-horario_saida')

    # Métricas de Frota
    total_viaturas = Viatura.objects.filter(ativo=True).count()
    disponiveis = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_DISPONIVEL).count()
    em_uso = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_EM_USO).count()
    manutencao = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_MANUTENCAO).count()
    indisponiveis = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_INDISPONIVEL).count()

    # Alertas de manutenção urgentes ou próximas
    todas_viaturas = Viatura.objects.filter(ativo=True).select_related('setor_pertencente')
    viaturas_alerta = []
    for v in todas_viaturas:
        alerta = v.get_alerta_manutencao()
        if alerta['status'] in ['vencida', 'proxima']:
            viaturas_alerta.append({
                'viatura': v,
                'alerta': alerta
            })

    # Histórico de KM rodados nos últimos 7 dias
    dias_grafico = []
    km_grafico = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        dias_grafico.append(dia.strftime('%d/%m'))
        registros_dia = RegistroUso.objects.filter(
            ficha__data_expediente=dia,
            status=RegistroUso.STATUS_CONCLUIDO
        )
        km_dia = sum(r.km_percorrido for r in registros_dia)
        km_grafico.append(km_dia)

    # Totais gerais
    total_saidas_mes = RegistroUso.objects.filter(
        ficha__data_expediente__year=hoje.year,
        ficha__data_expediente__month=hoje.month
    ).count()

    return render(request, 'dashboard/index.html', {
        'hoje': hoje,
        'ficha_hoje': ficha_hoje,
        'registros_em_aberto': registros_em_aberto,
        'total_viaturas': total_viaturas,
        'disponiveis': disponiveis,
        'em_uso': em_uso,
        'manutencao': manutencao,
        'indisponiveis': indisponiveis,
        'viaturas_alerta': viaturas_alerta,
        'dias_grafico': dias_grafico,
        'km_grafico': km_grafico,
        'total_saidas_mes': total_saidas_mes,
    })
