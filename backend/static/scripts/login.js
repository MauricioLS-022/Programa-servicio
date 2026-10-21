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

    // 3. Helper para mostrar alertas de feedback dinámicas en el cliente
    function showLoginAlert(message, isSuccess = false) {
        let container = document.getElementById('loginAlertContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'loginAlertContainer';
            const card = document.querySelector('.login-card');
            const formEl = document.getElementById('loginForm');
            if (card && formEl) {
                card.insertBefore(container, formEl);
            }
        }
        if (container) {
            const icon = isSuccess ? 'check_circle' : 'error';
            container.innerHTML = `
                <div class="login-alert" role="alert">
                    <span class="material-symbols-outlined" aria-hidden="true">${icon}</span>
                    <span>${message}</span>
                </div>
            `;
            container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    // 4. Estado de envío en botón y protección contra envíos múltiples
    const form = document.getElementById('loginForm');
    const btn = document.getElementById('btnLogin');
    const captcha = document.getElementById('g-recaptcha-response');
    let isSubmitting = false;

    if (form && btn) {
        const siteKey = form.getAttribute('data-sitekey');

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Prevenir doble clic o clics repetidos en ráfaga
            if (isSubmitting) return;
            isSubmitting = true;

            btn.disabled = true;
            const btnText = btn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Ingresando...';

            const restoreButton = () => {
                btn.disabled = false;
                isSubmitting = false;
                if (btnText) btnText.textContent = 'Ingresar al Sistema';
            };

            // Limpiar alertas de error previas al intentar de nuevo
            const existingAlert = document.getElementById('loginAlertContainer');
            if (existingAlert) {
                existingAlert.innerHTML = '';
            }

            try {
                // Caso 1: Sin site_key configurada (desarrollo local)
                if (!siteKey) {
                    form.submit();
                    return;
                }

                // Caso 2: reCAPTCHA no cargó (bloqueador de anuncios o error de red)
                if (typeof grecaptcha === 'undefined') {
                    console.warn("reCAPTCHA no está disponible en la ventana.");
                    showLoginAlert("No se pudo cargar la verificación de seguridad (reCAPTCHA). Si tienes activo un bloqueador de anuncios o extensiones de privacidad, desactívalo temporalmente e inténtalo de nuevo.");
                    restoreButton();
                    return;
                }

                let hasCompleted = false;

                // Temporizador de seguridad (Timeout 4s): no dejar al usuario colgado
                const timeoutId = setTimeout(() => {
                    if (!hasCompleted) {
                        hasCompleted = true;
                        console.warn("reCAPTCHA ha excedido el tiempo máximo de espera (timeout 4s).");
                        showLoginAlert("La verificación de seguridad tardó demasiado. Por favor, verifica tu conexión a internet e inténtalo de nuevo.");
                        restoreButton();
                    }
                }, 4000);

                // Soporte para API tradicional o Enterprise
                const client = (typeof grecaptcha.enterprise !== 'undefined' && typeof grecaptcha.enterprise.execute === 'function')
                    ? grecaptcha.enterprise
                    : grecaptcha;

                client.ready(() => {
                    try {
                        client.execute(siteKey, { action: 'login' })
                            .then((token) => {
                                if (hasCompleted) return;
                                hasCompleted = true;
                                clearTimeout(timeoutId);
                                if (captcha) captcha.value = token;
                                form.submit();
                            })
                            .catch((error) => {
                                if (hasCompleted) return;
                                hasCompleted = true;
                                clearTimeout(timeoutId);
                                console.error("Error al obtener token de reCAPTCHA:", error);
                                showLoginAlert("Error en la verificación de seguridad. Por favor recarga la página o inténtalo nuevamente.");
                                restoreButton();
                            });
                    } catch (innerErr) {
                        if (hasCompleted) return;
                        hasCompleted = true;
                        clearTimeout(timeoutId);
                        console.error("Error síncrono al ejecutar reCAPTCHA:", innerErr);
                        showLoginAlert("No fue posible completar la verificación de seguridad. Recarga la página e intenta de nuevo.");
                        restoreButton();
                    }
                });
            } catch (err) {
                console.error("Error inesperado en flujo de autenticación:", err);
                showLoginAlert("Ocurrió un error inesperado al procesar el inicio de sesión. Inténtalo de nuevo.");
                restoreButton();
            }
        });
    }
});
