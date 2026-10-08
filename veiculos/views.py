import time
from datetime import date

from django.contrib import messages
from django.db.models import Count, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accesscontrol.decorators import requer_permissao
from services.consulta_placa import consultar_placa
from services.relatorios_excel import gerar_excel_manutencoes, gerar_excel_viaturas
from services.relatorios_pdf import gerar_pdf_manutencoes_viatura, gerar_pdf_viaturas

from .forms import (
    ClassificacaoViaturaForm,
    ConfiguracaoConsultaPlacaForm,
    ManutencaoForm,
    ViaturaForm,
)
from .models import ConfiguracaoConsultaPlaca, Manutencao, PlacaConsultada, Setor, Viatura


@requer_permissao("frota.viaturas.visualizar")
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


@requer_permissao("frota.viaturas.criar")
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


@requer_permissao("frota.viaturas.editar")
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


@requer_permissao("frota.viaturas.visualizar")
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


@requer_permissao("frota.manutencao.criar")
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


@requer_permissao("frota.manutencao.visualizar")
def manutencao_lista(request):
    manutencoes = Manutencao.objects.select_related("viatura", "registrado_por").order_by("-data_manutencao")
    return render(request, "veiculos/lista_manutencoes.html", {
        "manutencoes": manutencoes,
    })


@requer_permissao("frota.viaturas.visualizar")
def exportar_viaturas_pdf(request):
    viaturas = Viatura.objects.filter(ativo=True).select_related("setor_pertencente", "responsavel_pessoa")
    pdf_bytes = gerar_pdf_viaturas(viaturas)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Relatorio_Viaturas_PF_{date.today().strftime("%Y%m%d")}.pdf"'
    return response


