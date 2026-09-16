// Interacciones de la vista de inicio de sesión: alternar visibilidad de contraseña, control de tema y estado del botón de envío.
document.addEventListener('DOMContentLoaded', () => {
    // 1. Alternar Contraseña
    const passInput = document.getElementById('contrasena');
    const togglePassBtn = document.getElementById('togglePasswordBtn');
    const eyeIcon = document.getElementById('eyeIcon');

    if (togglePassBtn && passInput) {
        togglePassBtn.addEventListener('click', () => {
            const isPassword = passInput.type === 'password';
            passInput.type = isPassword ? 'text' : 'password';
            eyeIcon.textContent = isPassword ? 'visibility' : 'visibility_off';
            togglePassBtn.setAttribute('aria-label', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');
        });
    }

    // 2. Control de Tema Oscuro / Claro
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');

    function updateThemeIcon() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        if (themeIcon) {
            themeIcon.textContent = isDark ? 'light_mode' : 'dark_mode';
        }
    }

    updateThemeIcon();

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            if (isDark) {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            }
            updateThemeIcon();
        });
    }

    // 3. Estado de envío en botón
    const form = document.getElementById('loginForm');
    const btn = document.getElementById('btnLogin');
    const captcha = document.getElementById('g-recaptcha-response');
    if (form && btn) {

        const siteKey = form.getAttribute('data-sitekey');

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            btn.disabled = true;
            const btnText = btn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Ingresando...';

            const restoreButton = () => {
                btn.disabled = false;
                if (btnText) btnText.textContent = 'Ingresar al Sistema';
            };

            try {
                if (typeof grecaptcha === 'undefined' || !siteKey) {
                    console.warn("reCAPTCHA no está disponible o la clave no está configurada.");
                    if (!siteKey) {
                        // Si no hay clave (por ejemplo entorno local sin reCAPTCHA), enviar directamente
                        form.submit();
                        return;
                    }
                    restoreButton();
                    return;
                }

                grecaptcha.ready(() => {
                    try {
                        grecaptcha.execute(siteKey, { action: 'login' })
                            .then((token) => {
                                captcha.value = token;
                                form.submit();
                            })
                            .catch((error) => {
                                console.error("Error al obtener reCAPTCHA:", error);
                                restoreButton();
                            });
                    } catch (innerErr) {
                        console.error("Error síncrono al ejecutar reCAPTCHA:", innerErr);
                        restoreButton();
                    }
                });
            } catch (err) {
                console.error("Error inesperado en flujo de autenticación:", err);
                restoreButton();
            }
        });
    }
});
