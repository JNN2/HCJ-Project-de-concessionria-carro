from flask import (Flask, abort, jsonify, render_template, request)
import os

app = Flask(__name__)
# Necessária para mensagens flash e sessões.
# Configure FLASK_SECRET_KEY no ambiente em produção.
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "chave-apenas-para-desenvolvimento-local"
)

# Dados temporários para testar o catálogo.
# Posteriormente serão carregados do armazenamento.
veiculos = [
    {
        "id": 1,
        "marca": "BMW",
        "modelo": "M3 Competition",
        "ano": 2022,
        "combustivel": "Gasolina",
        "transmissao": "Automático",
        "preco": "489.900,00",
        "imagem": "m3_competition.webp",
        "quilometragem": "25.500",
        "carroceria": "Sedã",
        "cor": "Cinza"
    }
]


# Página inicial
@app.route("/")
def home():
    return render_template("index.html")


# Catálogo de veículos
@app.route("/catalogo")
def catalogo():
    return render_template(
        "catalogo.html",
        veiculos=veiculos
    )


# Detalhes do veículo
@app.route("/detalhes/<int:id>")
def detalhes_veiculo(id):
    veiculo = next(
        (v for v in veiculos if v["id"] == id),
        None
    )

    if veiculo is None:
        abort(404)

    return render_template(
        "detalhes_veiculo.html",
        veiculo=veiculo
    )


# Formulário de cadastro de veículos
@app.route("/cadastrar-veiculo", methods=["GET", "POST"])
def cadastrar_veiculo():
    if request.method == "GET":
        return render_template("cadastrar_veiculo.html")
    # Recebe os dados enviados pelo FormData.
    dados = request.form
    campos_obrigatorios = [
        "marca",
        "modelo",
        "ano",
        "preco",
        "quilometragem",
        "combustivel",
        "transmissao",
        "localizacao",
        "descricao"
    ]
    # Validação inicial no servidor.
    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return jsonify({
                "sucesso": False,
                "mensagem": f"O campo {campo} é obrigatório."
            }), 400

    # Esta rota ainda não salva o anúncio.
    return jsonify({
        "sucesso": True,
        "mensagem": (
            "Dados recebidos para teste! "
            "O anúncio ainda não foi cadastrado."
        )
    }), 200



if __name__ == "__main__":
    app.run(debug=True)
