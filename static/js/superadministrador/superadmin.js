
        // Función para cambiar sección activa
        function showSection(section) {
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            // En una implementación real, aquí se comunicaría con el iframe o se cargaría el contenido
            console.log('Cambiando a sección:', section);
        }

        // Función de logout
        function logout() {
            if (confirm('¿Está seguro de que desea cerrar sesión?')) {
                alert('Sesión cerrada correctamente');
                // En una aplicación real, aquí redirigirías al login
            }
        }