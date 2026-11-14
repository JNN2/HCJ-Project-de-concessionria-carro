from flask import (Flask, abort, jsonify, render_template, request)
import os
import csv

def carregar_veiculos():
    veiculos = []
    caminho = os.path.join(
        os.path.dirname(__file__), "data", "veiculos.csv"
    )
    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        for veiculo in leitor:
            veiculo["id"] = int(veiculo["id"])
            # Converte as imagens do CSV em uma lista Python
            fotos = veiculo.get("imagens", "").strip()
            veiculo["imagens"] = [
                foto.strip()
                for foto in fotos.split("|")
                if foto.strip()
            ]
            # Se não houver galeria, usa a imagem principal
            imagem = veiculo.get("imagem", "").strip()

            if not veiculo["imagens"] and imagem:
                veiculo["imagens"] = [imagem]

            veiculos.append(veiculo)
    return veiculos

app = Flask(__name__)
# Necessária para mensagens flash e sessões.
# Configure FLASK_SECRET_KEY no ambiente em produção.
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "chave-apenas-para-desenvolvimento-local"
)


# Página inicial
@app.route("/")
def home():
    return render_template("index.html")


# Catálogo de veículos
@app.route("/catalogo")
def catalogo():
    veiculos = carregar_veiculos()
    
    return render_template(
        "catalogo.html",
        veiculos=veiculos
    )

# Resultados da pesquisa
@app.route("/resultados-pesquisa")
def resultados_pesquisa():
    termo = request.args.get("busca", "").strip().lower()
    veiculos = carregar_veiculos()

    resultados = [
        veiculo for veiculo in veiculos
        if termo in veiculo["marca"].lower()
        or termo in veiculo["modelo"].lower()
    ]

    return render_template(
        "catalogo.html",
        veiculos=resultados
    )

@app.route("/api/veiculos")
def api_veiculos():
    veiculos = carregar_veiculos()
    return jsonify(veiculos)

# Detalhes do veículo
@app.route("/detalhes/<int:id>")
def detalhes_veiculo(id):
    veiculo = next(
        (v for v in carregar_veiculos() if v["id"] == id),
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


@app.route("/meus-anuncios")
def meus_anuncios():
    veiculos = carregar_veiculos()
    # Temporário: ainda não existe filtro por vendedor autenticado
    anuncios = veiculos
    return render_template(
        "meus_anuncios.html",
        anuncios=anuncios
    )

if __name__ == "__main__":
    app.run(debug=True)
