from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from services.relatorios_excel import gerar_excel_manutencoes, gerar_excel_viaturas
from services.relatorios_pdf import gerar_pdf_manutencoes_viatura, gerar_pdf_viaturas

from .forms import ManutencaoForm, ViaturaForm
from .models import Manutencao, Setor, Viatura


@login_required
def viatura_lista(request):
    termo = request.GET.get("q", "").strip()
    status_filtro = request.GET.get("status", "").strip()
    setor_filtro = request.GET.get("setor", "").strip()

    viaturas = Viatura.objects.filter(ativo=True).select_related("setor_pertencente", "responsavel_pessoa")

    if termo:
        viaturas = viaturas.filter(
            placa__icontains=termo
        ) | viaturas.filter(
            modelo__icontains=termo
        ) | viaturas.filter(
            marca__icontains=termo
        )

    if status_filtro:
        viaturas = viaturas.filter(status=status_filtro)

    if setor_filtro:
        viaturas = viaturas.filter(setor_pertencente_id=setor_filtro)

    # Anexa alerta de manutenção para cada viatura na listagem
    lista_com_alertas = []
    for v in viaturas:
        lista_com_alertas.append({
            "viatura": v,
            "alerta": v.get_alerta_manutencao()
        })

    setores = Setor.objects.filter(ativo=True)

    # Estatísticas rápidas
    total_viaturas = Viatura.objects.filter(ativo=True).count()
    total_disponiveis = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_DISPONIVEL).count()
    total_em_uso = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_EM_USO).count()
    total_manutencao = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_MANUTENCAO).count()
    total_indisponiveis = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_INDISPONIVEL).count()

    return render(request, "veiculos/lista.html", {
        "viaturas_alertas": lista_com_alertas,
        "setores": setores,
        "termo": termo,
        "status_filtro": status_filtro,
        "setor_filtro": setor_filtro,
        "total_viaturas": total_viaturas,
        "total_disponiveis": total_disponiveis,
        "total_em_uso": total_em_uso,
        "total_manutencao": total_manutencao,
        "total_indisponiveis": total_indisponiveis,
    })


@login_required
def viatura_criar(request):
    if request.method == "POST":
        form = ViaturaForm(request.POST)
        if form.is_valid():
            viatura = form.save()
            messages.success(request, f"Viatura {viatura.marca} {viatura.modelo} (Placa {viatura.placa}) cadastrada com sucesso.")
            return redirect("veiculos:detalhe", pk=viatura.pk)
    else:
        form = ViaturaForm()

    return render(request, "veiculos/form.html", {
        "form": form,
        "titulo": "Cadastrar Nova Viatura",
    })


@login_required
def viatura_editar(request, pk):
    viatura = get_object_or_404(Viatura, pk=pk)

    if request.method == "POST":
        form = ViaturaForm(request.POST, instance=viatura)
        if form.is_valid():
            viatura = form.save()
            messages.success(request, f"Dados da viatura {viatura.placa} atualizados com sucesso.")
            return redirect("veiculos:detalhe", pk=viatura.pk)
    else:
        form = ViaturaForm(instance=viatura)

    return render(request, "veiculos/form.html", {
        "form": form,
        "viatura": viatura,
        "titulo": f"Editar Viatura: {viatura.placa}",
    })


@login_required
def viatura_detalhe(request, pk):
    viatura = get_object_or_404(Viatura, pk=pk)
    manutencoes = viatura.manutencoes.all()
    alerta = viatura.get_alerta_manutencao()

    # Últimos registros de movimentação
    ultimos_usos = viatura.registros_uso.select_related("ficha").order_by("-ficha__data_expediente", "-horario_saida")[:10]

    return render(request, "veiculos/detalhe.html", {
        "viatura": viatura,
        "manutencoes": manutencoes,
        "alerta": alerta,
        "ultimos_usos": ultimos_usos,
    })


@login_required
def manutencao_criar(request, viatura_pk):
    viatura = get_object_or_404(Viatura, pk=viatura_pk)

    if request.method == "POST":
        form = ManutencaoForm(request.POST)
        if form.is_valid():
            manutencao = form.save(commit=False)
            manutencao.viatura = viatura
            manutencao.registrado_por = request.user
            manutencao.save()

            messages.success(request, f"Manutenção registrada com sucesso para a viatura {viatura.placa}.")
            return redirect("veiculos:detalhe", pk=viatura.pk)
    else:
        # Preenche com odômetro atual da viatura como sugestão
        form = ManutencaoForm(initial={"km_no_momento": viatura.km_atual})

    return render(request, "veiculos/form_manutencao.html", {
        "form": form,
        "viatura": viatura,
    })


@login_required
def manutencao_lista(request):
    manutencoes = Manutencao.objects.select_related("viatura", "registrado_por").order_by("-data_manutencao")
    return render(request, "veiculos/lista_manutencoes.html", {
        "manutencoes": manutencoes,
    })


@login_required
def exportar_viaturas_pdf(request):
    viaturas = Viatura.objects.filter(ativo=True).select_related("setor_pertencente", "responsavel_pessoa")
    pdf_bytes = gerar_pdf_viaturas(viaturas)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Relatorio_Viaturas_PF_{date.today().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
def exportar_viaturas_excel(request):
    viaturas = Viatura.objects.filter(ativo=True).select_related("setor_pertencente", "responsavel_pessoa")
    excel_bytes = gerar_excel_viaturas(viaturas)
    response = HttpResponse(excel_bytes, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="Relatorio_Viaturas_PF_{date.today().strftime("%Y%m%d")}.xlsx"'
    return response


@login_required
def exportar_manutencoes_pdf(request, pk):
    viatura = get_object_or_404(Viatura, pk=pk)
    manutencoes = viatura.manutencoes.all()
    pdf_bytes = gerar_pdf_manutencoes_viatura(viatura, manutencoes)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Manutencao_{viatura.placa}_{date.today().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
def exportar_manutencoes_excel(request, pk):
    viatura = get_object_or_404(Viatura, pk=pk)
    manutencoes = viatura.manutencoes.all()
    excel_bytes = gerar_excel_manutencoes(viatura, manutencoes)
    response = HttpResponse(excel_bytes, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="Manutencao_{viatura.placa}_{date.today().strftime("%Y%m%d")}.xlsx"'
    return response
