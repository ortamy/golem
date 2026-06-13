// GOLEM web-v2 — placeholder

// Theme toggle (sun/moon button)
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("theme-toggle");
  if (!toggle) return;

  toggle.addEventListener("click", () => {
    const html = document.documentElement;
    html.classList.toggle("dark");
  });
});