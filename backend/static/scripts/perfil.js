/**
 * perfil.js — Interactividad de la página de perfil
 * - Toggle de visibilidad de contraseñas
 * - Indicador de fortaleza de contraseña
 * - Validación de confirmación en tiempo real
 * - Toggle de tema claro/oscuro con persistencia en localStorage
 */
document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. TOGGLE DE VISIBILIDAD DE CONTRASEÑAS
    // =========================================================================
    document.querySelectorAll('.btn-toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const input = document.getElementById(targetId);
            if (!input) return;

            const icon = btn.querySelector('.material-symbols-outlined');
            if (input.type === 'password') {
                input.type = 'text';
                icon.textContent = 'visibility_off';
            } else {
                input.type = 'password';
                icon.textContent = 'visibility';
            }
        });
    });

    // =========================================================================
    // 2. INDICADOR DE FORTALEZA DE CONTRASEÑA
    // =========================================================================
    const passwordNueva = document.getElementById('password_nueva');
    const strengthContainer = document.getElementById('strengthContainer');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');

    if (passwordNueva && strengthContainer) {
        passwordNueva.addEventListener('input', () => {
            const val = passwordNueva.value;
            if (val.length === 0) {
                strengthContainer.style.display = 'none';
                return;
            }
            strengthContainer.style.display = 'flex';

            let score = 0;
            if (val.length >= 6) score++;
            if (val.length >= 10) score++;
            if (/[A-Z]/.test(val)) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;

            const levels = [
                { label: 'Muy débil', color: '#ef4444', width: '20%' },
                { label: 'Débil', color: '#f97316', width: '40%' },
                { label: 'Regular', color: '#eab308', width: '60%' },
                { label: 'Buena', color: '#22c55e', width: '80%' },
                { label: 'Excelente', color: '#16a34a', width: '100%' }
            ];
            const level = levels[Math.min(score, 4)];
            strengthFill.style.width = level.width;
            strengthFill.style.backgroundColor = level.color;
            strengthText.textContent = level.label;
            strengthText.style.color = level.color;

            checkPasswordMatch();
        });
    }

    // =========================================================================
    // 3. VALIDACIÓN DE CONFIRMACIÓN DE CONTRASEÑA
    // =========================================================================
    const passwordConfirmar = document.getElementById('password_confirmar');
    const matchIndicator = document.getElementById('matchIndicator');
    const btnCambiar = document.getElementById('btnCambiarPassword');
    const passwordActual = document.getElementById('password_actual');

    function checkPasswordMatch() {
        if (!passwordNueva || !passwordConfirmar || !matchIndicator || !btnCambiar) return;
        const nueva = passwordNueva.value;
        const confirmar = passwordConfirmar.value;
        const actual = passwordActual ? passwordActual.value : '';

        if (confirmar.length === 0) {
            matchIndicator.style.display = 'none';
            btnCambiar.disabled = true;
            return;
        }
        matchIndicator.style.display = 'inline-flex';

        if (nueva === confirmar) {
            matchIndicator.textContent = '✓ Las contraseñas coinciden';
            matchIndicator.className = 'match-indicator match-success';
            btnCambiar.disabled = !(actual.length > 0 && nueva.length >= 6);
        } else {
            matchIndicator.textContent = '✗ Las contraseñas no coinciden';
            matchIndicator.className = 'match-indicator match-error';
            btnCambiar.disabled = true;
        }
    }

    if (passwordConfirmar) {
        passwordConfirmar.addEventListener('input', checkPasswordMatch);
    }
    if (passwordActual) {
        passwordActual.addEventListener('input', checkPasswordMatch);
    }

    // =========================================================================
    // 4. TOGGLE DE TEMA CLARO / OSCURO
    // =========================================================================
    const themeToggle = document.getElementById('themeToggle');
    const themeModeIcon = document.getElementById('themeModeIcon');
    const themeLabel = document.getElementById('themeLabel');

    function applyTheme(isDark) {
        if (isDark) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            if (themeModeIcon) themeModeIcon.textContent = 'dark_mode';
            if (themeLabel) themeLabel.textContent = 'Tema Oscuro';
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
            if (themeModeIcon) themeModeIcon.textContent = 'light_mode';
            if (themeLabel) themeLabel.textContent = 'Tema Claro';
        }
    }

    // Inicializar estado del toggle basado en localStorage
    const savedTheme = localStorage.getItem('theme');
    const isDark = savedTheme === 'dark';
    if (themeToggle) {
        themeToggle.checked = isDark;
    }
    // Actualizar iconos/labels sin reaplicar el tema (ya aplicado por el script en <head>)
    if (isDark) {
        if (themeModeIcon) themeModeIcon.textContent = 'dark_mode';
        if (themeLabel) themeLabel.textContent = 'Tema Oscuro';
    }

    if (themeToggle) {
        themeToggle.addEventListener('change', () => {
            applyTheme(themeToggle.checked);
        });
    }
});
