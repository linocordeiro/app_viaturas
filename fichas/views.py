from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accesscontrol.decorators import requer_permissao
from services.relatorios_excel import gerar_excel_ficha
from services.relatorios_pdf import gerar_pdf_ficha
from veiculos.models import Viatura

from .forms import (
    FichaControleForm,
    RegistroChegadaForm,
    RegistroEdicaoForm,
    RegistroSaidaForm,
)
from .models import FichaControle, RegistroUso


@requer_permissao("operacao_diaria.fichas.visualizar")
def ficha_lista(request):
    data_filtro = request.GET.get("data", "").strip()
    status_filtro = request.GET.get("status", "").strip()

    fichas = FichaControle.objects.select_related("vigilante", "responsavel_visto_usuario", "chefia_visto_usuario").all()

    if data_filtro:
        try:
            data_parsed = datetime.strptime(data_filtro, "%Y-%m-%d").date()
            fichas = fichas.filter(data_expediente=data_parsed)
        except ValueError:
            data_filtro = ""

    if status_filtro:
        fichas = fichas.filter(status=status_filtro)

    # Verifica se a ficha de hoje já existe
    ficha_hoje = FichaControle.objects.filter(data_expediente=date.today()).first()

    return render(request, "fichas/lista.html", {
        "fichas": fichas,
        "ficha_hoje": ficha_hoje,
        "data_filtro": data_filtro,
        "status_filtro": status_filtro,
        "hoje": date.today(),
    })


@requer_permissao("operacao_diaria.fichas.criar")
def ficha_hoje(request):
    """
    Atalho inteligente: vai para a ficha do turno atual.
    """
    from datetime import time
    
    hoje = date.today()
    hora_atual = timezone.localtime().time()
    
    if hora_atual >= time(19, 0) or hora_atual < time(7, 0):
        h_inicio = time(19, 0)
        h_termino = time(7, 0)
        # Se for madrugada (antes das 7h), a ficha pertence à data de ontem
        if hora_atual < time(7, 0):
            from datetime import timedelta
            hoje = hoje - timedelta(days=1)
    else:
        h_inicio = time(7, 0)
        h_termino = time(19, 0)

    ficha = FichaControle.objects.filter(data_expediente=hoje, horario_inicio=h_inicio).first()

    if not ficha:
        nome_vigilante = request.user.get_full_name() or request.user.username
        ficha = FichaControle.objects.create(
            data_expediente=hoje,
            horario_inicio=h_inicio,
            horario_termino=h_termino,
            vigilante=request.user,
            nome_vigilante=nome_vigilante,
            status=FichaControle.STATUS_ABERTA
        )
        messages.success(request, f"Ficha do turno ({h_inicio.strftime('%H:%M')} às {h_termino.strftime('%H:%M')}) aberta com sucesso.")

    return redirect("fichas:detalhe", pk=ficha.pk)


@requer_permissao("operacao_diaria.fichas.criar")
def ficha_criar(request):
    if request.method == "POST":
        form = FichaControleForm(request.POST)
        if form.is_valid():
            ficha = form.save(commit=False)
            ficha.vigilante = request.user
            ficha.save()
            messages.success(request, f"Ficha Diária de {ficha.data_expediente.strftime('%d/%m/%Y')} aberta com sucesso.")
            return redirect("fichas:detalhe", pk=ficha.pk)
    else:
        initial = {
            "nome_vigilante": request.user.get_full_name() or request.user.username,
            "data_expediente": date.today(),
        }
        form = FichaControleForm(initial=initial)

    return render(request, "fichas/form.html", {
        "form": form,
        "titulo": "Abrir Nova Ficha Diária de Controle",
    })


@requer_permissao("operacao_diaria.fichas.visualizar")
def ficha_detalhe(request, pk):
    ficha = get_object_or_404(
        FichaControle.objects.select_related(
            "vigilante", "responsavel_visto_usuario", "chefia_visto_usuario", "encerrada_por"
        ),
        pk=pk
    )
    registros = ficha.registros.select_related("viatura", "condutor_usuario").all()

    # Estatísticas da ficha
    total_saidas = registros.count()
    em_transito = registros.filter(status=RegistroUso.STATUS_EM_TRANSITO).count()
    concluidos = registros.filter(status=RegistroUso.STATUS_CONCLUIDO).count()
    total_km_dia = sum(r.km_percorrido for r in registros)

    # Lista de viaturas disponíveis para novo registro de saída
    viaturas_disponiveis = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_DISPONIVEL)

    return render(request, "fichas/detalhe.html", {
        "ficha": ficha,
        "registros": registros,
        "total_saidas": total_saidas,
        "em_transito": em_transito,
        "concluidos": concluidos,
        "total_km_dia": total_km_dia,
        "viaturas_disponiveis": viaturas_disponiveis,
    })


@requer_permissao("operacao_diaria.fichas.registrar_saida")
def registro_saida_criar(request, ficha_pk):
    ficha = get_object_or_404(FichaControle, pk=ficha_pk)

    if not ficha.pode_editar:
        messages.error(request, "Esta ficha está ENCERRADA e não permite novas inclusões de saídas de viaturas.")
        return redirect("fichas:detalhe", pk=ficha.pk)

    if request.method == "POST":
        form = RegistroSaidaForm(request.POST)
        form.instance.ficha = ficha
        if form.is_valid():
            reg = form.save(commit=False)
            reg.ficha = ficha
            reg.registrado_por = request.user
            reg.status = RegistroUso.STATUS_EM_TRANSITO
            reg.save()

            messages.success(request, f"Saída da viatura {reg.viatura.placa} registrada com sucesso. Veículo em trânsito.")
            return redirect("fichas:detalhe", pk=ficha.pk)
    else:
        viatura_id = request.GET.get("viatura_id")
        initial = {}
        if viatura_id:
            viatura = Viatura.objects.filter(pk=viatura_id).first()
            if viatura:
                initial["viatura"] = viatura
                initial["odometro_saida"] = viatura.km_atual
        form = RegistroSaidaForm(initial=initial)

    import json
    odometros_map = {str(v.pk): v.km_atual for v in form.fields["viatura"].queryset}

    return render(request, "fichas/registro_saida_form.html", {
        "form": form,
        "ficha": ficha,
        "odometros_map": json.dumps(odometros_map),
    })


