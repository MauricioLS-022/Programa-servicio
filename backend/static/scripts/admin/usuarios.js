/**
 * Vino Nuevo - Gestión de Usuarios
 * Filtros dinámicos, modal de confirmación y exportación de datos.
 */
document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.querySelector('.filter-section');
    const roleSelect = document.getElementById('user-role');
    const searchInput = document.getElementById('user-search');
    const deleteModal = document.getElementById('deleteModal');
    let activeDeleteBtn = null;

    // 1. Auto-filtrado al cambiar rol
    if (roleSelect && filterForm) {
        roleSelect.addEventListener('change', () => {
            filterForm.submit();
        });
    }

    // 2. Debounce en búsqueda para envío rápido al presionar Enter o limpiar
    if (searchInput && filterForm) {
        searchInput.addEventListener('search', () => {
            filterForm.submit();
        });
    }

    // 3. Modales de Eliminación (Bloqueo por dependencias y Confirmación con 'ELIMINAR')
    const deleteBlockedModal = document.getElementById('deleteBlockedModal');
    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    const deleteInput = document.getElementById('deleteInput');
    const btnConfirmDelete = document.getElementById('btnConfirmDelete');
    const formEliminar = document.getElementById('formEliminarUsuario');

    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function() {
            activeDeleteBtn = this;
            const isSelf = this.dataset.isSelf === 'true';
            const redNombre = (this.dataset.red || '').trim();
            const cdpCodigo = (this.dataset.cdp || '').trim();
            const nombre = (this.dataset.nombre || 'este usuario').trim();
            const deleteUrl = this.dataset.deleteUrl;

            if (isSelf || redNombre || cdpCodigo) {
                // Caso Bloqueado: cuenta propia, red vinculada o cdp vinculada
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
                // Caso Permitido: sin dependencias
                const nameEl = document.getElementById('deleteUserName');
                if (nameEl) nameEl.textContent = nombre;
                if (formEliminar && deleteUrl) formEliminar.action = deleteUrl;

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
    });

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
        if (activeDeleteBtn) {
            activeDeleteBtn.focus();
            activeDeleteBtn = null;
        }
    };

    window.confirmDeleteUser = function() {
        if (formEliminar && formEliminar.action) {
            formEliminar.submit();
        } else if (activeDeleteBtn) {
            const form = activeDeleteBtn.closest('form');
            if (form) {
                form.submit();
            } else {
                const deleteUrl = activeDeleteBtn.dataset.deleteUrl;
                if (deleteUrl) {
                    window.location.href = deleteUrl;
                }
            }
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

    // 4. Exportación a CSV / Excel
    const btnExport = document.getElementById('btnExportUsers');
    if (btnExport) {
        btnExport.addEventListener('click', exportUsersToCSV);
    }

    function exportUsersToCSV() {
        const table = document.querySelector('.user-table');
        if (!table) return;

        const rows = table.querySelectorAll('tbody tr');
        if (!rows.length || (rows.length === 1 && rows[0].querySelector('.empty-state'))) {
            alert('No hay usuarios para exportar.');
            return;
        }

        let csv = '\uFEFF'; // UTF-8 BOM para soporte de tildes y caracteres en Excel
        csv += 'Usuario,Username,Rol,Estado\n';

        rows.forEach(tr => {
            if (tr.querySelector('.empty-state')) return;
            const nameEl = tr.querySelector('.user-details strong');
            const usernameEl = tr.querySelector('.text-muted');
            const roleEl = tr.querySelector('.badge');
            const statusEl = tr.querySelector('.status span:last-child');

            const name = nameEl ? `"${nameEl.textContent.trim().replace(/"/g, '""')}"` : '""';
            const username = usernameEl ? `"${usernameEl.textContent.trim().replace('@', '').replace(/"/g, '""')}"` : '""';
            const role = roleEl ? `"${roleEl.textContent.trim().replace(/"/g, '""')}"` : '""';
            const status = statusEl ? `"${statusEl.textContent.trim().replace(/"/g, '""')}"` : '""';

            csv += `${name},${username},${role},${status}\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const today = new Date().toISOString().split('T')[0];
        a.href = url;
        a.download = `directorio_usuarios_${today}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
});

