document.addEventListener("DOMContentLoaded", () => {
  // Smooth scrolling
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });

  // Animación de aparición al hacer scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.animationDelay = "0s";
        entry.target.classList.add("fade-in");
      }
    });
  }, observerOptions);

  document.querySelectorAll(".section").forEach((section) => {
    observer.observe(section);
  });

  // Efecto de partículas en el hero
  const hero = document.querySelector(".hero");
  if (hero) {
    function createParticle() {
      const particle = document.createElement("div");
      particle.style.cssText = `
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255,255,255,0.3);
        border-radius: 50%;
        pointer-events: none;
        animation: particleFloat 4s linear infinite;
      `;
      particle.style.left = Math.random() * 100 + "%";
      particle.style.animationDelay = Math.random() * 4 + "s";
      hero.appendChild(particle);

      setTimeout(() => {
        particle.remove();
      }, 4000);
    }

    setInterval(createParticle, 500);

    const style = document.createElement("style");
    style.textContent = `
      @keyframes particleFloat {
        0% {
          transform: translateY(100vh) rotate(0deg);
          opacity: 0;
        }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% {
          transform: translateY(-100px) rotate(360deg);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }
});
