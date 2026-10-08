from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accesscontrol.decorators import requer_permissao
from services.consulta_placa import consultar_placa, normalizar_placa
from services.relatorios_excel import gerar_excel_ficha
from services.relatorios_pdf import gerar_pdf_ficha
from veiculos.models import Viatura

from .forms import (
    FichaControleForm,
    RegistroChegadaAvulsaForm,
    RegistroChegadaForm,
    RegistroEdicaoForm,
    RegistroMovimentacaoForm,
    RegistroSaidaForm,
)

from .models import FichaControle, RegistroUso


@requer_permissao("operacao_diaria.fichas.visualizar")
def ficha_lista(request):
    data_filtro = request.GET.get("data", "").strip()
    status_filtro = request.GET.get("status", "").strip()

    fichas = FichaControle.objects.select_related("vigilante", "vigilante_assinatura_usuario", "responsavel_visto_usuario", "chefia_visto_usuario").order_by("-data_expediente", "-horario_inicio")

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
            messages.error(request, "Por favor, corrija os erros apontados no formulário.")
    else:
        from datetime import time
        hora_atual = timezone.localtime().time()
        turno_padrao = "NOTURNO" if (hora_atual >= time(19, 0) or hora_atual < time(7, 0)) else "DIURNO"

        initial = {
            "nome_vigilante": request.user.get_full_name() or request.user.username,
            "data_expediente": date.today(),
            "turno": turno_padrao,
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
            "vigilante", "vigilante_assinatura_usuario", "responsavel_visto_usuario", "chefia_visto_usuario", "encerrada_por"
        ),
        pk=pk
    )
    registros = ficha.registros.select_related("viatura", "condutor_usuario", "registro_saida_origem__ficha").all()

    # Estatísticas da ficha
    total_saidas = registros.filter(horario_saida__isnull=False).count()
    total_chegadas = registros.filter(horario_chegada__isnull=False).count()
    em_transito = registros.filter(status=RegistroUso.STATUS_EM_TRANSITO, horario_saida__isnull=False).count()
    concluidos = registros.filter(status=RegistroUso.STATUS_CONCLUIDO).count()
    total_km_dia = sum(r.km_percorrido for r in registros)

    # Lista de viaturas disponíveis para novo registro de saída
    viaturas_disponiveis = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_DISPONIVEL)
    # Quantidade de viaturas em trânsito (na rua) que podem ter retorno registrado
    viaturas_em_transito_count = Viatura.objects.filter(ativo=True, status=Viatura.STATUS_EM_USO).count()

    return render(request, "fichas/detalhe.html", {
        "ficha": ficha,
        "registros": registros,
        "total_saidas": total_saidas,
        "total_chegadas": total_chegadas,
        "em_transito": em_transito,
        "concluidos": concluidos,
        "total_km_dia": total_km_dia,
        "viaturas_disponiveis": viaturas_disponiveis,
        "viaturas_em_transito_count": viaturas_em_transito_count,
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


@requer_permissao("operacao_diaria.fichas.registrar_chegada")
def registro_chegada_avulsa_criar(request, ficha_pk):
    """
    Registra a chegada/retorno de uma viatura que saiu em outro plantão/ficha (ou nesta ficha).
    Gera um registro na ficha atual contendo exclusivamente a chegada, associando
    ao registro de saída original (caso existente) para cálculo de KM e fechamento de ciclo.
    """
    ficha = get_object_or_404(FichaControle, pk=ficha_pk)

    if not ficha.pode_editar:
        messages.error(request, "Esta ficha está ENCERRADA e não permite novos lançamentos de retorno de viaturas.")
        return redirect("fichas:detalhe", pk=ficha.pk)

    if request.method == "POST":
        form = RegistroChegadaAvulsaForm(request.POST)
        form.instance.ficha = ficha
        if form.is_valid():
            reg = form.save(commit=False)
            reg.ficha = ficha
            reg.registrado_por = request.user
            reg.tipo_movimentacao = RegistroUso.TIPO_CHEGADA
            reg.status = RegistroUso.STATUS_CONCLUIDO

            if not reg.registro_saida_origem and reg.viatura:
                reg.registro_saida_origem = RegistroUso.objects.filter(
                    viatura=reg.viatura,
                    status=RegistroUso.STATUS_EM_TRANSITO
                ).order_by("-data_saida", "-horario_saida", "-id").first()

            # Se vinculou a uma saída de origem e condutor não foi informado manualmente, herda da saída
            if reg.registro_saida_origem:
                if not reg.condutor and reg.registro_saida_origem.condutor:
                    reg.condutor = reg.registro_saida_origem.condutor
                if not reg.destino and reg.registro_saida_origem.destino:
                    reg.destino = reg.registro_saida_origem.destino

            reg.save()
            messages.success(
                request,
                f"Retorno da viatura {reg.viatura.placa} registrado com sucesso nesta ficha. "
                f"KM percorrido: {reg.km_percorrido:,} km."
            )
            return redirect("fichas:detalhe", pk=ficha.pk)
    else:
        viatura_id = request.GET.get("viatura_id")
        initial = {
            "data_chegada": date.today(),
            "horario_chegada": timezone.localtime().strftime("%H:%M"),
        }
        if viatura_id:
            viatura = Viatura.objects.filter(pk=viatura_id, ativo=True).first()
            if viatura:
                initial["viatura"] = viatura
                saida_origem = RegistroUso.objects.filter(
                    viatura=viatura,
                    status=RegistroUso.STATUS_EM_TRANSITO
                ).order_by("-data_saida", "-horario_saida").first()
                if saida_origem:
                    initial["registro_saida_origem"] = saida_origem
                    initial["odometro_chegada"] = saida_origem.odometro_saida
                    if saida_origem.condutor:
                        initial["condutor"] = saida_origem.condutor
                    initial["destino"] = saida_origem.destino

        form = RegistroChegadaAvulsaForm(initial=initial)

    # Mapa em JSON com metadados de cada viatura em uso para auto-preenchimento no front-end
    import json
    viaturas_map = {}
    for v in form.fields["viatura"].queryset:
        saida_aberta = RegistroUso.objects.filter(
            viatura=v,
            status=RegistroUso.STATUS_EM_TRANSITO
        ).select_related("ficha").order_by("-data_saida", "-horario_saida").first()

        if saida_aberta:
            viaturas_map[str(v.pk)] = {
                "saida_id": saida_aberta.pk,
                "ficha_origem": f"Ficha {saida_aberta.ficha.data_expediente.strftime('%d/%m/%Y')} (#{saida_aberta.ficha.pk})",
                "km_saida": saida_aberta.odometro_saida or v.km_atual,
                "data_saida": saida_aberta.data_saida.strftime("%d/%m/%Y") if saida_aberta.data_saida else "",
                "horario_saida": saida_aberta.horario_saida.strftime("%H:%M") if saida_aberta.horario_saida else "",
                "condutor": saida_aberta.condutor or "",
                "destino": saida_aberta.destino or "",
            }
        else:
            viaturas_map[str(v.pk)] = {
                "saida_id": "",
                "ficha_origem": "Sem registro de saída em aberto localizado",
                "km_saida": v.km_atual,
                "data_saida": "",
                "horario_saida": "",
                "condutor": "",
                "destino": "",
            }

    return render(request, "fichas/registro_chegada_avulsa_form.html", {
        "form": form,
        "ficha": ficha,
        "viaturas_map": json.dumps(viaturas_map),
    })


@login_required
def registro_movimentacao_criar(request, ficha_pk):
    """
    Interface unificada e inteligente para lançamento de Saída ou Retorno de viatura.
    Ao selecionar a viatura, a tela adapta dinamicamente os campos de acordo com
    o status do veículo (no pátio = Saída, na rua = Retorno).
    """
    from accesscontrol.services import tem_permissao
    from django.core.exceptions import PermissionDenied

    pode_saida = tem_permissao(request.user, "operacao_diaria.fichas.registrar_saida")
    pode_chegada = tem_permissao(request.user, "operacao_diaria.fichas.registrar_chegada")
    if not (pode_saida or pode_chegada):
        raise PermissionDenied("Você não possui permissão para registrar movimentações de viaturas.")

    ficha = get_object_or_404(FichaControle, pk=ficha_pk)

    if not ficha.pode_editar:
        messages.error(request, "Esta ficha está ENCERRADA e não permite novas movimentações de viaturas.")
        return redirect("fichas:detalhe", pk=ficha.pk)

    if request.method == "POST":
        form = RegistroMovimentacaoForm(request.POST, ficha=ficha)
        if form.is_valid():
            reg, tipo = form.save(ficha=ficha, usuario=request.user)
            if tipo == "SAIDA":
                messages.success(request, f"Saída da viatura {reg.viatura.placa} registrada com sucesso. Veículo em trânsito.")
            else:
                km = reg.km_percorrido or 0
                messages.success(request, f"Retorno da viatura {reg.viatura.placa} concluído com sucesso. KM percorrido: {km:,} km.")
            return redirect("fichas:detalhe", pk=ficha.pk)
        else:
            messages.error(request, "Por favor, verifique as pendências no formulário de movimentação.")
    else:
        viatura_id = request.GET.get("viatura_id")
        initial = {}
        if viatura_id:
            viatura = Viatura.objects.filter(pk=viatura_id, ativo=True).first()
            if viatura:
                initial["viatura"] = viatura
        form = RegistroMovimentacaoForm(initial=initial, ficha=ficha)

    import json
    viaturas = Viatura.objects.filter(ativo=True).order_by("status", "marca", "modelo")
    viaturas_map = {}
    for v in viaturas:
        saida_aberta = RegistroUso.objects.filter(
            viatura=v,
            status=RegistroUso.STATUS_EM_TRANSITO
        ).select_related("ficha").order_by("-data_saida", "-horario_saida", "-id").first()

        viaturas_map[str(v.pk)] = {
            "id": v.pk,
            "placa": v.placa,
            "modelo": f"{v.marca} {v.modelo}",
            "cor": v.cor or "",
            "status": v.status,  # "DISPONIVEL" ou "EM_USO"
            "km_atual": v.km_atual or 0,
            "saida_origem": {
                "id": saida_aberta.pk,
                "ficha_origem": f"Ficha {saida_aberta.ficha.data_expediente.strftime('%d/%m/%Y')} (#{saida_aberta.ficha.pk})",
                "ficha_data": saida_aberta.ficha.data_expediente.strftime("%d/%m/%Y"),
                "ficha_pk": saida_aberta.ficha.pk,
                "data_saida": saida_aberta.data_saida.strftime("%d/%m/%Y") if saida_aberta.data_saida else "",
                "data_saida_iso": saida_aberta.data_saida.strftime("%Y-%m-%d") if saida_aberta.data_saida else "",
                "horario_saida": saida_aberta.horario_saida.strftime("%H:%M") if saida_aberta.horario_saida else "",
                "odometro_saida": saida_aberta.odometro_saida or v.km_atual,
                "condutor": saida_aberta.condutor or "",
                "destino": saida_aberta.destino or "",
                "mesma_ficha": (saida_aberta.ficha_id == ficha.pk),
            } if saida_aberta else None
        }

    return render(request, "fichas/registro_movimentacao_form.html", {
        "form": form,
        "ficha": ficha,
        "viaturas_map": json.dumps(viaturas_map),
        "total_disponiveis": viaturas.filter(status=Viatura.STATUS_DISPONIVEL).count(),
        "total_em_transito": viaturas.filter(status=Viatura.STATUS_EM_USO).count(),
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
    registro = get_object_or_404(
        RegistroUso.objects.select_related("ficha", "viatura", "registro_saida_origem__ficha"),
        pk=pk
    )
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


@requer_permissao("operacao_diaria.fichas.assinar_vigilante")
def ficha_assinar_vigilante(request, pk):
    ficha = get_object_or_404(FichaControle, pk=pk)

    if not ficha.pode_editar:
        messages.warning(request, "Esta ficha já se encontra encerrada.")
        return redirect("fichas:detalhe", pk=ficha.pk)

    ficha.assinar_vigilante(request.user)
    messages.success(request, "Assinatura eletrônica do Vigilante aplicada com sucesso.")
    return redirect("fichas:detalhe", pk=ficha.pk)


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


@login_required
def api_consulta_placa(request):
    """
    Endpoint AJAX para consulta em tempo real da placa de um veículo.
    Retorna os dados cadastrais (marca, modelo, cor, procedência da frota ou API)
    e identifica se o veículo já se encontra em trânsito (na rua) para sugerir
    o fechamento automático do retorno.
    """
    placa_raw = request.GET.get("placa", "").strip()
    if not placa_raw:
        return JsonResponse({"sucesso": False, "mensagem": "Informe a placa do veículo."})

    placa_normalizada = normalizar_placa(placa_raw)
    resultado = consultar_placa(placa_normalizada)
    dados = resultado.to_dict()

    # Informações adicionais do banco local se a viatura existir
    viatura = Viatura.objects.filter(placa=placa_normalizada).first()
    if viatura:
        dados["viatura_id"] = viatura.pk
        dados["eh_frota"] = viatura.eh_frota
        dados["classificacao"] = viatura.classificacao
        dados["classificacao_display"] = viatura.get_classificacao_display()
        dados["status_viatura"] = viatura.status
        dados["km_atual"] = viatura.km_atual
        dados["setor"] = viatura.setor_pertencente.sigla if viatura.setor_pertencente else ""
        dados["responsavel"] = viatura.identificacao_responsavel
        if not dados["marca"]:
            dados["marca"] = viatura.marca
        if not dados["modelo"]:
            dados["modelo"] = viatura.modelo
    else:
        dados["viatura_id"] = None
        dados["eh_frota"] = False
        dados["classificacao"] = Viatura.CLASSIFICACAO_PENDENTE
        dados["classificacao_display"] = "Aguardando Classificação"
        dados["status_viatura"] = Viatura.STATUS_DISPONIVEL
        dados["km_atual"] = 0
        dados["setor"] = ""
        dados["responsavel"] = ""

    # Verifica se há saída em trânsito (na rua) para esta placa
    saida_aberta = RegistroUso.objects.filter(
        viatura__placa=placa_normalizada,
        status=RegistroUso.STATUS_EM_TRANSITO
    ).select_related("ficha").order_by("-data_saida", "-horario_saida", "-id").first()

    if saida_aberta:
        dados["em_transito"] = True
        dados["saida_origem_id"] = saida_aberta.pk
        dados["saida_pendente_id"] = saida_aberta.pk
        dados["ficha_origem"] = f"Ficha {saida_aberta.ficha.data_expediente.strftime('%d/%m/%Y')} (#{saida_aberta.ficha.pk})"
        dados["km_saida"] = saida_aberta.odometro_saida or dados["km_atual"]
        dados["data_saida"] = saida_aberta.data_saida.strftime("%Y-%m-%d") if saida_aberta.data_saida else ""
        dados["data_saida_display"] = saida_aberta.data_saida.strftime("%d/%m/%Y") if saida_aberta.data_saida else ""
        dados["horario_saida"] = saida_aberta.horario_saida.strftime("%H:%M") if saida_aberta.horario_saida else ""
        dados["condutor_saida"] = saida_aberta.condutor or ""
        dados["destino_saida"] = saida_aberta.destino or ""
    else:
        dados["em_transito"] = False
        dados["saida_origem_id"] = None
        dados["saida_pendente_id"] = None
        dados["km_saida"] = dados["km_atual"]

    return JsonResponse(dados)

