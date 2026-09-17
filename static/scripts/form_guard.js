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
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"], .btn-save, .btn-new, .btn-modal-save');
            if (submitBtn) {
                // Guardar contenido original si no se ha guardado
                if (!submitBtn.dataset.originalHtml) {
                    submitBtn.dataset.originalHtml = submitBtn.innerHTML;
                }

                // Determinar texto apropiado según el botón
                const btnText = submitBtn.textContent.trim().toLowerCase();
                let loadingText = 'Guardando...';
                if (btnText.includes('enviar') || btnText.includes('reporte')) {
                    loadingText = 'Enviando...';
                } else if (btnText.includes('iniciar') || btnText.includes('acceder')) {
                    loadingText = 'Iniciando sesión...';
                }

                // Aplicar estado visual de carga
                submitBtn.classList.add('is-submitting');
                submitBtn.disabled = true;

                // Renderizar spinner discreto
                submitBtn.innerHTML = `
                    <span class="material-symbols-outlined form-guard-spinner" aria-hidden="true">progress_activity</span>
                    <span>${loadingText}</span>
                `;

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
            btn.disabled = false;
            if (btn.dataset.originalHtml) {
                btn.innerHTML = btn.dataset.originalHtml;
            }
        }
    }

    // Si el usuario regresa con el botón Atrás del navegador (bfcache), restablecer formularios
    window.addEventListener('pageshow', function (event) {
        forms.forEach(function (form) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"], .btn-save, .btn-new, .btn-modal-save');
            resetFormButton(form, submitBtn);
        });
    });
});

