import io
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

if TYPE_CHECKING:
    from fichas.models import FichaControle
    from veiculos.models import Manutencao, Viatura

# Paleta Frontline PF
PF_BLACK = colors.HexColor("#111213")
PF_GOLD = colors.HexColor("#E1AD62")
PF_BLUE = colors.HexColor("#3363CC")
PF_GREY_TEXT = colors.HexColor("#41434E")
PF_GREY_LIGHT = colors.HexColor("#F4F6F8")
PF_GREY_BORDER = colors.HexColor("#DADADD")


def get_brasao_image(width: int = 50, height: int = 60) -> Image | None:
    brasao_path: Path = Path(settings.BASE_DIR) / "static" / "img" / "brasao_pf.png"
    if brasao_path.is_file():
        return Image(str(brasao_path), width=width, height=height)
    return None



def cabecalho_institucional(
    titulo_documento: str,
    subtitulo: str = "SISTEMA DE CONTROLE DE ENTRADA E SAÍDA DE VIATURAS",
) -> Table:
    brasao = get_brasao_image()
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=PF_BLACK,
        alignment=1
    )
    sub_style = ParagraphStyle(
        "HeaderSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=PF_GREY_TEXT,
        alignment=1
    )
    doc_title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=PF_BLUE,
        alignment=1
    )

    col_text = [
        Paragraph("<b>MINISTÉRIO DA JUSTIÇA E SEGURANÇA PÚBLICA</b>", titulo_style),
        Paragraph("<b>DEPARTAMENTO DE POLÍCIA FEDERAL</b>", titulo_style),
        Paragraph(subtitulo, sub_style),
        Spacer(1, 4),
        Paragraph(f"<b>{titulo_documento.upper()}</b>", doc_title_style),
    ]

    header_data = [[brasao, col_text]] if brasao else [[col_text]]
    col_widths = [60, None] if brasao else [None]

    header_table = Table(header_data, colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return header_table


def gerar_pdf_ficha(ficha: "FichaControle") -> bytes:
    """
    Gera o PDF oficial da Ficha Diária de Controle de Viaturas (formato paisagem).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )
    elements = []
    styles = getSampleStyleSheet()

    # Cabeçalho Institucional
    elements.append(cabecalho_institucional(f"FICHA DIÁRIA DE CONTROLE DE VIATURAS — {ficha.data_expediente.strftime('%d/%m/%Y')}"))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=PF_GOLD, spaceBefore=6, spaceAfter=8))

    # Dados do Expediente
    dados_expediente = [
        [
            Paragraph(f"<b>Data do Expediente:</b> {ficha.data_expediente.strftime('%d/%m/%Y')}", styles["Normal"]),
            Paragraph(f"<b>Horário Início:</b> {ficha.horario_inicio.strftime('%H:%M')}", styles["Normal"]),
            Paragraph(f"<b>Horário Término:</b> {ficha.horario_termino.strftime('%H:%M')}", styles["Normal"]),
            Paragraph(f"<b>Vigilante do Dia:</b> {ficha.nome_vigilante}", styles["Normal"]),
            Paragraph(f"<b>Status:</b> {ficha.get_status_display().upper()}", styles["Normal"]),
        ]
    ]
    t_expediente = Table(dados_expediente, colWidths=[140, 110, 110, 240, 150])
    t_expediente.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PF_GREY_LIGHT),
        ("BOX", (0, 0), (-1, -1), 1, PF_GREY_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_expediente)
    elements.append(Spacer(1, 10))

    # Tabela de Movimentações
    headers = [
        Paragraph("<b>Viatura / Placa</b>", styles["Normal"]),
        Paragraph("<b>Condutor</b>", styles["Normal"]),
        Paragraph("<b>Destino / Missão</b>", styles["Normal"]),
        Paragraph("<b>Saída (H/KM)</b>", styles["Normal"]),
        Paragraph("<b>Chegada (H/KM)</b>", styles["Normal"]),
        Paragraph("<b>KM Perc.</b>", styles["Normal"]),
        Paragraph("<b>Avarias / Obs</b>", styles["Normal"]),
    ]

    tabela_data = [headers]

    for reg in ficha.registros.all():
        saida_txt = f"{reg.horario_saida.strftime('%H:%M')}<br/>{reg.odometro_saida:,} km"
        chegada_txt = f"{reg.horario_chegada.strftime('%H:%M')}<br/>{reg.odometro_chegada:,} km" if reg.horario_chegada and reg.odometro_chegada else "EM TRÂNSITO"
        km_txt = f"{reg.km_percorrido:,} km" if reg.odometro_chegada else "-"
        avarias_txt = f"<b>SIM:</b> {reg.avarias_encontradas}" if reg.possui_avarias else "Não"

        tabela_data.append([
            Paragraph(f"<b>{reg.viatura.modelo}</b><br/>{reg.viatura.placa}", styles["Normal"]),
            Paragraph(reg.condutor, styles["Normal"]),
            Paragraph(reg.destino, styles["Normal"]),
            Paragraph(saida_txt, styles["Normal"]),
            Paragraph(chegada_txt, styles["Normal"]),
            Paragraph(km_txt, styles["Normal"]),
            Paragraph(avarias_txt, styles["Normal"]),
        ])

    if len(tabela_data) == 1:
        tabela_data.append([Paragraph("<i>Nenhum registro de saída lançado nesta ficha.</i>", styles["Normal"])] * 7)

    table_mov = Table(tabela_data, colWidths=[120, 130, 140, 95, 95, 70, 100])
    table_mov.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PF_BLACK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, PF_GREY_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PF_GREY_LIGHT]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table_mov)
    elements.append(Spacer(1, 20))

    # Área de Vistos e Assinaturas (3 Colunas)
    visto_resp_txt = "<b>VISTO DO RESPONSÁVEL:</b><br/>"
    if ficha.visto_responsavel and ficha.responsavel_visto_usuario:
        visto_resp_txt += f"Assinado digitalmente por {ficha.responsavel_visto_usuario.get_full_name() or ficha.responsavel_visto_usuario.username}<br/>"
        visto_resp_txt += f"Data: {ficha.data_visto_responsavel.strftime('%d/%m/%Y %H:%M') if ficha.data_visto_responsavel else '-'}"
    else:
        visto_resp_txt += "<br/>___________________________<br/>Assinatura / Visto"

    visto_chefia_txt = "<b>VISTO DA CHEFIA:</b><br/>"
    if ficha.visto_chefia and ficha.chefia_visto_usuario:
        visto_chefia_txt += f"Assinado digitalmente por {ficha.chefia_visto_usuario.get_full_name() or ficha.chefia_visto_usuario.username}<br/>"
        visto_chefia_txt += f"Data: {ficha.data_visto_chefia.strftime('%d/%m/%Y %H:%M') if ficha.data_visto_chefia else '-'}"
    else:
        visto_chefia_txt += "<br/>___________________________<br/>Assinatura / Visto"

    vigilante_txt = f"<b>VIGILANTE DO DIA:</b><br/>{ficha.nome_vigilante}<br/>"
    vigilante_txt += "<br/>___________________________<br/>Assinatura"

    assinaturas_data = [
        [
            Paragraph(vigilante_txt, styles["Normal"]),
            Paragraph(visto_resp_txt, styles["Normal"]),
            Paragraph(visto_chefia_txt, styles["Normal"]),
        ]
    ]

    t_assinaturas = Table(assinaturas_data, colWidths=[250, 250, 250])
    t_assinaturas.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, PF_GREY_BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(KeepTogether([t_assinaturas]))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def gerar_pdf_viaturas(viaturas: Iterable["Viatura"]) -> bytes:
    """
    Gera o Relatório Geral da Frota de Viaturas.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )
    elements = []
    styles = getSampleStyleSheet()

    elements.append(cabecalho_institucional("RELATÓRIO GERAL DA FROTA DE VIATURAS"))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=PF_GOLD, spaceBefore=6, spaceAfter=10))

    headers = [
        Paragraph("<b>Viatura</b>", styles["Normal"]),
        Paragraph("<b>Placa</b>", styles["Normal"]),
        Paragraph("<b>Tipo</b>", styles["Normal"]),
        Paragraph("<b>Setor Pertencente</b>", styles["Normal"]),
        Paragraph("<b>Responsável</b>", styles["Normal"]),
        Paragraph("<b>Odômetro Atual</b>", styles["Normal"]),
        Paragraph("<b>Próx. Revisão (KM/Data)</b>", styles["Normal"]),
        Paragraph("<b>Estado</b>", styles["Normal"]),
    ]

    tabela_data = [headers]
    for v in viaturas:
        proxima = []
        if v.proxima_manutencao_km:
            proxima.append(f"{v.proxima_manutencao_km:,} km")
        if v.proxima_manutencao_data:
            proxima.append(v.proxima_manutencao_data.strftime("%d/%m/%Y"))
        proxima_txt = " / ".join(proxima) if proxima else "Não agendada"

        tabela_data.append([
            Paragraph(f"<b>{v.marca} {v.modelo}</b><br/>{v.ano_modelo} - {v.cor}", styles["Normal"]),
            Paragraph(f"<b>{v.placa}</b>", styles["Normal"]),
            Paragraph(v.get_tipo_display(), styles["Normal"]),
            Paragraph(v.setor_pertencente.sigla, styles["Normal"]),
            Paragraph(v.identificacao_responsavel, styles["Normal"]),
            Paragraph(f"{v.km_atual:,} km", styles["Normal"]),
            Paragraph(proxima_txt, styles["Normal"]),
            Paragraph(v.get_status_display(), styles["Normal"]),
        ])

    table = Table(tabela_data, colWidths=[140, 80, 110, 100, 110, 80, 100, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PF_BLACK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, PF_GREY_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PF_GREY_LIGHT]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def gerar_pdf_manutencoes_viatura(
    viatura: "Viatura",
    manutencoes: Iterable["Manutencao"],
) -> bytes:
    """
    Gera o Relatório Individual de Viatura com Histórico Completo de Manutenções.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    elements = []
    styles = getSampleStyleSheet()

    elements.append(cabecalho_institucional(f"HISTÓRICO DE MANUTENÇÃO — VIATURA {viatura.placa}"))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=PF_GOLD, spaceBefore=6, spaceAfter=10))

    # Ficha técnica da viatura
    ficha_data = [
        [
            Paragraph(f"<b>Veículo:</b> {viatura.marca} {viatura.modelo}", styles["Normal"]),
            Paragraph(f"<b>Placa:</b> {viatura.placa}", styles["Normal"]),
            Paragraph(f"<b>Ano/Modelo:</b> {viatura.ano_fabricacao}/{viatura.ano_modelo}", styles["Normal"]),
        ],
        [
            Paragraph(f"<b>Setor:</b> {viatura.setor_pertencente.sigla}", styles["Normal"]),
            Paragraph(f"<b>Odômetro Atual:</b> {viatura.km_atual:,} km", styles["Normal"]),
            Paragraph(f"<b>Status:</b> {viatura.get_status_display()}", styles["Normal"]),
        ]
    ]
    t_ficha = Table(ficha_data, colWidths=[200, 170, 180])
    t_ficha.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PF_GREY_LIGHT),
        ("BOX", (0, 0), (-1, -1), 1, PF_GREY_BORDER),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_ficha)
    elements.append(Spacer(1, 15))

    headers = [
        Paragraph("<b>Data</b>", styles["Normal"]),
        Paragraph("<b>Tipo</b>", styles["Normal"]),
        Paragraph("<b>Odômetro</b>", styles["Normal"]),
        Paragraph("<b>Oficina / OS</b>", styles["Normal"]),
        Paragraph("<b>Descrição / Peças</b>", styles["Normal"]),
        Paragraph("<b>Valor (R$)</b>", styles["Normal"]),
    ]

    tabela_data = [headers]
    total_gasto = 0

    for m in manutencoes:
        total_gasto += float(m.valor_total)
        desc = f"<b>{m.descricao_servico}</b>"
        if m.pecas_substituidas:
            desc += f"<br/><font size=8 color='#555868'>Peças: {m.pecas_substituidas}</font>"

        tabela_data.append([
            Paragraph(m.data_manutencao.strftime("%d/%m/%Y"), styles["Normal"]),
            Paragraph(m.get_tipo_display(), styles["Normal"]),
            Paragraph(f"{m.km_no_momento:,} km", styles["Normal"]),
            Paragraph(f"{m.fornecedor_oficina}<br/><font size=8>OS: {m.numero_ordem_servico or '-'}</font>", styles["Normal"]),
            Paragraph(desc, styles["Normal"]),
            Paragraph(f"R$ {m.valor_total:,.2f}", styles["Normal"]),
        ])

    if len(tabela_data) == 1:
        tabela_data.append([Paragraph("<i>Nenhum registro de manutenção encontrado para este veículo.</i>", styles["Normal"])] * 6)

    table = Table(tabela_data, colWidths=[70, 95, 75, 110, 130, 70])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PF_BLACK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, PF_GREY_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PF_GREY_LIGHT]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"<b>Investimento Total em Manutenções:</b> R$ {total_gasto:,.2f}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
