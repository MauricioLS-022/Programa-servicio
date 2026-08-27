/**
 * Vino Nuevo - Gestión de Usuarios
 * Filtros dinámicos, modal de confirmación y exportación de datos.
 */
document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.querySelector('.filter-section');
    const roleSelect = document.getElementById('user-role');
    const searchInput = document.getElementById('user-search');
    const deleteModal = document.getElementById('deleteModal');
    const deleteInput = document.getElementById('deleteInput');
    const btnConfirmDelete = document.getElementById('btnConfirmDelete');
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

    // 3. Modal de Eliminación Accesible
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function() {
            activeDeleteBtn = this;
            if (deleteModal) {
                deleteModal.style.display = 'flex';
                deleteModal.setAttribute('aria-hidden', 'false');
                if (deleteInput) {
                    deleteInput.value = '';
                    deleteInput.focus();
                }
                if (btnConfirmDelete) {
                    btnConfirmDelete.disabled = true;
                }
            }
        });
    });

    if (deleteInput && btnConfirmDelete) {
        deleteInput.addEventListener('input', function() {
            btnConfirmDelete.disabled = this.value.trim().toUpperCase() !== 'ELIMINAR';
        });
    }

    window.closeDeleteModal = function() {
        if (deleteModal) {
            deleteModal.style.display = 'none';
            deleteModal.setAttribute('aria-hidden', 'true');
        }
        if (activeDeleteBtn) {
            activeDeleteBtn.focus();
            activeDeleteBtn = null;
        }
    };

    window.confirmDeleteUser = function() {
        if (activeDeleteBtn) {
            const form = activeDeleteBtn.closest('form');
            if (form) {
                form.submit();
            } else {
                const userId = activeDeleteBtn.dataset.id;
                if (userId) {
                    window.location.href = `/admin/usuario/eliminar/${userId}`;
                }
            }
        }
        window.closeDeleteModal();
    };

    if (deleteModal) {
        deleteModal.addEventListener('click', (e) => {
            if (e.target === deleteModal) window.closeDeleteModal();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && deleteModal && deleteModal.style.display === 'flex') {
            window.closeDeleteModal();
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

