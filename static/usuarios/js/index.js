 function openModal() {
            document.getElementById('loginModal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('loginModal').style.display = 'none';
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('loginModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

        // Login form handling
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Simulate login process
            if (email && password) {
                // Show loading state
                const submitBtn = document.querySelector('.login-submit');
                submitBtn.innerHTML = 'Iniciando sesión...';
                submitBtn.disabled = true;
                
                // Simulate API call delay
                setTimeout(() => {
                    alert('¡Bienvenido a PhysicsLab Pro! Redirigiendo al dashboard...');
                    closeModal();
                    
                    // Reset form
                    document.getElementById('loginForm').reset();
                    submitBtn.innerHTML = 'Acceder a la Plataforma';
                    submitBtn.disabled = false;
                }, 1500);
            }
        });

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Animated counters for features
        function animateValue(element, start, end, duration) {
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                element.innerHTML = Math.floor(progress * (end - start) + start);
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        }

        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
                }
            });
        }, observerOptions);

        // Observe feature cards
        document.querySelectorAll('.feature-card, .pricing-card').forEach(card => {
            observer.observe(card);
        });