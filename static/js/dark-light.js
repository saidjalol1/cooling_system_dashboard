const html = document.documentElement;
const toggleBtn = document.getElementById("theme-toggle");

toggleBtn.addEventListener("click", () => {
    html.classList.toggle("dark");
});