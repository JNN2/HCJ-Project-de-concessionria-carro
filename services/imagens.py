import os
from pathlib import Path
from uuid import uuid4
from PIL import Image, UnidentifiedImageError

# Pasta pública onde ficam as fotos.
PASTA_IMAGENS = ( Path(__file__).resolve().parent.parent / "static" / "images")

# Formatos aceitos pelo servidor.
FORMATOS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp"
}

MAX_FOTOS = 8
MAX_BYTES = 5 * 1024 * 1024

def validar_fotos(arquivos):
    """
    Valida os arquivos recebidos.
    Retorna uma mensagem quando encontra erro.
    Retorna None quando estão válidos.
    """

    # Verifica a quantidade de fotos.
    if len(arquivos) > MAX_FOTOS:
        return "Selecione no máximo 8 fotos."

    for arquivo in arquivos:
        # Descobre o tamanho em bytes.
        arquivo.stream.seek(0, os.SEEK_END)
        tamanho = arquivo.stream.tell()
        # Volta ao início para permitir a leitura.
        arquivo.stream.seek(0)

        if not 0 < tamanho <= MAX_BYTES:
            return (
                "Cada foto deve ter entre "
                "1 byte e 5 MB."
            )
        try:
            # Abre a imagem e identifica o formato real.
            with Image.open(arquivo.stream) as imagem:
                if imagem.format not in FORMATOS:
                    return ( "Envie apenas JPG, PNG ou WEBP." )
                # Verifica se a imagem está íntegra.
                imagem.verify()
        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            Image.DecompressionBombError
        ):
            return "Uma das fotos é inválida."

        finally:
            # Permite ler novamente para salvar.
            arquivo.stream.seek(0)

    return None


def remover_fotos(nomes):
    """
    Remove as imagens salvas quando
    ocorre um erro no cadastro.
    """

    for nome in nomes:
        caminho = PASTA_IMAGENS / nome
        caminho.unlink(missing_ok=True)


def salvar_fotos(arquivos):
    """
    Salva as imagens na pasta static/images.
    Gera nomes únicos e devolve uma lista
    com os nomes dos arquivos salvos.
    """

    PASTA_IMAGENS.mkdir(parents=True, exist_ok=True)

    nomes = []

    try:
        for arquivo in arquivos:
            arquivo.stream.seek(0)
            with Image.open(arquivo.stream) as imagem:
                formato = imagem.format
                if formato not in FORMATOS:
                    raise ValueError( "Formato de foto inválido." )
                # Cria um nome único para cada foto.
                nome = (
                    f"veiculo_{uuid4().hex}"
                    f"{FORMATOS[formato]}"
                )

                destino = PASTA_IMAGENS / nome
                # Decodifica a imagem.
                imagem.load()
                # JPEG exige RGB ou escala de cinza.
                if formato == "JPEG":
                    imagem = imagem.convert("RGB")
                # Salva o arquivo processado.
                imagem.save( destino, format=formato )
            nomes.append(nome)
    except Exception:
        # Se uma foto falhar, remove as anteriores.
        remover_fotos(nomes)
        raise
    return nomes
