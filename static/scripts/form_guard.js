/**
 * form_guard.js - Prevención global de doble envío accidental en formularios.
 * Inhabilita el botón de envío al primer submit válido, muestra un indicador
 * visual de progreso y previene múltiples solicitudes concurrentes al servidor.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Seleccionar todos los formularios POST del sistema
    const forms = document.querySelectorAll('form[method="POST"], form[method="post"], .crud-form, .report-form');

    forms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            // Si el navegador soporta validación nativa y el formulario es inválido, permitir corrección
            if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
                return;
            }

            // Si ya está en proceso de envío, abortar cualquier clic o enter adicional
            if (form.dataset.submitting === 'true') {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }

            // Marcar estado de envío en curso
            form.dataset.submitting = 'true';

            // Localizar el botón de acción principal (submit)
            const submitBtn = (e && e.submitter) || form.querySelector('button[type="submit"], input[type="submit"], .btn-save, .btn-new, .btn-modal-save');
            if (submitBtn) {
                // Guardar contenido original si no se ha guardado
                if (!submitBtn.dataset.originalHtml) {
                    submitBtn.dataset.originalHtml = submitBtn.innerHTML;
                }

                // Detectar si es un botón de sólo icono o acción compacta en tabla
                const originalIcon = submitBtn.querySelector('.material-symbols-outlined');
                const hasOnlyIcon = originalIcon && (submitBtn.textContent.replace(originalIcon.textContent, '').trim() === '');
                const isIconButton = submitBtn.classList.contains('btn-icon') ||
                                     submitBtn.closest('.action-buttons') !== null ||
                                     submitBtn.classList.contains('btn-icon-only') ||
                                     hasOnlyIcon;

                // Aplicar estado visual de carga
                submitBtn.classList.add('is-submitting');
                submitBtn.disabled = true;
                submitBtn.setAttribute('aria-busy', 'true');

                if (isIconButton) {
                    // Mantener clases de color originales del icono (ej. text-primary, text-secondary)
                    const iconColorClass = originalIcon
                        ? Array.from(originalIcon.classList).filter(c => c !== 'material-symbols-outlined').join(' ')
                        : '';
                    // Rueda girando (spinner) sin texto adicional para no alterar el tamaño del botón
                    submitBtn.innerHTML = `<span class="material-symbols-outlined form-guard-spinner ${iconColorClass}" aria-hidden="true">progress_activity</span>`;
                } else {
                    // Determinar texto apropiado según el botón para formularios normales
                    const btnText = submitBtn.textContent.trim().toLowerCase();
                    let loadingText = 'Guardando...';
                    if (btnText.includes('enviar') || btnText.includes('reporte')) {
                        loadingText = 'Enviando...';
                    } else if (btnText.includes('iniciar') || btnText.includes('acceder')) {
                        loadingText = 'Iniciando sesión...';
                    } else if (btnText.includes('eliminar') || btnText.includes('borrar')) {
                        loadingText = 'Eliminando...';
                    } else if (btnText.includes('pausa') || btnText.includes('reactivar') || btnText.includes('desactivar')) {
                        loadingText = 'Actualizando...';
                    }

                    // Renderizar spinner discreto con texto para botones regulares
                    submitBtn.innerHTML = `
                        <span class="material-symbols-outlined form-guard-spinner" aria-hidden="true">progress_activity</span>
                        <span>${loadingText}</span>
                    `;
                }

                // Temporizador de seguridad: Si la red se cae o la descarga tarda más de 10s, restablecer
                setTimeout(function () {
                    if (form.dataset.submitting === 'true') {
                        resetFormButton(form, submitBtn);
                    }
                }, 10000);
            }
        });
    });

    function resetFormButton(form, btn) {
        form.dataset.submitting = 'false';
        if (btn) {
            btn.classList.remove('is-submitting');
            btn.removeAttribute('aria-busy');
            btn.disabled = false;
            if (btn.dataset.originalHtml) {
                btn.innerHTML = btn.dataset.originalHtml;
            }
        }
    }

    // Si el usuario regresa con el botón Atrás del navegador (bfcache), restablecer formularios
    window.addEventListener('pageshow', function (event) {
        forms.forEach(function (form) {
            const submitBtns = form.querySelectorAll('button[type="submit"], input[type="submit"], .btn-save, .btn-new, .btn-modal-save, .btn-icon');
            submitBtns.forEach(function (btn) {
                resetFormButton(form, btn);
            });
        });
    });

    // Alternancia de visibilidad de contraseñas (Toggle Password Visibility) mediante delegación
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.input-wrapper .input-icon.clickable, .btn-toggle-password');
        if (!btn) return;
        e.preventDefault();

        const wrapper = btn.closest('.input-wrapper');
        const input = wrapper ? wrapper.querySelector('input') : document.getElementById(btn.dataset.target);
        if (!input) return;

        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';

        const icon = btn.classList.contains('material-symbols-outlined')
            ? btn
            : btn.querySelector('.material-symbols-outlined');

        if (icon) {
            icon.textContent = isPassword ? 'visibility_off' : 'visibility';
        }
        btn.setAttribute('aria-label', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');
        btn.setAttribute('title', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');
    });

    document.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        const btn = e.target.closest('.input-wrapper .input-icon.clickable, .btn-toggle-password');
        if (!btn) return;
        e.preventDefault();
        btn.click();
    });
});

