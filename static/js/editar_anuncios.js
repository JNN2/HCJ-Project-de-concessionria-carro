// Aguarda o carregamento do HTML.
document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.querySelector("#form-editar-anuncio");
    // Impede erros caso o formulário não exista na página.
    if (!formulario) return;
    const botaoSalvar = formulario.querySelector(".btn_salvar");
    const mensagem = document.querySelector("#edicao-mensagem");
    const galeria = formulario.querySelector(".edicao_fotos");
    const inputFotos = document.querySelector("#novas_fotos");
    const MAX_FOTOS = 8;
    const MAX_TAMANHO = 5 * 1024 * 1024;
    const formatosPermitidos = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];
    // Armazena os nomes das fotos removidas.
    const fotosRemovidas = [];
    // =========================================
    // EXIBIR MENSAGENS
    // ==========================================
    function exibirMensagem(texto, sucesso = false) {
        mensagem.textContent = texto;
        mensagem.className = sucesso
            ? "edicao-mensagem sucesso"
            : "edicao-mensagem erro";
    }
    // ==========================================
    // VALIDAR CAMPOS
    // ==========================================
    function validarFormulario() {
        const campos = formulario.querySelectorAll("[required]");
        // Verifica os campos obrigatórios.
        for (const campo of campos) {
            if (!campo.value.trim()) {
                const nome = campo.labels?.[0]?.textContent || campo.name;
                exibirMensagem(`Preencha o campo ${nome}.`);
                campo.focus();
                return false;
            }
        }
        const ano = Number(formulario.elements.ano.value);
        const anoMaximo = new Date().getFullYear() + 1;
        // Valida o ano do veículo.
        if ( !Number.isInteger(ano) || ano < 1900 || ano > anoMaximo) {   
            exibirMensagem(`Informe um ano entre 1900 e ${anoMaximo}.` );
            formulario.elements.ano.focus();
            return false;
        }
        const precoTexto = formulario.elements.preco.value.trim();
        // Aceita preço decimal com ponto ou vírgula.
        const precoNormalizado = precoTexto.includes(",")
            ? precoTexto.replace(/\./g, "").replace(",", ".")
            : precoTexto;
        const preco = Number(precoNormalizado);

        // Valida o preço.
        if ( !/^\d+(\.\d{1,2})?$/.test(precoNormalizado) || !Number.isFinite(preco) || preco <= 0) {
            exibirMensagem("Informe um preço válido.");
            formulario.elements.preco.focus();
            return false;
        }
        const km = Number(formulario.elements.quilometragem.value );
        // Valida a quilometragem.
        if (!Number.isInteger(km) || km < 0) {
            exibirMensagem( "Informe uma quilometragem inteira e não negativa." );
            formulario.elements.quilometragem.focus();
            return false;
        }
        const descricao = formulario.elements.descricao.value.trim();
        // Valida o tamanho da descrição.
        if (descricao.length < 10 || descricao.length > 500) {
            exibirMensagem("A descrição deve possuir entre 10 e 500 caracteres." );
            formulario.elements.descricao.focus();
            return false;
        }
        return true;
    }
    // ==========================================
    // VALIDAR NOVAS FOTOS
    // ==========================================
    function validarFotos() {
        const fotosAtuais = galeria.querySelectorAll(".edicao_foto").length;
        const novasFotos = Array.from(inputFotos.files);
        // Considera fotos antigas e novas.
        if (fotosAtuais + novasFotos.length > MAX_FOTOS) {
            exibirMensagem("O anúncio pode possuir até 8 fotos.");
            return false;
        }

        for (const foto of novasFotos) {
            // Verifica o formato da imagem.
            if (!formatosPermitidos.includes(foto.type)) {
                exibirMensagem( "Selecione apenas imagens JPG, PNG ou WEBP.");
                return false;
            }
            // Verifica o tamanho da imagem.
            if (foto.size === 0 || foto.size > MAX_TAMANHO) {
                exibirMensagem( "Cada imagem deve possuir até 5 MB e não estar vazia.");
                return false;
            }
        }
        return true;
    }
    // Valida as imagens assim que forem selecionadas.
    inputFotos.addEventListener("change", () => {
        if (!validarFotos()) {
            inputFotos.value = "";
            return;
        }
        mensagem.textContent = "";
    });
    // ==========================================
    // REMOVER E REORGANIZAR FOTOS
    // ==========================================
    galeria.addEventListener("click", (evento) => {
        const botao = evento.target.closest("button");
        if (!botao) return;
        const foto = botao.closest(".edicao_foto");

        if (!foto) return;
        // Remove uma foto existente da interface.
        if (botao.classList.contains("btn_remover")) {
            fotosRemovidas.push(foto.dataset.foto);
            foto.remove();
            return;
        }
        // Reorganiza a posição das fotos.
        if (botao.classList.contains("btn_mover")) {
            const direcao = botao.getAttribute("aria-label");
            const anterior = foto.previousElementSibling;
            const proxima = foto.nextElementSibling;

            // Move a foto para a esquerda.
            if ( direcao === "Mover foto para a esquerda" && anterior?.classList.contains("edicao_foto")) {
                galeria.insertBefore(foto, anterior);
            }

            // Move a foto para a direita.
            if (direcao === "Mover foto para a direita" && proxima?.classList.contains("edicao_foto")) {
                galeria.insertBefore(proxima, foto);
            }
        }
    });
    // ==========================================
    // ENVIAR ALTERAÇÕES AO FLASK
    // ==========================================
    formulario.addEventListener("submit", async (evento) => {
        // Impede o envio tradicional do formulário.
        evento.preventDefault();
        mensagem.textContent = "";
        // Valida os campos e as imagens.
        if (!validarFormulario() || !validarFotos()) {
            return;
        }
        // Recupera todos os campos do formulário.
        const dados = new FormData(formulario);
        // Normaliza o preço para envio ao backend.
        const preco = formulario.elements.preco.value.trim();
        dados.set( "preco", preco.includes(",") ? preco.replace(/\./g, "").replace(",", "."): preco);
        // Recupera as fotos mantidas na ordem atual.
        const fotosMantidas = Array.from( galeria.querySelectorAll(".edicao_foto")).map(foto => foto.dataset.foto);
        // Envia a lista de fotos existentes.
        dados.set("fotos_mantidas", JSON.stringify(fotosMantidas));
        // Envia a lista de fotos removidas.
        dados.set( "fotos_removidas", JSON.stringify(fotosRemovidas) );
        // Impede múltiplos envios.
        botaoSalvar.disabled = true;
        const textoOriginal = botaoSalvar.textContent;
        botaoSalvar.textContent = "Salvando...";
        try {
            // Envia os dados para a rota Flask.
            const resposta = await fetch(formulario.action, {
                method: "POST",
                body: dados,
                credentials: "same-origin",
                headers: {
                    "Accept": "application/json"
                }
            });
            // Verifica se o backend retornou JSON.
            const tipo = resposta.headers.get("content-type") || "";
            if (!tipo.includes("application/json")) {
                throw new Error("O servidor não retornou uma resposta válida.");
            }
            const resultado = await resposta.json();
            // Trata erros retornados pelo Flask.
            if (!resposta.ok || resultado.sucesso !== true) {
                exibirMensagem( resultado.mensagem || "Não foi possível atualizar o anúncio.");
                return;
            }
            // Apresenta a confirmação.
            exibirMensagem(resultado.mensagem || "Anúncio atualizado com sucesso!", true );
            // Retorna para Meus Anúncios.
            setTimeout(() => {
                window.location.href = formulario.dataset.redirect;
            }, 1500);
        } catch (erro) {
            console.error("Erro ao editar anúncio:", erro);
            exibirMensagem(erro.message || "Erro de comunicação com o servidor.");
        } finally {
            // Restaura o botão após a resposta.
            botaoSalvar.disabled = false;
            botaoSalvar.textContent = textoOriginal;
        }
    });
});
