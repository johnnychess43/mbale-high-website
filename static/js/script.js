document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.getElementById("menuToggle");
    const navMenu = document.getElementById("navMenu");

    if (!menuToggle || !navMenu) {
        console.log("❌ Navigation elements not found");
        return;
    }

    console.log("✅ Navigation JavaScript loaded");

    menuToggle.addEventListener("click", function () {

        navMenu.classList.toggle("active");

        console.log("🍔 Menu clicked");

    });

});