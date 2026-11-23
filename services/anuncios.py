import csv
import os
from pathlib import Path
from uuid import uuid4

# Localiza o CSV a partir da raiz do projeto.
CAMINHO_CSV = ( Path(__file__).resolve().parent.parent / "data" / "veiculos.csv" )

# Define a estrutura das colunas do arquivo.
COLUNAS = [
    "id",
    "marca",
    "modelo",
    "ano",
    "combustivel",
    "transmissao",
    "preco",
    "imagem",
    "imagens",
    "quilometragem",
    "carroceria",
    "cor",
    "descricao",
    "localizacao",
    "status",
    "usuario_id"
]


def atualizar_status_anuncio(anuncio_id, usuario_id, status):
    """Atualiza somente um anúncio pertencente ao usuário autenticado."""
    with CAMINHO_CSV.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames or []
        if (len(colunas) != len(set(colunas))
                or not {"id", "status"}.issubset(colunas)):
            raise ValueError("Cabeçalho CSV incompatível.")
        registros = list(leitor)

    if any(None in registro or any(valor is None for valor in registro.values())
           for registro in registros):
        raise ValueError("Há linhas inválidas no CSV.")

    encontrados = [registro for registro in registros
                   if registro["id"] == str(anuncio_id)]
    if not encontrados:
        return "nao_encontrado"
    if len(encontrados) != 1:
        raise ValueError("Há IDs duplicados no CSV.")
    anuncio = encontrados[0]
    if not anuncio.get("usuario_id") or anuncio["usuario_id"] != str(usuario_id):
        return "proibido"

    anuncio["status"] = status
    temporario = CAMINHO_CSV.with_name(f".veiculos_{uuid4().hex}.tmp")
    try:
        with temporario.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=colunas)
            escritor.writeheader()
            escritor.writerows(registros)
        os.replace(temporario, CAMINHO_CSV)
    finally:
        temporario.unlink(missing_ok=True)
    return "atualizado"


def salvar_anuncio(anuncio):
    """
    Adiciona um novo anúncio ao CSV.
    Preserva os registros existentes,
    gera um ID e retorna esse ID.
    """

    # Garante que a pasta data exista.
    CAMINHO_CSV.parent.mkdir( parents=True, exist_ok=True )

    registros = []
    # Carrega os anúncios já cadastrados.
    if CAMINHO_CSV.exists():
        with CAMINHO_CSV.open( "r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader( arquivo, delimiter=",")
            cabecalho = leitor.fieldnames or []

            # Impede perder colunas desconhecidas
            # ou interpretar um CSV incompatível.
            if ( len(cabecalho) != len(set(cabecalho)) or not set(cabecalho).issubset(COLUNAS)):
                raise ValueError("Cabeçalho CSV incompatível.")

            registros = list(leitor)

            # Detecta linhas com colunas excedentes.
            if any(None in item for item in registros):
                raise ValueError("Há linhas inválidas no CSV.")

    # Gera um ID maior que todos os anteriores.
    novo_id = max((int(item["id"]) for item in registros), default=0 ) + 1

    # Organiza os dados na ordem das colunas.
    novo = {
        coluna: anuncio.get(coluna, "")
        for coluna in COLUNAS
    }

    novo["id"] = novo_id

    # Converte a lista de imagens para texto.
    # Exemplo: foto1.jpg|foto2.jpg
    if isinstance(novo["imagens"], list):
        novo["imagens"] = "|".join(novo["imagens"])

    registros.append(novo)

    # Cria um arquivo temporário para gravar
    # antes de substituir o CSV original.
    temporario = CAMINHO_CSV.with_name(f".veiculos_{uuid4().hex}.tmp")

    try:
        with temporario.open( "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter( arquivo, fieldnames=COLUNAS, delimiter=",")
            escritor.writeheader()
            escritor.writerows(registros)
        # Substitui o arquivo após concluir a escrita.
        os.replace(temporario, CAMINHO_CSV)

    finally:
        # Remove o temporário se ele ainda existir.
        temporario.unlink(missing_ok=True)

    return novo_id
