//Galeria de imagens do veículo

document.addEventListener("DOMContentLoaded", () => {
    const galeria = document.querySelector(".galeria");
    if (!galeria) return;

    const principal = galeria.querySelector("#galeria-foto-principal");
    if (!principal) return;

    const miniaturas = [...galeria.querySelectorAll(".galeria-miniatura")];
    const anterior = galeria.querySelector(".galeria-anterior");
    const proxima = galeria.querySelector(".galeria-proxima");
    const contador = galeria.querySelector(".galeria-contador");

    const ampliar = galeria.querySelector(".galeria-ampliar");
    const modal = galeria.querySelector(".galeria-modal");
    const imagemModal = galeria.querySelector(".galeria-modal-imagem");
    const fechar = galeria.querySelector(".galeria-fechar");

    const fotos = miniaturas.length
        ? miniaturas.map(botao => botao.dataset.foto)
        : [principal.src];

    let atual = 0;

    function mostrarFoto(indice) {
        atual = (indice + fotos.length) % fotos.length;

        principal.src = fotos[atual];
        principal.alt = `Foto ${atual + 1} de ${fotos.length} do veículo`;

        if (contador) {
            contador.textContent = `${atual + 1} / ${fotos.length}`;
        }

        miniaturas.forEach((botao, indiceMiniatura) => {
            const selecionada = indiceMiniatura === atual;

            botao.classList.toggle("ativa", selecionada);
            botao.setAttribute("aria-pressed", String(selecionada));
        });

        if (modal?.open && imagemModal) {
            imagemModal.src = fotos[atual];
            imagemModal.alt = principal.alt;
        }
    }

    // Navegação pelas setas
    anterior?.addEventListener("click", () => mostrarFoto(atual - 1));
    proxima?.addEventListener("click", () => mostrarFoto(atual + 1));

    // Navegação pelas miniaturas
    miniaturas.forEach((botao, indice) => {
        botao.addEventListener("click", () => mostrarFoto(indice));
    });

    // Ampliar a foto selecionada
    ampliar?.addEventListener("click", () => {
        if (!modal || !imagemModal) return;

        imagemModal.src = fotos[atual];
        imagemModal.alt = principal.alt;
        modal.showModal();
    });

    // Fechar a ampliação
    fechar?.addEventListener("click", () => modal.close());

    // Navegação pelo teclado
    document.addEventListener("keydown", evento => {
        const focoNaGaleria = galeria.contains(document.activeElement);

        if (!focoNaGaleria && !modal?.open) return;
        if (fotos.length < 2) return;

        if (evento.key === "ArrowRight") {
            evento.preventDefault();
            mostrarFoto(atual + 1);
        }

        if (evento.key === "ArrowLeft") {
            evento.preventDefault();
            mostrarFoto(atual - 1);
        }
    });

    // Gestos de deslizar no celular
    let inicioToque = null;

    const area = galeria.querySelector(".galeria-principal");

    area?.addEventListener("touchstart", evento => {
        inicioToque = evento.changedTouches[0].screenX;
    }, { passive: true });

    area?.addEventListener("touchend", evento => {
        if (inicioToque === null || fotos.length < 2) return;

        const distancia = evento.changedTouches[0].screenX - inicioToque;

        if (Math.abs(distancia) > 45) {
            mostrarFoto(atual + (distancia < 0 ? 1 : -1));
        }

        inicioToque = null;
    }, { passive: true });

    console.log(`Galeria HCJ Motors: ${fotos.length} foto(s) carregada(s).`);
});
