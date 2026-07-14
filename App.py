# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, send_file, redirect, url_for

from Calculo import calcular
from Pdf import gerar_pdf

app = Flask(__name__)


@app.template_filter("numero_br")
def numero_br(valor):
    """Formata um inteiro com separador de milhar no padrão brasileiro.
    Ex.: 8760 -> '8.760'. Números negativos mantêm o sinal: -366 -> '-366'.
    """
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return valor


@app.route("/")
def index():
    return render_template("Index.html")


def _calcular_a_partir_do_form(form):
    """Lê os campos do formulário e chama calcular(). Lança ValueError
    se algum campo numérico estiver inválido."""
    return calcular(
        sexo=form.get("sexo", ""),
        tempo_bruto_geral_2019=int(form.get("tempo_bruto_geral_2019", 0)),
        tempo_bruto_militar_2019=int(form.get("tempo_bruto_militar_2019", 0)),
        desconto_le_2017=int(form.get("desconto_le_2017", 0)),
        desconto_le_2019=int(form.get("desconto_le_2019", 0)),
        tempo_privado_2019=int(form.get("tempo_privado_2019", 0)),
        tempo_militar_2019=int(form.get("tempo_militar_2019", 0)),
    )


@app.route("/Calculadora", methods=["GET", "POST"])
def Calculadora():
    resultado = None
    erro = None
    dados_form = {}

    if request.method == "POST":
        dados_form = request.form.to_dict()
        try:
            resultado = _calcular_a_partir_do_form(request.form)
        except ValueError as e:
            erro = "Verifique os dados: todos os campos numéricos devem ser números inteiros." \
                if "invalid literal" in str(e) else str(e)

    return render_template(
        "Calculadora.html",
        resultado=resultado,
        erro=erro,
        dados_form=dados_form,
    )


@app.route("/Calculadora/pdf", methods=["POST"])
def calculadora_pdf():
    dados_form = request.form.to_dict()
    try:
        resultado = _calcular_a_partir_do_form(request.form)
    except ValueError:
        # Dados inválidos: volta para a calculadora em vez de gerar PDF quebrado
        return redirect(url_for("Calculadora"))

    buffer = gerar_pdf(dados_form, resultado)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="ficha-calculo-inatividade.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
