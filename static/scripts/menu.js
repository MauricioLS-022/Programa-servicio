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

    // 4. Bottom nav: ocultar al scrollear hacia abajo, mostrar al subir
    const bottomNav = document.querySelector('.mobile-bottom-nav');
    if (bottomNav) {
        let lastScrollY = window.scrollY;
        let ticking = false;
        let hidden = false;
        const THRESHOLD = 50;

        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const currentScrollY = window.scrollY;

                    if (currentScrollY <= 15) {
                        bottomNav.classList.remove('hidden-nav');
                        hidden = false;
                    } else if (!hidden && currentScrollY > lastScrollY && currentScrollY > THRESHOLD) {
                        const downDelta = currentScrollY - lastScrollY;
                        if (downDelta > 5) {
                            bottomNav.classList.add('hidden-nav');
                            hidden = true;
                        }
                    } else if (hidden && currentScrollY < lastScrollY) {
                        const upDelta = lastScrollY - currentScrollY;
                        if (upDelta > THRESHOLD) {
                            bottomNav.classList.remove('hidden-nav');
                            hidden = false;
                        }
                    }

                    lastScrollY = currentScrollY;
                    ticking = false;
                });
                ticking = true;
            }
        });
    }
});