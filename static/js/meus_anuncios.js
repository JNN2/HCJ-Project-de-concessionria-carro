/*
 * HCJ Motors — Meus Anúncios
 */

document.addEventListener("DOMContentLoaded", () => {
    const lista = document.getElementById("lista-anuncios");
    const resumo = document.querySelector(".anuncios-resumo");

    if (!lista) return;

    const urlImagemPadrao = "/static/images/m3_competition.webp";

    function atualizarContador() {
        const quantidade = lista.querySelectorAll(".anuncio-card").length;

        if (resumo) {
            resumo.textContent = "";

            const texto = document.createElement("p");
            texto.append("Total de anúncios: ");

            const total = document.createElement("strong");
            total.textContent = quantidade;

            texto.appendChild(total);
            resumo.appendChild(texto);
        }

        return quantidade;
    }

    function criarElemento(tag, classe, texto) {
        const elemento = document.createElement(tag);

        if (classe) {
            elemento.className = classe;
        }

        if (texto !== undefined) {
            elemento.textContent = texto;
        }

        return elemento;
    }

    function exibirEstadoVazio() {
        lista.replaceChildren();

        const vazio = criarElemento("div", "anuncios-vazio");
        const titulo = criarElemento(
            "h2",
            "",
            "Nenhum anúncio encontrado"
        );

        const descricao = criarElemento(
            "p",
            "",
            "Você ainda não possui anúncios publicados."
        );

        const link = criarElemento(
            "a",
            "",
            "Cadastrar veículo"
        );

        link.href = "/cadastrar-veiculo";

        vazio.append(titulo, descricao, link);
        lista.appendChild(vazio);

        atualizarContador();
    }

    function exibirErro(mensagem) {
        const aviso = criarElemento(
            "div",
            "anuncios-aviso",
            mensagem
        );

        aviso.setAttribute("role", "alert");
        lista.before(aviso);
    }

    function criarCard(anuncio) {
        const card = criarElemento("article", "anuncio-card");

        const id = Number(anuncio.id);
        const status = anuncio.status === "pausado"
            ? "pausado"
            : "ativo";

        card.dataset.id = String(id);
        card.dataset.status = status;

        const imagem = document.createElement("img");

        // A API deve retornar o nome do arquivo, não um caminho externo.
        const nomeImagem = String(anuncio.imagem || "");

        const imagemValida = /^[a-zA-Z0-9_.-]+$/.test(nomeImagem)
            && !nomeImagem.startsWith(".");

        imagem.src = imagemValida
            ? `/static/images/${encodeURIComponent(nomeImagem)}`
            : urlImagemPadrao;

        imagem.alt = `${anuncio.marca || ""} ${anuncio.modelo || ""}`;
        imagem.loading = "lazy";

        const info = criarElemento("div", "anuncio-info");

        const titulo = criarElemento(
            "h2",
            "",
            `${anuncio.marca || ""} ${anuncio.modelo || ""}`
        );

        const detalhes = criarElemento(
            "p",
            "",
            `${anuncio.ano || "—"} · ${anuncio.quilometragem || "—"} km`
        );

        const preco = criarElemento(
            "strong",
            "",
            `R$ ${anuncio.preco || "0,00"}`
        );

        const etiqueta = criarElemento(
            "span",
            "anuncio-status",
            status === "ativo" ? "Ativo" : "Pausado"
        );

        const acoes = criarElemento("div", "anuncio-acoes");

        const linkDetalhes = criarElemento(
            "a",
            "",
            "Ver detalhes"
        );

        linkDetalhes.href = Number.isSafeInteger(id) && id > 0
            ? `/detalhes/${id}`
            : "#";

        const botaoStatus = criarElemento(
            "button",
            "btn-status",
            status === "ativo" ? "Pausar" : "Reativar"
        );

        botaoStatus.type = "button";
        botaoStatus.disabled = true;
        botaoStatus.title =
            "Disponível após integração com o backend";
        acoes.append(linkDetalhes, botaoStatus);
        info.append(titulo, detalhes, preco, etiqueta, acoes);
        card.append(imagem, info);
        return card;
    }

    function renderizarAnuncios(anuncios) {
        if (!Array.isArray(anuncios)) {
            exibirErro("Formato de dados inválido.");
            return;
        }

        if (anuncios.length === 0) {
            exibirEstadoVazio();
            return;
        }

        const fragmento = document.createDocumentFragment();
        anuncios.forEach((anuncio) => {
            fragmento.appendChild(criarCard(anuncio));
        });

        lista.replaceChildren(fragmento);
        atualizarContador();
    }

    async function carregarAnuncios(url) {
        try {
            const resposta = await fetch(url, {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    Accept: "application/json"
                }
            });

            if (!resposta.ok) {
                throw new Error(
                    `Falha ao carregar anúncios: ${resposta.status}`
                );
            }

            const dados = await resposta.json();
            renderizarAnuncios(dados);
        } catch (erro) {
            console.error("HCJ Motors:", erro);

            exibirErro(
                "Não foi possível carregar seus anúncios. Tente novamente."
            );
        }
    }

    // Por padrão, usa os cards já renderizados pelo Flask.
    atualizarContador();
    // Opcional: configure data-api-url no container
    // somente quando a API autenticada estiver pronta.
    const apiUrl = lista.dataset.apiUrl;

    if (apiUrl) {
        carregarAnuncios(apiUrl);
    }
});
