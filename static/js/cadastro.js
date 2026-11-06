document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const form = document.querySelector(".cadastro-form");
    // Executa apenas na página de cadastro.
    if (!form) return;
    const campos = {
        marca: form.querySelector("#marca"),
        modelo: form.querySelector("#modelo"),
        ano: form.querySelector("#ano"),
        preco: form.querySelector("#preco"),
        quilometragem: form.querySelector("#quilometragem"),
        combustivel: form.querySelector("#combustivel"),
        transmissao: form.querySelector("#transmissao"),
        localizacao: form.querySelector("#localizacao"),
        descricao: form.querySelector("#descricao"),
        fotos: form.querySelector("#fotos")
    };

    const botaoEnviar = form.querySelector(".cadastro-btn-enviar");
    const botaoLimpar = form.querySelector(".cadastro-btn-limpar");
    const LIMITE_FOTOS = 8;
    const TAMANHO_MAXIMO = 5 * 1024 * 1024;
    const TIPOS_PERMITIDOS = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];
    const anoAtual = new Date().getFullYear();
    // ========================================
    // ELEMENTOS DE FEEDBACK
    // ========================================
    const mensagemGeral = document.createElement("div");
    mensagemGeral.className = "cadastro-mensagem";
    mensagemGeral.setAttribute("role", "status");
    mensagemGeral.setAttribute("aria-live", "polite");
    form.prepend(mensagemGeral);

    const contador = document.createElement("small");
    contador.className = "cadastro-contador";
    contador.setAttribute("aria-live", "off");
    campos.descricao.closest(".cadastro-campo").append(contador);

    const previa = document.createElement("div");
    previa.className = "cadastro-previas";
    form.querySelector(".cadastro-fotos").append(previa);

    const resumoFotos = document.createElement("small");
    resumoFotos.className = "cadastro-resumo-fotos";
    form.querySelector(".cadastro-fotos").append(resumoFotos);
    // ========================================
    // FUNÇÕES DE MENSAGEM
    // ========================================
    function mostrarMensagem(texto, tipo = "erro") {
        mensagemGeral.textContent = texto;
        mensagemGeral.className =
            `cadastro-mensagem cadastro-mensagem--${tipo}`;
        mensagemGeral.hidden = false;
    }
    function limparMensagem() {
        mensagemGeral.textContent = "";
        mensagemGeral.hidden = true;
    }
    function mostrarErro(campo, texto) {
        const grupo = campo.closest(".cadastro-campo")
            || campo.closest(".cadastro-fotos");

        if (!grupo) return;
        campo.setAttribute("aria-invalid", "true");
        let erro = grupo.querySelector(".cadastro-erro");
        if (!erro) {
            erro = document.createElement("small");
            erro.className = "cadastro-erro";
            erro.setAttribute("role", "alert");
            grupo.append(erro);
        }
        erro.textContent = texto;
    }

    function limparErro(campo) {
        const grupo = campo.closest(".cadastro-campo")
            || campo.closest(".cadastro-fotos");

        if (!grupo) return;
        campo.removeAttribute("aria-invalid");
        const erro = grupo.querySelector(".cadastro-erro");
        if (erro) erro.remove();
    }
    // ========================================
    // VALIDAÇÃO DOS CAMPOS
    // ========================================
    function validarCampo(campo) {
        limparErro(campo);
        const valor = campo.value.trim();

        if (campo.required && !valor) {
            mostrarErro(campo, "Este campo é obrigatório.");
            return false;
        }
        if (!valor) return true;
        switch (campo.id) {
            case "modelo":
                if (valor.length < 2) {
                    mostrarErro(
                        campo,
                        "Informe um modelo com pelo menos 2 caracteres."
                    );
                    return false;
                }
                break;

            case "ano": {
                const ano = Number(valor);

                if (
                    !Number.isInteger(ano) ||
                    ano < 1900 ||
                    ano > anoAtual + 1
                ) {
                    mostrarErro(
                        campo,
                        `Informe um ano entre 1900 e ${anoAtual + 1}.`
                    );
                    return false;
                }
                break;
            }

            case "preco": {
                const preco = Number(valor);

                if (!Number.isFinite(preco) || preco <= 0) {
                    mostrarErro(
                        campo,
                        "O preço deve ser maior que zero."
                    );
                    return false;
                }
                break;
            }

            case "quilometragem": {
                const km = Number(valor);

                if (!Number.isInteger(km) || km < 0) {
                    mostrarErro(
                        campo,
                        "Informe uma quilometragem válida."
                    );
                    return false;
                }
                break;
            }

            case "localizacao":
                if (valor.length < 3) {
                    mostrarErro(
                        campo,
                        "Informe uma localização válida."
                    );
                    return false;
                }
                break;

            case "descricao":
                if (valor.length < 10 || valor.length > 500) {
                    mostrarErro(
                        campo,
                        "A descrição deve ter entre 10 e 500 caracteres."
                    );
                    return false;
                }
                break;
        }

        // Respeita outras restrições definidas no HTML.
        if (!campo.checkValidity()) {
            mostrarErro(
                campo,
                "Verifique o valor informado."
            );
            return false;
        }

        return true;
    }

    // ========================================
    // VALIDAÇÃO DAS FOTOS
    // ========================================

    function validarFotos() {
        limparErro(campos.fotos);

        const arquivos = Array.from(campos.fotos.files);

        // Fotos opcionais nesta etapa.
        if (arquivos.length === 0) return true;

        if (arquivos.length > LIMITE_FOTOS) {
            mostrarErro(
                campos.fotos,
                `Selecione no máximo ${LIMITE_FOTOS} fotos.`
            );
            return false;
        }

        for (const arquivo of arquivos) {
            if (!TIPOS_PERMITIDOS.includes(arquivo.type)) {
                mostrarErro(
                    campos.fotos,
                    "São permitidas apenas imagens JPG, PNG ou WEBP."
                );
                return false;
            }

            if (arquivo.size > TAMANHO_MAXIMO) {
                mostrarErro(
                    campos.fotos,
                    `A imagem "${arquivo.name}" ultrapassa 5 MB.`
                );
                return false;
            }

            if (arquivo.size === 0) {
                mostrarErro(
                    campos.fotos,
                    "Não é permitido enviar arquivos vazios."
                );
                return false;
            }
        }

        return true;
    }

    // ========================================
    // PRÉ-VISUALIZAÇÃO DAS IMAGENS
    // ========================================

    let urlsTemporarias = [];

    function limparPrevias() {
        urlsTemporarias.forEach((url) => {
            URL.revokeObjectURL(url);
        });

        urlsTemporarias = [];
        previa.replaceChildren();
        resumoFotos.textContent = "";
    }

    function atualizarPrevias() {
        limparPrevias();

        if (!validarFotos()) return;

        const arquivos = Array.from(campos.fotos.files);

        if (arquivos.length === 0) return;

        resumoFotos.textContent =
            `${arquivos.length} foto(s) selecionada(s).`;

        arquivos.forEach((arquivo) => {
            const url = URL.createObjectURL(arquivo);
            urlsTemporarias.push(url);

            const imagem = document.createElement("img");
            imagem.src = url;
            imagem.alt = `Prévia de ${arquivo.name}`;
            imagem.loading = "lazy";

            const item = document.createElement("div");
            item.className = "cadastro-previa-item";
            item.append(imagem);

            previa.append(item);
        });
    }

    // ========================================
    // CONTADOR DE CARACTERES
    // ========================================

    function atualizarContador() {
        const quantidade = campos.descricao.value.length;
        contador.textContent = `${quantidade}/500 caracteres`;
    }

    // ========================================
    // VALIDAÇÃO COMPLETA
    // ========================================

    function validarFormulario() {
        let valido = true;
        let primeiroInvalido = null;

        Object.entries(campos).forEach(([nome, campo]) => {
            if (nome === "fotos") return;

            if (!validarCampo(campo)) {
                valido = false;

                if (!primeiroInvalido) {
                    primeiroInvalido = campo;
                }
            }
        });

        if (!validarFotos()) {
            valido = false;

            if (!primeiroInvalido) {
                primeiroInvalido = campos.fotos;
            }
        }

        if (!valido) {
            mostrarMensagem(
                "Corrija os campos destacados antes de continuar."
            );

            primeiroInvalido?.focus();
        }

        return valido;
    }

    // ========================================
    // EVENTOS DOS CAMPOS
    // ========================================

    Object.entries(campos).forEach(([nome, campo]) => {
        if (nome === "fotos") return;

        const evento = campo.tagName === "SELECT"
            ? "change"
            : "input";

        campo.addEventListener(evento, () => {
            limparErro(campo);
            limparMensagem();

            if (campo === campos.descricao) {
                atualizarContador();
            }
        });

        campo.addEventListener("blur", () => {
            if (campo.value.trim()) {
                validarCampo(campo);
            }
        });
    });

    campos.fotos.addEventListener("change", atualizarPrevias);

    // ========================================
    // LIMPAR FORMULÁRIO
    // ========================================

    botaoLimpar?.addEventListener("click", () => {
        // O reset nativo é executado após o clique.
    });

    form.addEventListener("reset", () => {
        Object.values(campos).forEach(limparErro);

        limparMensagem();
        limparPrevias();

        // Aguarda o reset nativo restaurar os valores.
        queueMicrotask(atualizarContador);
    });

    // ========================================
    // ENVIO DOS DADOS PARA O FLASK
    // ========================================

    form.noValidate = true;

    form.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        limparMensagem();

        if (!validarFormulario()) return;

        const dados = new FormData(form);
        const textoOriginal = botaoEnviar.innerHTML;

        botaoEnviar.disabled = true;
        botaoEnviar.textContent = "Enviando...";

        try {
            const resposta = await fetch(form.action, {
                method: "POST",
                body: dados,
                headers: {
                    "Accept": "application/json"
                }
            });

            const resultado = await resposta.json();

            if (!resposta.ok || !resultado.sucesso) {
                throw new Error(
                    resultado.mensagem ||
                    "Não foi possível enviar o formulário."
                );
            }

            mostrarMensagem(resultado.mensagem, "sucesso");

            // Não limpa o formulário automaticamente:
            // nesta etapa o backend ainda não salva anúncios.

        } catch (erro) {
            mostrarMensagem(
                erro.message ||
                "Ocorreu um erro ao enviar o formulário."
            );
        } finally {
            botaoEnviar.disabled = false;
            botaoEnviar.innerHTML = textoOriginal;
        }
    });

    // Inicialização
    limparMensagem();
    atualizarContador();
});
