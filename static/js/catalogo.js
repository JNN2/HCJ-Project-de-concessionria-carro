/*
 * HCJ Motors — Catálogo de Veículos
 */

document.addEventListener("DOMContentLoaded", () => {
    // FILTRO DE ANO
    const anoMinimo = document.getElementById("ano-minimo");
    const anoMaximo = document.getElementById("ano-maximo");

    const valorMinimo = document.getElementById("ano-minimo-valor");
    const valorMaximo = document.getElementById("ano-maximo-valor");

    if (anoMinimo && anoMaximo && valorMinimo && valorMaximo) {
        function atualizarAnos(controleAlterado) {
            // Impede que o mínimo ultrapasse o máximo
            if (Number(anoMinimo.value) > Number(anoMaximo.value)) {
                if (controleAlterado === anoMinimo) {
                    anoMaximo.value = anoMinimo.value;
                } else {
                    anoMinimo.value = anoMaximo.value;
                }
            }
            valorMinimo.textContent = anoMinimo.value;
            valorMaximo.textContent = anoMaximo.value;
        }

        anoMinimo.addEventListener("input", () => {
            atualizarAnos(anoMinimo);
        });

        anoMaximo.addEventListener("input", () => {
            atualizarAnos(anoMaximo);
        });
        atualizarAnos(anoMinimo);
    }
    // VISUALIZAÇÃO EM GRADE OU LISTA
    const botaoGrade = document.querySelector(".visualizacao-grade");
    const botaoLista = document.querySelector(".visualizacao-lista");
    const container = document.querySelector(".catalogo-veiculos");

    if (botaoGrade && botaoLista && container) {
        function alternarVisualizacao(modoLista) {
            container.classList.toggle("modo-lista", modoLista);

            botaoGrade.setAttribute("aria-pressed", String(!modoLista));
            botaoLista.setAttribute("aria-pressed", String(modoLista));
        }
        botaoGrade.addEventListener("click", () => {
            alternarVisualizacao(false);
        });

        botaoLista.addEventListener("click", () => {
            alternarVisualizacao(true);
        });
    }
});
