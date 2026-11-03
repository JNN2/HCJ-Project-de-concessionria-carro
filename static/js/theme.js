
/* ======================================
   ALTERNÂNCIA DE TEMA
====================================== */

// Seleciona o elemento HTML e o botão
const html = document.documentElement;
const themeButton = document.getElementById("theme-toggle");

// Recupera o tema salvo ou utiliza dark
const savedTheme = localStorage.getItem("hcj-theme") || "dark";

// Aplica o tema inicial
applyTheme(savedTheme);

// Evento de clique
themeButton.addEventListener("click", () => {

    const currentTheme = html.getAttribute("data-theme");

    const newTheme =
        currentTheme === "dark" ? "light" : "dark";

    applyTheme(newTheme);

    // Salva a preferência
    localStorage.setItem("hcj-theme", newTheme);
});

// Função responsável pela mudança
function applyTheme(theme) {

    html.setAttribute("data-theme", theme);

    const icon = themeButton.querySelector("i");

    if (theme === "dark") {
        icon.className = "fa-solid fa-moon";
        themeButton.setAttribute(
            "aria-label",
            "Ativar tema claro"
        );
    } else {
        icon.className = "fa-solid fa-sun";
        themeButton.setAttribute(
            "aria-label",
            "Ativar tema escuro"
        );
    }
}