@requer_permissao("frota.viaturas.visualizar")
def exportar_viaturas_excel(request):
    viaturas = Viatura.objects.filter(ativo=True).select_related("setor_pertencente", "responsavel_pessoa")
    excel_bytes = gerar_excel_viaturas(viaturas)
    response = HttpResponse(excel_bytes, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="Relatorio_Viaturas_PF_{date.today().strftime("%Y%m%d")}.xlsx"'
    return response


@requer_permissao("frota.manutencao.visualizar")
def exportar_manutencoes_pdf(request, pk):
    viatura = get_object_or_404(Viatura, pk=pk)
    manutencoes = viatura.manutencoes.all()
    pdf_bytes = gerar_pdf_manutencoes_viatura(viatura, manutencoes)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Manutencao_{viatura.placa}_{date.today().strftime("%Y%m%d")}.pdf"'
    return response


@requer_permissao("frota.manutencao.visualizar")
def exportar_manutencoes_excel(request, pk):
    viatura = get_object_or_404(Viatura, pk=pk)
    manutencoes = viatura.manutencoes.all()
    excel_bytes = gerar_excel_manutencoes(viatura, manutencoes)
    response = HttpResponse(excel_bytes, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="Manutencao_{viatura.placa}_{date.today().strftime("%Y%m%d")}.xlsx"'
    return response


@requer_permissao("frota.viaturas.visualizar")
def classificacao_lista(request):
    """
    Tela do NUTRAN para identificação e classificação de veículos a partir dos
    registros de entrada e saída da portaria. Permite definir se o veículo pertence
    à frota oficial ou se é veículo externo, atribuindo setor e responsável.
    """
    termo = request.GET.get("q", "").strip()
    classificacao_filtro = request.GET.get("classificacao", "").strip()

    viaturas = Viatura.objects.annotate(
        total_usos=Count("registros_uso"),
        ultimo_uso_data=Max("registros_uso__ficha__data_expediente"),
    ).select_related("setor_pertencente", "classificado_por")

    if termo:
        viaturas = viaturas.filter(
            placa__icontains=termo
        ) | viaturas.filter(
            modelo__icontains=termo
        ) | viaturas.filter(
            marca__icontains=termo
        )

    if classificacao_filtro:
        viaturas = viaturas.filter(classificacao=classificacao_filtro)

    # Ordenação: pendentes primeiro, depois por placa
    viaturas = viaturas.order_by("-classificacao", "-total_usos", "placa")

    # Contadores rápidos
    total_veiculos = Viatura.objects.count()
    total_pendentes = Viatura.objects.filter(classificacao=Viatura.CLASSIFICACAO_PENDENTE).count()
    total_frota = Viatura.objects.filter(classificacao=Viatura.CLASSIFICACAO_FROTA).count()
    total_externos = Viatura.objects.filter(classificacao=Viatura.CLASSIFICACAO_EXTERNA).count()

    return render(request, "veiculos/classificacao_lista.html", {
        "viaturas": viaturas,
        "termo": termo,
        "classificacao_filtro": classificacao_filtro,
        "total_veiculos": total_veiculos,
        "total_pendentes": total_pendentes,
        "total_frota": total_frota,
        "total_externos": total_externos,
    })


@requer_permissao("frota.viaturas.editar")
def classificacao_definir(request, pk):
    """
    Processa a definição de classificação do veículo pelo NUTRAN.
    """
    viatura = get_object_or_404(Viatura, pk=pk)

    if request.method == "POST":
        form = ClassificacaoViaturaForm(request.POST, instance=viatura)
        if form.is_valid():
            v = form.save(commit=False)
            v.classificado_por = request.user
            v.classificado_em = timezone.now()
            v.save()

            messages.success(
                request,
                f"Veículo {v.placa} ({v.marca} {v.modelo}) classificado como "
                f"'{v.get_classificacao_display()}' com sucesso.",
            )
            return redirect("veiculos:classificacao_lista")
        else:
            messages.error(request, "Por favor, corrija as pendências no formulário.")
    else:
        form = ClassificacaoViaturaForm(instance=viatura)

    # Histórico de usos deste veículo
    registros = viatura.registros_uso.select_related("ficha").order_by("-ficha__data_expediente", "-id")[:5]

    return render(request, "veiculos/classificacao_form.html", {
        "form": form,
        "viatura": viatura,
        "registros": registros,
    })


@requer_permissao("usuarios.cadastro.visualizar")
def configuracao_placa_view(request):
    """
    Interface gráfica para o Administrador configurar a integração de consulta
    de placas, escolhendo entre a API Gratuita e a API oficial SERPRO / SENATRAN,
    além de definir o proxy institucional corporativo.
    """
    config = ConfiguracaoConsultaPlaca.obter_configuracao()

    if request.method == "POST":
        form = ConfiguracaoConsultaPlacaForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Parâmetros de integração da consulta de placas atualizados com sucesso.")
            return redirect("veiculos:configuracao_placa")
        else:
            messages.error(request, "Por favor, verifique os campos destacados.")
    else:
        form = ConfiguracaoConsultaPlacaForm(instance=config)

    total_cache = PlacaConsultada.objects.count()
    ultimas_consultadas = PlacaConsultada.objects.order_by("-consultado_em")[:8]

    return render(request, "veiculos/configuracao_placa.html", {
        "form": form,
        "config": config,
        "total_cache": total_cache,
        "ultimas_consultadas": ultimas_consultadas,
    })


@requer_permissao("usuarios.cadastro.visualizar")
def configuracao_placa_testar(request):
    """
    Endpoint AJAX para teste em tempo real da consulta de placa contra a API configurada.
    """
    placa = request.GET.get("placa", "").strip()
    if not placa:
        return JsonResponse({"sucesso": False, "mensagem": "Informe uma placa para teste."})

    inicio = time.time()
    resultado = consultar_placa(placa, forcar_api=True)
    duracao_ms = int((time.time() - inicio) * 1000)

    dados = resultado.to_dict()
    dados["tempo_resposta_ms"] = duracao_ms
    return JsonResponse(dados)

