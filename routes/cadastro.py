from datetime import date
from decimal import Decimal, InvalidOperation

from flask import jsonify, render_template, request


MARCAS = { "BMW", "Chevrolet", "Fiat", "Ford", "Honda", "Hyundai", "Toyota", "Volkswagen", "BYD", "GWM", "Jeep", "Mercedes-Benz", "Audi", "Porsche", "Renault", "Volvo", "Ferrari", "McLaren", "Lamborghini", "Outra", 
}

COMBUSTIVEIS = { "Gasolina", "Etanol", "Flex", "Diesel", "Elétrico", "Híbrido",
}

TRANSMISSOES = { "Manual", "Automático", "CVT", "Automatizado",
}

CARROCERIAS = { "Sedã", "Hatch", "SUV", "Picape", "Cupê", "Conversível",
}

CAMPOS = {
    "marca": "Marca",
    "modelo": "Modelo",
    "ano": "Ano",
    "preco": "Preço",
    "combustivel": "Combustível",
    "transmissao": "Câmbio",
    "localizacao": "Localização",
    "carroceria": "Carroceria",
    "cor": "Cor",
    "quilometragem": "Quilometragem",
    "descricao": "Descrição",
}


def cadastrar_veiculo():
    # GET: exibe o formulário.
    if request.method == "GET":
        return render_template("cadastrar_veiculo.html")

    # POST: recebe os campos enviados pelo FormData.
    dados = {
        campo: request.form.get(campo, "").strip()
        for campo in CAMPOS
    }

    erros = {}

    # Valida todos os campos obrigatórios.
    for campo, nome in CAMPOS.items():
        if not dados[campo]:
            erros[campo] = f"O campo {nome} é obrigatório."

    # Valida as opções dos selects.
    opcoes = {
        "marca": MARCAS,
        "combustivel": COMBUSTIVEIS,
        "transmissao": TRANSMISSOES,
        "carroceria": CARROCERIAS,
    }

    for campo, permitidas in opcoes.items():
        if dados[campo] and dados[campo] not in permitidas:
            erros[campo] = (
                f"Selecione uma opção válida para {CAMPOS[campo]}."
            )

    # Valida os tamanhos dos textos.
    limites = {
        "modelo": (2, 80),
        "localizacao": (3, 120),
        "cor": (1, 40),
        "descricao": (10, 500),
    }

    for campo, (minimo, maximo) in limites.items():
        valor = dados[campo]

        if valor and not minimo <= len(valor) <= maximo:
            erros[campo] = (
                f"{CAMPOS[campo]} deve ter entre "
                f"{minimo} e {maximo} caracteres."
            )

    # Valida o ano.
    ano_maximo = date.today().year + 1
    if dados["ano"]:
        try:
            ano = int(dados["ano"])
            if not 1900 <= ano <= ano_maximo:
                raise ValueError

        except ValueError:
            erros["ano"] = ( f"Informe um ano entre 1900 e {ano_maximo}." )

    # Valida a quilometragem.
    if dados["quilometragem"]:
        try:
            quilometragem = int(dados["quilometragem"])

            if quilometragem < 0:
                raise ValueError

        except ValueError:
            erros["quilometragem"] = (
                "A quilometragem deve ser um número inteiro "
                "maior ou igual a zero."
            )

    # O input number envia o preço no formato 65000.00.
    if dados["preco"]:
        try:
            preco = Decimal(dados["preco"])

            if not preco.is_finite() or preco <= 0:
                raise ValueError

            if preco != preco.quantize(Decimal("0.01")):
                raise ValueError

        except (InvalidOperation, ValueError):
            erros["preco"] = (
                "Informe um preço maior que zero "
                "com no máximo duas casas decimais."
            )

    # Retorna os erros para o JavaScript.
    if erros:
        return jsonify({
            "sucesso": False,
            "mensagem": next(iter(erros.values())),
            "erros": erros,
        }), 400

    # Nesta task, apenas validamos os dados.
    return jsonify({
        "sucesso": True,
        "mensagem": (
            "Dados do anúncio validados com sucesso! "
            "O anúncio ainda não foi salvo."
        ),
    }), 200


def registrar_rotas_cadastro(app):
    app.add_url_rule(
        "/cadastrar-veiculo",
        endpoint="cadastrar_veiculo",
        view_func=cadastrar_veiculo,
        methods=["GET", "POST"],
    )