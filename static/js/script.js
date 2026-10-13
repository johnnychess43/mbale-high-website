document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menuToggle");
    const navMenu = document.getElementById("navMenu");

    if (!menuToggle || !navMenu) return;

    function setMenuOpen(open) {
        navMenu.classList.toggle("active", open);
        menuToggle.setAttribute("aria-expanded", String(open));
        menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    }

    setMenuOpen(false);

    menuToggle.addEventListener("click", function (event) {
        event.stopPropagation();
        setMenuOpen(!navMenu.classList.contains("active"));
    });

    navMenu.addEventListener("click", function (event) {
        if (event.target.closest("a")) setMenuOpen(false);
    });

    document.addEventListener("click", function (event) {
        if (!navMenu.contains(event.target) && !menuToggle.contains(event.target)) {
            setMenuOpen(false);
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            setMenuOpen(false);
            menuToggle.focus();
        }
    });
});
