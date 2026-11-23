from datetime import date
from decimal import Decimal, InvalidOperation
from flask import jsonify, render_template, request, session, current_app
import csv
from services.anuncios import salvar_anuncio
from services.imagens import validar_fotos, salvar_fotos, remover_fotos


# Opções aceitas pelo formulário de cadastro.
MARCAS = {
    "BMW", "Chevrolet", "Fiat", "Ford", "Honda", "Hyundai", "Toyota", "Volkswagen", "BYD", "GWM", "Jeep", "Mercedes-Benz", "Audi", "Porsche", "Renault", "Volvo", "Ferrari", "McLaren", "Lamborghini", "Outra"
}

COMBUSTIVEIS = {
    "Gasolina", "Etanol", "Flex", "Diesel", "Elétrico", "Híbrido"
}

TRANSMISSOES = {
    "Manual", "Automático", "CVT", "Automatizado"
}

CARROCERIAS = {
    "Sedã", "Hatch", "SUV", "Picape", "Cupê", "Conversível"
}

# Campos esperados do HTML.
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

def resposta_cadastro(sucesso, mensagem, status, erros=None, anuncio_id=None):
    """
    Padroniza as respostas da rota de cadastro.

    sucesso: indica se o cadastro funcionou.
    mensagem: texto exibido ao usuário.
    status: código HTTP da resposta.
    erros: erros específicos de cada campo.
    anuncio_id: ID do anúncio criado.
    """

    resposta = {
        "sucesso": sucesso,
        "mensagem": mensagem
    }

    # Inclui os erros quando existirem.
    if erros is not None:
        resposta["erros"] = erros

    # Inclui o ID somente após um cadastro concluído.
    if anuncio_id is not None:
        resposta["anuncio_id"] = anuncio_id

    return jsonify(resposta), status

def cadastrar_veiculo():
    # GET: apresenta a página de cadastro.
    if request.method == "GET":
        return render_template("cadastrar_veiculo.html")
    # POST: exige um vendedor autenticado.
    # A rota de login deve definir session["usuario_id"].
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return resposta_cadastro(
            sucesso=False,
            mensagem="Faça login para cadastrar um anúncio.",
            status=401
        )
    # Recebe os campos enviados pelo JavaScript.
    dados = {
        campo: request.form.get(campo, "").strip()
        for campo in CAMPOS
    }
    erros = {}
    # Verifica os campos obrigatórios.
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
            erros[campo] = (f"Selecione uma opção válida para {CAMPOS[campo]}.")

    # Verifica o tamanho dos textos.
    limites = {
        "modelo": (2, 80),
        "localizacao": (3, 120),
        "cor": (2, 40),
        "descricao": (10, 500),
    }
    for campo, (minimo, maximo) in limites.items():
        valor = dados[campo]
        if valor and not minimo <= len(valor) <= maximo:
            erros[campo] = (
                f"{CAMPOS[campo]} deve ter entre "
                f"{minimo} e {maximo} caracteres."
            )
    # Valida o ano de fabricação.
    ano_maximo = date.today().year + 1

    if dados["ano"]:
        try:
            ano = int(dados["ano"])

            if not 1900 <= ano <= ano_maximo:
                raise ValueError

        except ValueError:
            erros["ano"] = ( f"Informe um ano entre 1900 e {ano_maximo}.")
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
    # Valida o preço recebido pelo input number.
    # Exemplo: 65000.00
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
    # Retorna os erros ao cadastro.js.
    if erros:
        return resposta_cadastro(
            sucesso=False,
            mensagem=next(iter(erros.values())),
            status=400,
            erros=erros
        )
    # Recebe as fotos enviadas pelo formulário.
    # O input deve utilizar name="fotos".
    arquivos = [
        arquivo
        for arquivo in request.files.getlist("fotos")
        if arquivo.filename
    ]
    # Verifica as fotos antes de salvar.
    erro_fotos = validar_fotos(arquivos)
    if erro_fotos:
        return resposta_cadastro(
            sucesso=False,
            mensagem=erro_fotos,
            status=400,
            erros={"fotos": erro_fotos}
        )
    # Prepara os dados para o CSV.
    anuncio = dados.copy()
    # Mantém o formato de preço esperado pelo app.py.
    # Exemplo: 65000.00 -> 65000,00
    anuncio["preco"] = (
        f'{Decimal(dados["preco"]):.2f}'.replace(".", ",")
    )
    # O anúncio começa como ativo.
    anuncio["status"] = "ativo"
    # Associa o anúncio ao vendedor autenticado.
    # Nunca recebe o ID do vendedor diretamente do HTML.
    anuncio["usuario_id"] = str(usuario_id)

    nomes = []
    try:
        # Salva os arquivos na pasta static/images.
        nomes = salvar_fotos(arquivos)
        # A primeira foto é a imagem principal.
        anuncio["imagem"] = nomes[0] if nomes else ""
        # Todas as fotos formam a galeria.
        anuncio["imagens"] = nomes
        # Grava o anúncio no CSV e recebe seu ID.
        novo_id = salvar_anuncio(anuncio)
    except (OSError, ValueError, csv.Error):
        # Remove as fotos se o cadastro falhar.
        remover_fotos(nomes)
        current_app.logger.exception( "Falha ao persistir anúncio")
        return resposta_cadastro(
            sucesso=False,
            mensagem="Não foi possível salvar o anúncio. Tente novamente.",
            status=500
        )
    # HTTP 201: anúncio criado.
    return resposta_cadastro(
        sucesso=True,
        mensagem="Anúncio cadastrado com sucesso!",
        status=201,
        anuncio_id=novo_id
    )

def registrar_rotas_cadastro(app):
    # Registra a rota no app.py sem duplicá-la.
    app.add_url_rule(
        "/cadastrar-veiculo",
        endpoint="cadastrar_veiculo",
        view_func=cadastrar_veiculo,
        methods=["GET", "POST"],
    )