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

    // 2. Live Search client-side instantáneo + envío server-side con Enter o limpiar
    if (searchInput) {
        const userTableBody = document.querySelector('.user-table tbody');

        function applyLiveSearchUsers() {
            if (!userTableBody) return;
            const term = searchInput.value.trim().toLowerCase();
            const dataRows = Array.from(userTableBody.querySelectorAll('tr')).filter(
                (tr) => !tr.classList.contains('live-search-empty-row') && !tr.querySelector('.empty-state')
            );
            let visibleCount = 0;

            dataRows.forEach((tr) => {
                const text = (tr.textContent || '').toLowerCase();
                const matches = !term || text.includes(term);
                tr.style.display = matches ? '' : 'none';
                if (matches) visibleCount += 1;
            });

            let emptyRow = userTableBody.querySelector('.live-search-empty-row');
            if (term && dataRows.length > 0 && visibleCount === 0) {
                if (!emptyRow) {
                    emptyRow = document.createElement('tr');
                    emptyRow.className = 'live-search-empty-row';
                    emptyRow.innerHTML = '<td colspan="5" style="text-align:center;padding:1.5rem;color:var(--text-muted,#666);">No se encontraron usuarios en esta página. Presiona Enter para buscar en todo el directorio.</td>';
                    userTableBody.appendChild(emptyRow);
                }
                emptyRow.style.display = '';
            } else if (emptyRow) {
                emptyRow.style.display = 'none';
            }
        }

        searchInput.addEventListener('input', applyLiveSearchUsers);
        if (filterForm) {
            searchInput.addEventListener('search', () => {
                filterForm.submit();
            });
        }
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

    document.querySelectorAll('[data-close-delete-modal]').forEach(btn => {
        btn.addEventListener('click', () => window.closeDeleteModal());
    });

    if (btnConfirmDelete) {
        btnConfirmDelete.addEventListener('click', () => {
            if (!btnConfirmDelete.disabled) window.confirmDeleteUser();
        });
    }

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

    // 4. Exportación real server-side a Excel (.xlsx) con filtros activos
    const btnExport = document.getElementById('btnExportUsers');
    if (btnExport) {
        btnExport.addEventListener('click', () => {
            const params = new URLSearchParams({ format: 'xlsx' });
            if (searchInput && searchInput.value.trim()) {
                params.set('q', searchInput.value.trim());
            }
            if (roleSelect && roleSelect.value.trim()) {
                params.set('rol', roleSelect.value.trim());
            }
            window.location.href = `/api/export/usuarios?${params.toString()}`;
        });
    }
});

