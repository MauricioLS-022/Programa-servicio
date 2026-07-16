document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtenemos los elementos del DOM
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    // 2. Función genérica para abrir/cerrar
    function toggleMenu() {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        
        // Evitar que el usuario haga scroll en el cuerpo cuando el menú está abierto
        if (sidebar.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }

    // 3. Asignamos los eventos de clic
    if (menuToggle) {
        menuToggle.addEventListener('click', toggleMenu);
    }

    // Si hacen clic en el fondo oscuro, cerramos el menú
    if (overlay) {
        overlay.addEventListener('click', toggleMenu);
    }
});