@requer_permissao("operacao_diaria.fichas.registrar_chegada")
def registro_chegada_concluir(request, pk):
    registro = get_object_or_404(RegistroUso.objects.select_related("ficha", "viatura"), pk=pk)
    ficha = registro.ficha

    if request.method == "POST":
        form = RegistroChegadaForm(request.POST, instance=registro)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.status = RegistroUso.STATUS_CONCLUIDO
            reg.save()

            messages.success(request, f"Retorno da viatura {reg.viatura.placa} concluído com sucesso. KM percorrido: {reg.km_percorrido:,} km.")
            return redirect("fichas:detalhe", pk=ficha.pk)
    else:
        form = RegistroChegadaForm(instance=registro)

    return render(request, "fichas/registro_chegada_form.html", {
        "form": form,
        "registro": registro,
        "ficha": ficha,
    })


def is_ficha_turno_atual(ficha):
    from datetime import date, time, timedelta
    from django.utils import timezone
    hora_atual = timezone.localtime().time()
    hoje = date.today()
    if hora_atual >= time(19, 0) or hora_atual < time(7, 0):
        h_inicio = time(19, 0)
        if hora_atual < time(7, 0):
            hoje = hoje - timedelta(days=1)
    else:
        h_inicio = time(7, 0)
    return ficha.data_expediente == hoje and ficha.horario_inicio == h_inicio


@requer_permissao("operacao_diaria.fichas.editar_registro")
def registro_editar(request, pk):
    registro = get_object_or_404(RegistroUso.objects.select_related("ficha", "viatura"), pk=pk)
    ficha = registro.ficha

    bloquear_saida = (not ficha.pode_editar) or not is_ficha_turno_atual(ficha)

    if request.method == "POST":
        form = RegistroEdicaoForm(request.POST, instance=registro, bloquear_saida=bloquear_saida)
        if form.is_valid():
            reg = form.save()
            messages.success(request, f"Registro de uso da viatura {reg.viatura.placa} atualizado com sucesso.")
            return redirect("fichas:detalhe", pk=ficha.pk)
    else:
        form = RegistroEdicaoForm(instance=registro, bloquear_saida=bloquear_saida)

    return render(request, "fichas/registro_editar_form.html", {
        "form": form,
        "registro": registro,
        "ficha": ficha,
        "bloquear_saida": bloquear_saida,
    })


@requer_permissao("operacao_diaria.fichas.apor_visto_nutran")
def ficha_assinar_responsavel(request, pk):
    ficha = get_object_or_404(FichaControle, pk=pk)

    ficha.visto_responsavel = True
    ficha.responsavel_visto_usuario = request.user
    ficha.data_visto_responsavel = timezone.now()
    ficha.save(update_fields=["visto_responsavel", "responsavel_visto_usuario", "data_visto_responsavel"])

    messages.success(request, "Visto do Responsável pelas Viaturas (NUTRAN) aplicado com sucesso.")
    return redirect("fichas:detalhe", pk=ficha.pk)


@requer_permissao("operacao_diaria.fichas.apor_visto_chefia")
def ficha_assinar_chefia(request, pk):
    ficha = get_object_or_404(FichaControle, pk=pk)

    ficha.visto_chefia = True
    ficha.chefia_visto_usuario = request.user
    ficha.data_visto_chefia = timezone.now()
    ficha.save(update_fields=["visto_chefia", "chefia_visto_usuario", "data_visto_chefia"])

    messages.success(request, "Visto da Chefia aplicado com sucesso.")
    return redirect("fichas:detalhe", pk=ficha.pk)


@requer_permissao("operacao_diaria.fichas.encerrar")
def ficha_encerrar(request, pk):
    ficha = get_object_or_404(FichaControle, pk=pk)

    if request.method == "POST":
        ficha.encerrar_ficha(request.user)
        messages.success(request, f"Ficha Diária de {ficha.data_expediente.strftime('%d/%m/%Y')} ENCERRADA com sucesso. O documento está bloqueado para edições.")
        return redirect("fichas:detalhe", pk=ficha.pk)

    return redirect("fichas:detalhe", pk=ficha.pk)


@requer_permissao("operacao_diaria.fichas.exportar_pdf")
def exportar_ficha_pdf(request, pk):
    ficha = get_object_or_404(FichaControle, pk=pk)
    pdf_bytes = gerar_pdf_ficha(ficha)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Ficha_Controle_PF_{ficha.data_expediente.strftime("%Y%m%d")}.pdf"'
    return response


@requer_permissao("operacao_diaria.fichas.exportar_excel")
def exportar_ficha_excel(request, pk):
    ficha = get_object_or_404(FichaControle, pk=pk)
    excel_bytes = gerar_excel_ficha(ficha)
    response = HttpResponse(excel_bytes, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="Ficha_Controle_PF_{ficha.data_expediente.strftime("%Y%m%d")}.xlsx"'
    return response


# Mantém compatibilidade com @login_required para a view de listagem básica
# que pode ser acessada por qualquer usuário autenticado que tenha visualizar
ficha_lista.login_required = True
