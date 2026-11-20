/**
 * Vino Nuevo - Directorio de Liderazgo
 * Filtros automáticos y exportación de datos a Excel/PDF.
 */
document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.querySelector('.filter-section');
    const roleSelect = document.getElementById('leader-role');
    const cdpSelect = document.getElementById('leader-cdp');
    const netSelect = document.getElementById('leader-network');
    const searchInput = document.getElementById('leader-search');

    // 1. Auto-filtrado al cambiar cualquier selector
    [roleSelect, cdpSelect, netSelect].forEach(select => {
        if (select && filterForm) {
            select.addEventListener('change', () => {
                filterForm.submit();
            });
        }
    });

    // 1.5 Live Search client-side instantáneo en directorio de líderes
    if (searchInput) {
        const leaderTableBody = document.querySelector('.leader-table tbody');

        function applyLiveSearchLeaders() {
            if (!leaderTableBody) return;
            const term = searchInput.value.trim().toLowerCase();
            const dataRows = Array.from(leaderTableBody.querySelectorAll('tr')).filter(
                (tr) => !tr.classList.contains('live-search-empty-row') && !tr.querySelector('.empty-state')
            );
            let visibleCount = 0;

            dataRows.forEach((tr) => {
                const text = (tr.textContent || '').toLowerCase();
                const matches = !term || text.includes(term);
                tr.style.display = matches ? '' : 'none';
                if (matches) visibleCount += 1;
            });

            let emptyRow = leaderTableBody.querySelector('.live-search-empty-row');
            if (term && dataRows.length > 0 && visibleCount === 0) {
                if (!emptyRow) {
                    emptyRow = document.createElement('tr');
                    emptyRow.className = 'live-search-empty-row';
                    const colCount = document.querySelectorAll('.leader-table thead th').length || 6;
                    emptyRow.innerHTML = `<td colspan="${colCount}" style="text-align:center;padding:1.5rem;color:var(--text-muted,#666);">No se encontraron líderes en esta página. Presiona Enter para buscar en todo el directorio.</td>`;
                    leaderTableBody.appendChild(emptyRow);
                }
                emptyRow.style.display = '';
            } else if (emptyRow) {
                emptyRow.style.display = 'none';
            }
        }

        searchInput.addEventListener('input', applyLiveSearchLeaders);
        if (filterForm) {
            searchInput.addEventListener('search', () => {
                filterForm.submit();
            });
        }
    }

    // 2. Botones de exportación real server-side con filtros activos
    const btnExportPdf = document.querySelector('.footer-actions button:first-child');
    const btnExportExcel = document.querySelector('.footer-actions button:last-child');

    function buildLeaderExportUrl(format) {
        const params = new URLSearchParams({ format });
        if (searchInput && searchInput.value.trim()) params.set('q', searchInput.value.trim());
        if (roleSelect && roleSelect.value.trim()) params.set('rol', roleSelect.value.trim());
        if (cdpSelect && cdpSelect.value.trim()) params.set('cdp_id', cdpSelect.value.trim());
        if (netSelect && netSelect.value.trim()) params.set('red_id', netSelect.value.trim());
        return `/api/export/lideres?${params.toString()}`;
    }

    if (btnExportExcel) {
        btnExportExcel.addEventListener('click', () => {
            window.location.href = buildLeaderExportUrl('xlsx');
        });
    }

    if (btnExportPdf) {
        btnExportPdf.addEventListener('click', () => {
            window.location.href = buildLeaderExportUrl('csv');
        });
    }

    function getTableData() {
        const table = document.querySelector('.leader-table');
        if (!table) return [];

        const rows = table.querySelectorAll('tbody tr');
        const data = [];

        rows.forEach(tr => {
            if (tr.querySelector('.empty-state')) return;
            const nameEl = tr.querySelector('.leader-cell .font-semibold');
            const roleEl = tr.querySelector('.badge');
            const netEl = tr.querySelector('td[data-label="Red"]');
            const cdpEl = tr.querySelector('td[data-label="Casa de Paz"]');
            const phoneTd = tr.querySelector('td[data-label="Teléfono"]');
            
            let linkPhone = phoneTd ? phoneTd.querySelector('a') : null;
            let telefonoText = '';
            if (linkPhone) {
                telefonoText = (linkPhone.getAttribute('href') || '').replace('tel:', '').trim();
            } else if (phoneTd) {
                telefonoText = phoneTd.textContent.includes('Sin teléfono') ? 'Sin teléfono' : '';
            }

            data.push({
                nombre: nameEl ? nameEl.textContent.trim() : '',
                rol: roleEl ? roleEl.textContent.trim() : '',
                red: netEl ? netEl.textContent.trim() : '',
                cdp: cdpEl ? cdpEl.textContent.trim() : '',
                telefono: telefonoText
            });
        });

        return data;
    }

    function exportLeadersToCSV() {
        const data = getTableData();
        if (!data.length) {
            alert('No hay registros de líderes para exportar.');
            return;
        }

        let csv = '\uFEFF'; // UTF-8 BOM
        csv += 'Nombre,Rol,Red,Casa de Paz,Teléfono\n';

        data.forEach(item => {
            const nombre = `"${item.nombre.replace(/"/g, '""')}"`;
            const rol = `"${item.rol.replace(/"/g, '""')}"`;
            const red = `"${item.red.replace(/"/g, '""')}"`;
            const cdp = `"${item.cdp.replace(/"/g, '""')}"`;
            const telefono = `"${item.telefono.replace(/"/g, '""')}"`;

            csv += `${nombre},${rol},${red},${cdp},${telefono}\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const today = new Date().toISOString().split('T')[0];
        a.href = url;
        a.download = `directorio_lideres_${today}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function exportLeadersToPDF() {
        const data = getTableData();
        if (!data.length) {
            alert('No hay registros de líderes para exportar.');
            return;
        }

        const printWindow = window.open('', '_blank');
        if (!printWindow) {
            alert('Por favor habilite las ventanas emergentes para generar el documento imprimible.');
            return;
        }

        const today = new Date().toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        let rowsHtml = '';
        data.forEach(item => {
            rowsHtml += `
                <tr>
                    <td><strong>${item.nombre}</strong></td>
                    <td>${item.rol}</td>
                    <td>${item.red}</td>
                    <td>${item.cdp}</td>
                    <td>${item.telefono || 'Sin teléfono'}</td>
                </tr>
            `;
        });

        const html = `
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Directorio de Liderazgo - Vino Nuevo</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        color: #2b1111;
                        padding: 30px;
                        margin: 0;
                    }
                    .header {
                        border-bottom: 2px solid #390002;
                        padding-bottom: 15px;
                        margin-bottom: 20px;
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-end;
                    }
                    h1 {
                        color: #390002;
                        font-size: 24px;
                        margin: 0 0 5px 0;
                    }
                    .meta {
                        font-size: 13px;
                        color: #564240;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 15px;
                        font-size: 13px;
                    }
                    th {
                        background-color: #f8e4e3;
                        color: #390002;
                        font-weight: 700;
                        text-align: left;
                        padding: 10px 12px;
                        border-bottom: 1px solid #ddc0bd;
                    }
                    td {
                        padding: 10px 12px;
                        border-bottom: 1px solid #eee;
                    }
                    tr:nth-child(even) td {
                        background-color: #faf7f7;
                    }
                    .footer {
                        margin-top: 30px;
                        font-size: 11px;
                        color: #888;
                        text-align: center;
                        border-top: 1px solid #ddd;
                        padding-top: 10px;
                    }
                    @media print {
                        body { padding: 0; }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div>
                        <h1>Comunidad Cristiana Vino Nuevo</h1>
                        <div class="meta">Directorio de Liderazgo · Red de Casas de Paz</div>
                    </div>
                    <div class="meta">Fecha de emisión: ${today}</div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Nombre del Líder</th>
                            <th>Rol</th>
                            <th>Red</th>
                            <th>Casa de Paz</th>
                            <th>Teléfono</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
                <div class="footer">
                    Documento administrativo generado por el sistema de Casas de Paz Vino Nuevo.
                </div>
                <script>
                    window.onload = function() {
                        window.print();
                    };
                </script>
            </body>
            </html>
        `;

        printWindow.document.open();
        printWindow.document.write(html);
        printWindow.document.close();
    }

    // 3. Modal de Eliminación de Líder
    const deleteModal = document.getElementById('deleteModal');
    const deleteInput = document.getElementById('deleteInput');
    const deleteLeaderName = document.getElementById('deleteLeaderName');
    const deleteLeaderForm = document.getElementById('deleteLeaderForm');
    const btnConfirmDelete = document.getElementById('btnConfirmDelete');
    let activeDeleteBtn = null;

    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function() {
            activeDeleteBtn = this;
            const liderId = this.getAttribute('data-id');
            const liderNombre = this.getAttribute('data-nombre');

            if (deleteLeaderName) deleteLeaderName.textContent = liderNombre || 'este líder';
            if (deleteLeaderForm) deleteLeaderForm.action = `/admin/lider/${liderId}/eliminar`;

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

    document.querySelectorAll('[data-close-delete-modal]').forEach(btn => {
        btn.addEventListener('click', () => window.closeDeleteModal());
    });

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
});
