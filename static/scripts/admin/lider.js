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

    if (searchInput && filterForm) {
        searchInput.addEventListener('search', () => {
            filterForm.submit();
        });
    }

    // 2. Botones de exportación
    const btnExportPdf = document.querySelector('.footer-actions button:first-child');
    const btnExportExcel = document.querySelector('.footer-actions button:last-child');

    if (btnExportExcel) {
        btnExportExcel.addEventListener('click', exportLeadersToCSV);
    }

    if (btnExportPdf) {
        btnExportPdf.addEventListener('click', exportLeadersToPDF);
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
            const phoneEl = tr.querySelector('td[data-label="Teléfono"]');

            data.push({
                nombre: nameEl ? nameEl.textContent.trim() : '',
                rol: roleEl ? roleEl.textContent.trim() : '',
                red: netEl ? netEl.textContent.trim() : '',
                cdp: cdpEl ? cdpEl.textContent.trim() : '',
                telefono: phoneEl ? phoneEl.textContent.replace('call', '').replace('Llamar', '').trim() : ''
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
});

