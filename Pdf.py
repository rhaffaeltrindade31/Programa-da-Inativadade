# -*- coding: utf-8 -*-
"""Geração do PDF da ficha de cálculo de inatividade.

Usa o cabeçalho oficial (brasão do Estado do Rio Grande do Sul /
Brigada Militar) no topo da página e, abaixo, os dados informados
e o resultado do cálculo (tempo geral e tempo militar).
"""

import io
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
)

CABECALHO_PATH = os.path.join(os.path.dirname(__file__), "static", "cabecalho-brigada.png")

COR_INK = colors.HexColor("#1b2430")
COR_OLIVE = colors.HexColor("#5d6b45")
COR_LINHA = colors.HexColor("#d8d5c9")


def numero_br(valor):
    """Formata um inteiro com separador de milhar no padrão brasileiro."""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(valor)


def _linha_ficha(rotulo, valor):
    return [
        Paragraph(rotulo, _estilo_rotulo()),
        Paragraph(valor, _estilo_valor()),
    ]


_styles_cache = {}


def _estilo_rotulo():
    if "rotulo" not in _styles_cache:
        _styles_cache["rotulo"] = ParagraphStyle(
            "rotulo", fontName="Helvetica", fontSize=9.5, textColor=COR_INK,
        )
    return _styles_cache["rotulo"]


def _estilo_valor():
    if "valor" not in _styles_cache:
        _styles_cache["valor"] = ParagraphStyle(
            "valor", fontName="Courier-Bold", fontSize=9.5, textColor=COR_INK,
            alignment=2,  # direita
        )
    return _styles_cache["valor"]


def _tabela_ficha(linhas, destacar_ultima=True):
    tabela = Table(linhas, colWidths=[9.5 * cm, 6.5 * cm])
    estilo = [
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.6, COR_LINHA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    if destacar_ultima:
        estilo += [
            ("LINEABOVE", (0, -1), (-1, -1), 1.1, COR_INK),
            ("FONTNAME", (0, -1), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, -1), (1, -1), "Courier-Bold"),
        ]
    tabela.setStyle(TableStyle(estilo))
    return tabela


def gerar_pdf(dados_form, resultado):
    """Gera o PDF em memória (BytesIO) com o cabeçalho oficial e o
    resultado do cálculo, e devolve o buffer pronto para envio.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.4 * cm,
        bottomMargin=1.6 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title="Ficha de Cálculo de Inatividade",
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "titulo", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=14, textColor=COR_INK, spaceAfter=2, alignment=1,
    )
    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"], fontName="Helvetica", fontSize=9,
        textColor=colors.HexColor("#4a5568"), alignment=1, spaceAfter=10,
    )
    secao_style = ParagraphStyle(
        "secao", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=11.5, textColor=COR_OLIVE, spaceBefore=14, spaceAfter=6,
    )
    rodape_style = ParagraphStyle(
        "rodape", parent=styles["Normal"], fontName="Helvetica-Oblique",
        fontSize=8, textColor=colors.HexColor("#6b7280"), alignment=1,
        spaceBefore=18,
    )

    story = []

    # ---------- Cabeçalho oficial ----------
    if os.path.exists(CABECALHO_PATH):
        img = Image(CABECALHO_PATH)
        largura_max = 11 * cm
        proporcao = img.imageHeight / float(img.imageWidth)
        img.drawWidth = largura_max
        img.drawHeight = largura_max * proporcao
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=0.8, color=COR_LINHA))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Ficha de Cálculo de Inatividade", titulo_style))
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"Documento gerado em {agora} · Regra de transição EC 103/2019", sub_style))

    # ---------- Dados informados ----------
    sexo_extenso = {"M": "Masculino", "F": "Feminino"}.get(dados_form.get("sexo", ""), "—")
    dados_linhas = [
        _linha_ficha("Sexo", sexo_extenso),
        _linha_ficha("Tempo bruto geral em 31/12/2019", f"{numero_br(dados_form.get('tempo_bruto_geral_2019', 0))} dias"),
        _linha_ficha("Tempo bruto militar em 31/12/2019", f"{numero_br(dados_form.get('tempo_bruto_militar_2019', 0))} dias"),
        _linha_ficha("Licença especial convertida (após 24/07/2017)", f"{numero_br(dados_form.get('desconto_le_2017', 0))} dias"),
        _linha_ficha("Licença especial convertida (após 31/12/2019)", f"{numero_br(dados_form.get('desconto_le_2019', 0))} dias"),
        _linha_ficha("Tempo privado averbado após 2019", f"{numero_br(dados_form.get('tempo_privado_2019', 0))} dias"),
        _linha_ficha("Tempo militar averbado após 2019", f"{numero_br(dados_form.get('tempo_militar_2019', 0))} dias"),
    ]
    story.append(Paragraph("Dados informados", secao_style))
    story.append(_tabela_ficha(dados_linhas, destacar_ultima=False))

    # ---------- Tempo geral ----------
    geral = resultado["geral"]
    faltava = (
        f"{numero_br(geral['faltava_sem_acrescimo'])} dias"
        if geral["faltava_sem_acrescimo"] > 0
        else "Tempo já cumprido"
    )
    linhas_geral = [
        _linha_ficha("Tempo apurado em 2019", f"{numero_br(geral['tempo_final_2019'])} dias"),
        _linha_ficha("Faltava sem acréscimo", faltava),
        _linha_ficha("Data sem acréscimo", geral["data_sem_acrescimo"].strftime("%d/%m/%Y")),
        _linha_ficha("Acréscimo (pedágio 17%)", f"{numero_br(geral['acrescimo_17'])} dias"),
        _linha_ficha("Data final estimada", geral["data_final"].strftime("%d/%m/%Y")),
    ]
    story.append(Paragraph("Tempo geral", secao_style))
    story.append(_tabela_ficha(linhas_geral))

    # ---------- Tempo militar ----------
    militar = resultado["militar"]
    falta_militar = (
        f"{numero_br(militar['falta_tempo'])} dias"
        if militar["falta_tempo"] > 0
        else "Tempo já cumprido"
    )
    linhas_militar = [
        _linha_ficha("Tempo apurado em 2019", f"{numero_br(militar['tempo_final_2019'])} dias"),
        _linha_ficha("Tempo em 31/12/2021", f"{numero_br(militar['tempo_2021'])} dias"),
        _linha_ficha("Falta de tempo", falta_militar),
        _linha_ficha("Acréscimo aplicado", f"{numero_br(militar['acrescimo_aplicado'])} dias"),
        _linha_ficha("Data final estimada", militar["data_final"].strftime("%d/%m/%Y")),
    ]
    story.append(Paragraph("Tempo militar", secao_style))
    story.append(_tabela_ficha(linhas_militar))

    # ---------- Rodapé ----------
    story.append(Paragraph(
        "Ferramenta de simulação — modelo inicial ainda em testes. "
        "Os resultados não substituem a análise oficial do órgão competente.",
        rodape_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
