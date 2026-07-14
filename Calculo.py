# -*- coding: utf-8 -*-
"""Calculadora de Inatividade

Adaptado do script original (gerado a partir do Colab) para uma
função reutilizável, chamada pelo App.py (Flask).

As fórmulas de cálculo são exatamente as mesmas do script original;
apenas foram organizadas dentro de uma função que recebe os dados
do formulário e devolve os resultados em um dicionário.
"""

from datetime import date, timedelta

# ================== CONSTANTES ==================

TEMPO_TOTAL_MASC = 10950
TEMPO_TOTAL_FEM = 9125
TEMPO_TOTAL_MILITAR = 9125

DATA_BASE_GERAL = date(2019, 12, 31)
DATA_BASE_GERAL_2 = date(2020, 1, 1)
DATA_BASE_MILITAR = date(2022, 1, 1)

TABELA_ACRESCIMO = {
    2021: 0,
    2022: 120,
    2023: 240,
    2024: 365,
    2025: 485,
    2026: 605,
    2027: 730,
    2028: 850,
    2029: 970,
    2030: 1095,
    2031: 1215,
    2032: 1335,
    2033: 1460,
    2034: 1580,
    2035: 1700,
    2036: 1825,  # teto máximo
}


# ================== FUNÇÃO PRINCIPAL ==================

def calcular(
    sexo,
    tempo_bruto_geral_2019,
    tempo_bruto_militar_2019,
    desconto_le_2017,
    desconto_le_2019,
    tempo_privado_2019,
    tempo_militar_2019,
):
    """Recebe os dados do militar e devolve um dicionário com o
    resultado do tempo geral e do tempo militar, incluindo as datas
    estimadas de conclusão da inatividade.
    """

    sexo = (sexo or "").upper().strip()

    # ================ CONDICIONAL IF MASC OU FEM ==================
    if sexo == "M":
        tempo_total = TEMPO_TOTAL_MASC
    elif sexo == "F":
        tempo_total = TEMPO_TOTAL_FEM
    else:
        raise ValueError("Sexo inválido! Selecione Masculino ou Feminino.")

    # ================== CÁLCULO TEMPO GERAL ==================
    tempo_final_2019 = (
        tempo_bruto_geral_2019 - desconto_le_2019 - tempo_privado_2019 - tempo_militar_2019
    )  # Tempo final em 2019

    faltava_sem_acrescimo = tempo_total - tempo_final_2019  # Faltava depois de 2019 sem acréscimo

    data_completou_sem_acrescimo = DATA_BASE_GERAL_2 + timedelta(days=faltava_sem_acrescimo)

    acresimo_17 = int(faltava_sem_acrescimo * 0.17)  # 17% do que faltava

    faltava_com_acrescimo = (
        faltava_sem_acrescimo + acresimo_17 - tempo_militar_2019 - tempo_privado_2019 - desconto_le_2019
    )

    data_completou_com_acrescimo = DATA_BASE_GERAL_2 + timedelta(days=faltava_com_acrescimo)

    # ================== CÁLCULO TEMPO MILITAR ==================
    tempo_final_2019_militar = tempo_bruto_militar_2019 - desconto_le_2017 - tempo_militar_2019

    tempo_militar_2021 = tempo_final_2019_militar + 731

    falta_tempo = TEMPO_TOTAL_MILITAR - tempo_militar_2021 - tempo_militar_2019

    data_completou_sem_acrescimo_militar = (
        DATA_BASE_MILITAR + timedelta(days=falta_tempo) - timedelta(days=tempo_militar_2019)
    )

    # ================== CÁLCULO ACRÉSCIMO MILITAR ==================
    ano_referencia = max(
        data_completou_com_acrescimo.year,
        data_completou_sem_acrescimo_militar.year,
    )

    acrescimo = 0
    data_final = data_completou_sem_acrescimo_militar

    while True:
        # pega o pedágio da tabela
        if ano_referencia >= 2036:
            acrescimo = 1825
        else:
            acrescimo = TABELA_ACRESCIMO.get(ano_referencia, 0)

        # soma o pedágio na data que completaria sem pedágio
        data_final = data_completou_sem_acrescimo_militar + timedelta(days=acrescimo)

        # pega o maior ano entre geral e militar
        novo_ano = max(data_final.year, data_completou_com_acrescimo.year)

        # se estabilizou, para o loop
        if novo_ano == ano_referencia:
            break

        # senão recalcula
        ano_referencia = novo_ano

    # ================== RESULTADO ==================
    return {
        "geral": {
            "tempo_final_2019": tempo_final_2019,
            "faltava_sem_acrescimo": faltava_sem_acrescimo,
            "data_sem_acrescimo": data_completou_sem_acrescimo,
            "acrescimo_17": acresimo_17,
            "data_final": data_completou_com_acrescimo,
        },
        "militar": {
            "tempo_final_2019": tempo_final_2019_militar,
            "tempo_2021": tempo_militar_2021,
            "falta_tempo": falta_tempo,
            "acrescimo_aplicado": acrescimo,
            "data_final": data_final,
        },
    }
