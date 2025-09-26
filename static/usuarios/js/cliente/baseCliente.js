function toggleMobileMenu() {
  const nav = document.getElementById("navbarNav");
  nav.classList.toggle("mobile-active");
}

document.addEventListener("click", function (event) {
  const nav = document.getElementById("navbarNav");
  const toggle = document.querySelector(".mobile-menu-toggle");

  if (!nav.contains(event.target) && !toggle.contains(event.target)) {
    nav.classList.remove("mobile-active");
  }
});
