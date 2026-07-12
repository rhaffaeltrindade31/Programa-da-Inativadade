from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("Index.html")

@app.route("/Calculadora")
def calculadora():
    return render_template("Calculadora.html")

if __name__ == "__main__":
    app.run(debug=True)