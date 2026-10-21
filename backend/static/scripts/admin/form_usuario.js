// Gestión de visibilidad de asignación de Red / Casa de Paz según el rol seleccionado en el formulario de usuario.
document.addEventListener('DOMContentLoaded', () => {
    const rolSelect = document.getElementById('rol');
    const grupoRed = document.getElementById('grupo-asignacion-red');
    const grupoCdp = document.getElementById('grupo-asignacion-cdp');

    function actualizarVisibilidadAsignacion() {
        if (!rolSelect) return;
        const rol = rolSelect.value;
        if (grupoRed) {
            grupoRed.style.display = (rol === 'supervisor') ? 'block' : 'none';
            if (rol !== 'supervisor') {
                const sel = grupoRed.querySelector('select');
                if (sel) sel.value = '';
            }
        }
        if (grupoCdp) {
            grupoCdp.style.display = (rol === 'lider_cdp') ? 'block' : 'none';
            if (rol !== 'lider_cdp') {
                const sel = grupoCdp.querySelector('select');
                if (sel) sel.value = '';
            }
        }
    }

    if (rolSelect) {
        rolSelect.addEventListener('change', actualizarVisibilidadAsignacion);
        actualizarVisibilidadAsignacion();
    }

    // Modales de Eliminación de Usuario en Formulario (Bloqueo o Confirmación con 'ELIMINAR')
    const btnDelete = document.getElementById('btnDeleteUserForm') || document.querySelector('.btn-delete-text');
    const deleteBlockedModal = document.getElementById('deleteBlockedModal');
    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    const deleteInput = document.getElementById('deleteInput');
    const btnConfirmDelete = document.getElementById('btnConfirmDelete');
    const formEliminar = document.getElementById('formEliminarUsuario');

    if (btnDelete) {
        btnDelete.addEventListener('click', function() {
            const isSelf = this.dataset.isSelf === 'true';
            const redNombre = (this.dataset.red || '').trim();
            const cdpCodigo = (this.dataset.cdp || '').trim();
            const nombre = (this.dataset.nombre || 'este usuario').trim();

            if (isSelf || redNombre || cdpCodigo) {
                // Bloqueado: cuenta propia, supervisor de red o líder con CDP
                const reasonEl = document.getElementById('deleteBlockedReason');
                const hintEl = document.getElementById('deleteBlockedHint');

                if (isSelf) {
                    if (reasonEl) reasonEl.innerHTML = `No puedes eliminar tu propia cuenta de usuario en sesión (<strong>${nombre}</strong>).`;
                    if (hintEl) hintEl.textContent = 'Por razones de seguridad del sistema, otro administrador debe gestionar tu cuenta si es necesario.';
                } else if (redNombre) {
                    if (reasonEl) reasonEl.innerHTML = `El usuario <strong>${nombre}</strong> es actualmente supervisor de la red ministerial <strong>${redNombre}</strong>.`;
                    if (hintEl) hintEl.textContent = 'Para poder eliminarlo, primero debes reasignar o desvincular la red desde la vista de estructura.';
                } else if (cdpCodigo) {
                    if (reasonEl) reasonEl.innerHTML = `El usuario <strong>${nombre}</strong> tiene asignada la Casa de Paz <strong>${cdpCodigo}</strong>.`;
                    if (hintEl) hintEl.textContent = 'Para poder eliminarlo, primero debes reasignar o desvincular la cuenta en la gestión de la Casa de Paz.';
                }

                if (deleteBlockedModal) {
                    deleteBlockedModal.style.display = 'flex';
                    deleteBlockedModal.setAttribute('aria-hidden', 'false');
                }
            } else {
                // Permitido: abre modal de confirmación
                if (deleteConfirmModal) {
                    deleteConfirmModal.style.display = 'flex';
                    deleteConfirmModal.setAttribute('aria-hidden', 'false');
                    if (deleteInput) {
                        deleteInput.value = '';
                        setTimeout(() => deleteInput.focus(), 50);
                    }
                    if (btnConfirmDelete) {
                        btnConfirmDelete.disabled = true;
                    }
                }
            }
        });
    }

    if (deleteInput && btnConfirmDelete) {
        deleteInput.addEventListener('input', function() {
            btnConfirmDelete.disabled = this.value.trim().toUpperCase() !== 'ELIMINAR';
        });
        deleteInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !btnConfirmDelete.disabled) {
                e.preventDefault();
                window.confirmDeleteUser();
            }
        });
    }

    window.closeDeleteModal = function() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        });
        if (btnDelete) btnDelete.focus();
    };

    window.confirmDeleteUser = function() {
        if (formEliminar) {
            formEliminar.submit();
        }
        window.closeDeleteModal();
    };

    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) window.closeDeleteModal();
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal-overlay[style*="display: flex"]');
            if (openModal) window.closeDeleteModal();
        }
    });
});
