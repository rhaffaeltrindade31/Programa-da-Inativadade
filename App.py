# -*- coding: utf-8 -*-
from flask import Flask, render_template, request

from Calculo import calcular

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Calculadora", methods=["GET", "POST"])
def Calculadora():
    resultado = None
    erro = None
    dados_form = {}

    if request.method == "POST":
        dados_form = request.form.to_dict()
        try:
            resultado = calcular(
                sexo=request.form.get("sexo", ""),
                tempo_bruto_geral_2019=int(request.form.get("tempo_bruto_geral_2019", 0)),
                tempo_bruto_militar_2019=int(request.form.get("tempo_bruto_militar_2019", 0)),
                desconto_le_2017=int(request.form.get("desconto_le_2017", 0)),
                desconto_le_2019=int(request.form.get("desconto_le_2019", 0)),
                tempo_privado_2019=int(request.form.get("tempo_privado_2019", 0)),
                tempo_militar_2019=int(request.form.get("tempo_militar_2019", 0)),
            )
        except ValueError as e:
            erro = "Verifique os dados: todos os campos numéricos devem ser números inteiros." \
                if "invalid literal" in str(e) else str(e)

    return render_template(
        "Calculadora.html",
        resultado=resultado,
        erro=erro,
        dados_form=dados_form,
    )


if __name__ == "__main__":
    app.run(debug=True)
