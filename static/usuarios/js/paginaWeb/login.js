// Efecto de elevación en los campos de entrada
document.querySelectorAll(".form-input").forEach((input) => {
  input.addEventListener("focus", function () {
    this.style.transform = "translateY(-1px)";
    this.style.boxShadow =
      "0 0 0 3px rgba(0, 229, 255, 0.2), 0 0 20px rgba(0, 229, 255, 0.1)";
  });

  input.addEventListener("blur", function () {
    this.style.transform = "translateY(0)";
    this.style.boxShadow = "none";
  });
});

// Animación del cubo al hacer hover
document.querySelector(".cube").addEventListener("mouseenter", function () {
  this.style.animationDuration = "2s";
});

document.querySelector(".cube").addEventListener("mouseleave", function () {
  this.style.animationDuration = "8s";
});

// Efecto de ondas en el botón
document.querySelector(".submit-btn").addEventListener("click", function (e) {
  const ripple = document.createElement("span");
  const rect = this.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = e.clientX - rect.left - size / 2;
  const y = e.clientY - rect.top - size / 2;

  ripple.style.position = "absolute";
  ripple.style.width = ripple.style.height = size + "px";
  ripple.style.left = x + "px";
  ripple.style.top = y + "px";
  ripple.style.background = "rgba(255, 255, 255, 0.3)";
  ripple.style.borderRadius = "50%";
  ripple.style.pointerEvents = "none";
  ripple.style.transform = "scale(0)";
  ripple.style.animation = "ripple 0.6s linear";

  this.appendChild(ripple);

  setTimeout(() => {
    ripple.remove();
  }, 600);
});

const style = document.createElement("style");
style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
document.head.appendChild(style);
