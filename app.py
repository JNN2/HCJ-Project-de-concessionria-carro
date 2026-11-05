from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/catalogo")
def catalogo():
    return render_template("catalogo.html")


@app.route("/detalhes")
def veiculo():
    return render_template("detalhes_veiculo.html")


if __name__ == "__main__":
    app.run(debug=True)
