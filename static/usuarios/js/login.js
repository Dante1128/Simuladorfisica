// login.js - JavaScript para formulario de login mejorado

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const form = document.querySelector('form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const submitBtn = document.querySelector('.btn');
    const inputs = document.querySelectorAll('input');

    // Animaciones de entrada
    animateOnLoad();

    // Event listeners
    form.addEventListener('submit', handleSubmit);
    emailInput.addEventListener('input', validateEmail);
    emailInput.addEventListener('blur', validateEmail);
    passwordInput.addEventListener('input', validatePassword);
    passwordInput.addEventListener('blur', validatePassword);

    // Añadir efectos a los inputs
    inputs.forEach(input => {
        input.addEventListener('focus', handleInputFocus);
        input.addEventListener('blur', handleInputBlur);
    });

    /**
     * Animaciones de carga inicial
     */
    function animateOnLoad() {
        const container = document.querySelector('.container');
        const formGroups = document.querySelectorAll('.form-group');
        
        // Animación del contenedor principal
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            container.style.transition = 'all 0.6s ease';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 100);

        // Animación escalonada de los campos
        formGroups.forEach((group, index) => {
            group.style.opacity = '0';
            group.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                group.style.transition = 'all 0.4s ease';
                group.style.opacity = '1';
                group.style.transform = 'translateX(0)';
            }, 200 + (index * 150));
        });
    }

    /**
     * Manejar envío del formulario
     */
    function handleSubmit(e) {
        e.preventDefault();
        
        // Validar campos antes del envío
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();
        
        if (!isEmailValid || !isPasswordValid) {
            showError('Por favor, completa todos los campos correctamente.');
            return;
        }

        // Animación del botón durante el envío
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <span style="display: inline-flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="m12 1 0 6m0 6 0 6"/>
                    <path d="m17 12 6 0m-6 0-6 0"/>
                </svg>
                Iniciando sesión...
            </span>
        `;

        // Simular envío (aquí integrarías con Django)
        setTimeout(() => {
            // Aquí enviarías los datos a tu vista de Django
            submitToServer();
        }, 1500);
    }

    /**
     * Validar campo de email
     */
    function validateEmail() {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const inputContainer = emailInput.parentElement;
        
        // Limpiar mensajes anteriores
        clearFieldError(inputContainer);
        
        if (!email) {
            showFieldError(inputContainer, 'El correo es requerido');
            return false;
        }
        
        if (!emailRegex.test(email)) {
            showFieldError(inputContainer, 'Ingresa un correo válido');
            return false;
        }
        
        showFieldSuccess(inputContainer);
        return true;
    }

    /**
     * Validar campo de contraseña
     */
    function validatePassword() {
        const password = passwordInput.value;
        const inputContainer = passwordInput.parentElement;
        
        // Limpiar mensajes anteriores
        clearFieldError(inputContainer);
        
        if (!password) {
            showFieldError(inputContainer, 'La contraseña es requerida');
            return false;
        }
        
        if (password.length < 6) {
            showFieldError(inputContainer, 'La contraseña debe tener al menos 6 caracteres');
            return false;
        }
        
        showFieldSuccess(inputContainer);
        return true;
    }

    /**
     * Mostrar error en campo específico
     */
    function showFieldError(container, message) {
        const input = container.querySelector('input');
        input.style.borderColor = '#ef4444';
        input.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
        
        let errorElement = container.querySelector('.error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            errorElement.style.cssText = `
                color: #ef4444;
                font-size: 12px;
                margin-top: 5px;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            container.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        setTimeout(() => errorElement.style.opacity = '1', 10);
    }

    /**
     * Mostrar éxito en campo específico
     */
    function showFieldSuccess(container) {
        const input = container.querySelector('input');
        input.style.borderColor = '#22c55e';
        input.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.1)';
    }

    /**
     * Limpiar errores de campo
     */
    function clearFieldError(container) {
        const input = container.querySelector('input');
        const errorElement = container.querySelector('.error-message');
        
        input.style.borderColor = '';
        input.style.boxShadow = '';
        
        if (errorElement) {
            errorElement.style.opacity = '0';
            setTimeout(() => errorElement.remove(), 300);
        }
    }

    /**
     * Manejar foco en input
     */
    function handleInputFocus(e) {
        const container = e.target.parentElement;
        const label = container.parentElement.querySelector('label');
        
        container.style.transform = 'scale(1.02)';
        container.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
        
        if (label) {
            label.style.color = '#4f46e5';
            label.style.transform = 'translateY(-2px)';
        }
    }

    /**
     * Manejar pérdida de foco en input
     */
    function handleInputBlur(e) {
        const container = e.target.parentElement;
        const label = container.parentElement.querySelector('label');
        
        container.style.transform = 'scale(1)';
        container.style.boxShadow = '';
        
        if (label) {
            label.style.color = '';
            label.style.transform = '';
        }
    }

    /**
     * Mostrar mensaje de error general
     */
    function showError(message) {
        // Remover mensaje anterior si existe
        const existingError = document.querySelector('.general-error');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'general-error';
        errorDiv.style.cssText = `
            background: #fee2e2;
            border: 1px solid #fecaca;
            color: #dc2626;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
        `;
        errorDiv.textContent = message;
        
        form.insertBefore(errorDiv, form.firstChild);
        
        setTimeout(() => {
            errorDiv.style.opacity = '1';
            errorDiv.style.transform = 'translateY(0)';
        }, 10);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.style.opacity = '0';
                errorDiv.style.transform = 'translateY(-10px)';
                setTimeout(() => errorDiv.remove(), 300);
            }
        }, 5000);
    }

    /**
     * Enviar datos al servidor (Django)
     */
    function submitToServer() {
        const formData = new FormData();
        formData.append('correo', emailInput.value);
        formData.append('password', passwordInput.value);
        
        // Obtener CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken.value);
        }

        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess('¡Inicio de sesión exitoso! Redirigiendo...');
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/dashboard/';
                }, 1000);
            } else {
                showError(data.message || 'Error al iniciar sesión. Intenta nuevamente.');
                resetSubmitButton();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Error de conexión. Verifica tu conexión a internet.');
            resetSubmitButton();
        });
    }

    /**
     * Mostrar mensaje de éxito
     */
    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.style.cssText = `
            background: #d1fae5;
            border: 1px solid #a7f3d0;
            color: #065f46;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        `;
        
        successDiv.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m9 12 2 2 4-4"/>
                <circle cx="12" cy="12" r="9"/>
            </svg>
            ${message}
        `;
        
        form.insertBefore(successDiv, form.firstChild);
        
        setTimeout(() => {
            successDiv.style.opacity = '1';
            successDiv.style.transform = 'translateY(0)';
        }, 10);
    }

    /**
     * Resetear botón de envío
     */
    function resetSubmitButton() {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Iniciar Sesión';
    }

    /**
     * Efectos adicionales para mejorar UX
     */
    
    // Añadir efecto ripple al botón
    submitBtn.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;
        
        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });

    // Añadir animación CSS para el ripple
    if (!document.querySelector('#ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            .input-container {
                transition: all 0.3s ease;
            }
            
            label {
                transition: all 0.3s ease;
            }
        `;
        document.head.appendChild(style);
    }

    // Auto-focus en el primer campo al cargar
    setTimeout(() => {
        emailInput.focus();
    }, 800);
});