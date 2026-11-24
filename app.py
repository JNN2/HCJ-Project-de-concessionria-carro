from flask import (Flask, abort, jsonify, render_template, request)
from routes.cadastro import registrar_rotas_cadastro
from routes.anuncios import registrar_rotas_anuncios
import os
import csv

def converter_preco(preco):
    preco = preco.strip()
    preco = preco.replace(".", "")
    preco = preco.replace(",", ".")

    return float(preco)

def formatar_preco(preco):
    return f"{preco:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def carregar_veiculos():
    veiculos = []
    caminho = os.path.join(
        os.path.dirname(__file__), "data", "veiculos.csv"
    )
    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=",")

        for veiculo in leitor:
            veiculo["id"] = int(veiculo["id"])
            veiculo["preco"] = converter_preco(veiculo["preco"])
            veiculo["ano"] = int(veiculo["ano"])
            veiculo["quilometragem"] = int(veiculo["quilometragem"].replace(".",""))
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

def obter_opcoes_filtros(veiculos):
    return {
        "localizacoes": sorted(set(v["localizacao"] for v in veiculos)),
        "marcas": sorted(set(v["marca"] for v in veiculos)),
        "modelos": sorted(set(v["modelo"] for v in veiculos))
    }

app = Flask(__name__)
app.jinja_env.globals.update(formatar_preco=formatar_preco)
# Necessária para mensagens flash e sessões.
# Configure FLASK_SECRET_KEY no ambiente em produção.
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "chave-apenas-para-desenvolvimento-local"
)
# Rota de cadastro de viuculos
registrar_rotas_cadastro(app)
registrar_rotas_anuncios(app)
# Limita o tamanho total dos dados enviados.
# Até 8 imagens de 5 MB, mais os dados do formulário.
app.config["MAX_CONTENT_LENGTH"] = 42 * 1024 * 1024

# Página inicial
@app.route("/")
def home():
    return render_template("index.html")


# Catálogo de veículos
@app.route("/catalogo")
def catalogo():
    veiculos = carregar_veiculos()
    opcoes = obter_opcoes_filtros(veiculos)

    return render_template(
        "catalogo.html",
        veiculos=veiculos,
        **opcoes
    )

# Resultados da pesquisa
@app.route("/resultados-pesquisa")
def resultados_pesquisa():
    termo = request.args.get("busca", "").strip().lower()
    veiculos = carregar_veiculos()
    localizacao = request.args.get("localizacao", "").strip().lower()
    marca = request.args.get("marca", "").strip().lower()
    modelo = request.args.get("modelo", "").strip().lower()

    ano_minimo = request.args.get("ano_minimo")
    ano_maximo = request.args.get("ano_maximo")
    km_maxima = request.args.get("km_maxima")
    preco_minimo = request.args.get("preco_minimo")
    preco_maximo = request.args.get("preco_maximo")
    resultados = []

    for veiculo in veiculos:
        if marca and marca != veiculo["marca"].lower():
            continue

        if modelo and modelo != veiculo["modelo"].lower():
            continue

        if localizacao and localizacao != veiculo["localizacao"].lower():
            continue

        if ano_minimo and veiculo["ano"] < int(ano_minimo):
            continue

        if ano_maximo and veiculo["ano"] > int(ano_maximo):
            continue

        if km_maxima and veiculo["quilometragem"] > int(km_maxima):
            continue

        if preco_minimo and veiculo["preco"] < float(preco_minimo):
            continue

        if preco_maximo and veiculo["preco"] > float(preco_maximo):
            continue

        if termo in veiculo["marca"].lower() or termo in veiculo["modelo"].lower():
            resultados.append(veiculo)

    opcoes = obter_opcoes_filtros(veiculos)

    return render_template(
    "catalogo.html",
    veiculos=resultados,
    **opcoes
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

@app.route('/editar-anuncio/<int:id>')
def editar_anuncio(id):
    veiculos = carregar_veiculos()
    veiculo = next((v for v in veiculos if v['id'] == id), None)
    
    if veiculo is None:
        abort(404)

    return render_template('editar_anuncio.html', veiculo=veiculo)


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
