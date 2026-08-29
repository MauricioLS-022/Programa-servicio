/**
 * Vino Nuevo - Reportes de Actividad Ministerial
 * Control del modal de detalle, filtros dinámicos y exportación de reportes a PDF/Excel.
 */
document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // 1. FILTROS DINÁMICOS
    // ==========================================
    const filterForm = document.querySelector('.filter-section');
    const redSelect = document.getElementById('filter-red');
    const cdpSelect = document.getElementById('filter-cdp');
    const fechaDesde = document.getElementById('fecha_desde');
    const fechaHasta = document.getElementById('fecha_hasta');
    const searchInput = document.getElementById('filter-search');

    [redSelect, cdpSelect].forEach(select => {
        if (select && filterForm) {
            select.addEventListener('change', () => filterForm.submit());
        }
    });

    if (searchInput && filterForm) {
        searchInput.addEventListener('search', () => filterForm.submit());
    }

    if (fechaDesde && fechaHasta && filterForm) {
        [fechaDesde, fechaHasta].forEach(input => {
            input.addEventListener('change', () => {
                if (fechaDesde.value && fechaHasta.value) {
                    filterForm.submit();
                }
            });
        });
    }

    // ==========================================
    // 2. MODAL DE DETALLES DEL REPORTE
    // ==========================================
    const modal = document.getElementById('reporteModal');
    const modalClose = document.getElementById('modalClose');
    const modalCancel = document.getElementById('modalCancel');
    const modalSave = document.getElementById('modalSave');
    const modalAvatar = document.getElementById('modalAvatar');
    let lastFocusedBtn = null;

    const fields = {
        lider: document.getElementById('modalLider'),
        casa: document.getElementById('modalCasa'),
        fecha: document.getElementById('modalFecha'),
        horaInicio: document.getElementById('modalHoraInicio'),
        horaFin: document.getElementById('modalHoraFin'),
        regulares: document.getElementById('modalRegulares'),
        ninos: document.getElementById('modalNinos'),
        visitas: document.getElementById('modalVisitas'),
        comprometidos: document.getElementById('modalComprometidos'),
        asistencia: document.getElementById('modalAsistencia'),
        reconciliaciones: document.getElementById('modalReconciliaciones'),
        confesiones: document.getElementById('modalConfesiones'),
        ofrendasBs: document.getElementById('modalOfrendasBs'),
        ofrendasUsd: document.getElementById('modalOfrendasUsd'),
        cesta: document.getElementById('modalCesta'),
        tema: document.getElementById('modalTema'),
        obs: document.getElementById('modalObs')
    };

    function calcAsistencia() {
        if (!fields.regulares) return 0;
        const r = parseInt(fields.regulares.value) || 0;
        const n = parseInt(fields.ninos.value) || 0;
        const v = parseInt(fields.visitas.value) || 0;
        const c = parseInt(fields.comprometidos.value) || 0;
        return r + n + v + c;
    }

    function openModal(btn, isEdit) {
        if (!modal) return;
        lastFocusedBtn = btn;

        if (modalAvatar) modalAvatar.textContent = btn.dataset.iniciales || 'CDP';
        if (fields.lider) fields.lider.value = btn.dataset.lider || '';
        if (fields.casa) fields.casa.value = btn.dataset.casa || '';
        if (fields.fecha) fields.fecha.value = btn.dataset.fecha || '';
        if (fields.horaInicio) fields.horaInicio.value = btn.dataset.horaInicio || '';
        if (fields.horaFin) fields.horaFin.value = btn.dataset.horaFin || '';
        if (fields.regulares) fields.regulares.value = btn.dataset.regulares || 0;
        if (fields.ninos) fields.ninos.value = btn.dataset.ninos || 0;
        if (fields.visitas) fields.visitas.value = btn.dataset.visitas || 0;
        if (fields.comprometidos) fields.comprometidos.value = btn.dataset.comprometidos || 0;
        if (fields.reconciliaciones) fields.reconciliaciones.value = btn.dataset.reconciliaciones || 0;
        if (fields.confesiones) fields.confesiones.value = btn.dataset.confesiones || 0;
        if (fields.ofrendasBs) fields.ofrendasBs.value = 'Bs. ' + (parseFloat(btn.dataset.ofrendasBs || 0).toFixed(2));
        if (fields.ofrendasUsd) fields.ofrendasUsd.value = '$' + (parseFloat(btn.dataset.ofrendasUsd || btn.dataset.ofrendas || 0).toFixed(2));
        if (fields.cesta) fields.cesta.value = btn.dataset.cesta || '';
        if (fields.tema) fields.tema.value = btn.dataset.tema || '';
        if (fields.obs) fields.obs.value = btn.dataset.obs || '';

        if (fields.asistencia) fields.asistencia.value = calcAsistencia();

        Object.values(fields).forEach(f => {
            if (f) {
                f.readOnly = !isEdit;
                f.disabled = false;
            }
        });

        if (modalSave) modalSave.style.display = isEdit ? 'flex' : 'none';
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        if (modalClose) modalClose.focus();
    }

    function closeModal() {
        if (!modal) return;
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        if (lastFocusedBtn) {
            lastFocusedBtn.focus();
            lastFocusedBtn = null;
        }
    }

    [fields.regulares, fields.ninos, fields.visitas, fields.comprometidos].forEach(f => {
        if (f) {
            f.addEventListener('input', () => {
                if (fields.asistencia) fields.asistencia.value = calcAsistencia();
            });
        }
    });

    document.querySelectorAll('.btn-view').forEach(btn => {
        btn.addEventListener('click', () => openModal(btn, false));
    });

    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', () => openModal(btn, true));
    });

    if (modalClose) modalClose.addEventListener('click', closeModal);
    if (modalCancel) modalCancel.addEventListener('click', closeModal);
    if (modal) {
        modal.addEventListener('click', e => {
            if (e.target === modal) closeModal();
        });
    }

    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
            closeModal();
        }
    });

    if (modalSave) {
        modalSave.addEventListener('click', () => {
            // Guardar cambios si aplica
            closeModal();
        });
    }

    // ==========================================
    // 3. EXPORTACIÓN DE REPORTES A EXCEL / PDF
    // ==========================================
    const btnExportPdf = document.querySelector('.footer-actions button:first-child');
    const btnExportExcel = document.querySelector('.footer-actions button:last-child');

    if (btnExportExcel) {
        btnExportExcel.addEventListener('click', exportReportsToCSV);
    }

    if (btnExportPdf) {
        btnExportPdf.addEventListener('click', exportReportsToPDF);
    }

    function getReportsData() {
        const table = document.querySelector('table');
        if (!table) return [];

        const rows = table.querySelectorAll('tbody tr');
        const data = [];

        rows.forEach(tr => {
            if (tr.querySelector('.empty-state')) return;
            const fechaEl = tr.querySelector('td[data-label="Fecha"]');
            const liderEl = tr.querySelector('.leader-cell .font-semibold');
            const cdpEl = tr.querySelector('td[data-label="Casa de Paz"]');
            const asisEl = tr.querySelector('td[data-label="Asistencia"] .badge');
            const ofrEl = tr.querySelector('td[data-label="Ofrendas"]');

            data.push({
                fecha: fechaEl ? fechaEl.textContent.trim() : '',
                lider: liderEl ? liderEl.textContent.trim() : '',
                cdp: cdpEl ? cdpEl.textContent.trim() : '',
                asistencia: asisEl ? asisEl.textContent.trim() : '0',
                ofrendas: ofrEl ? ofrEl.textContent.replace('$', '').trim() : '0.00'
            });
        });

        return data;
    }

    function exportReportsToCSV() {
        const data = getReportsData();
        if (!data.length) {
            alert('No hay reportes para exportar.');
            return;
        }

        let csv = '\uFEFF'; // UTF-8 BOM
        csv += 'Fecha,Líder,Casa de Paz,Asistencia,Ofrendas\n';

        data.forEach(item => {
            const fecha = `"${item.fecha.replace(/"/g, '""')}"`;
            const lider = `"${item.lider.replace(/"/g, '""')}"`;
            const cdp = `"${item.cdp.replace(/"/g, '""')}"`;
            const asis = `"${item.asistencia.replace(/"/g, '""')}"`;
            const ofr = `"${item.ofrendas.replace(/"/g, '""')}"`;

            csv += `${fecha},${lider},${cdp},${asis},${ofr}\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const today = new Date().toISOString().split('T')[0];
        a.href = url;
        a.download = `reportes_actividad_${today}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function exportReportsToPDF() {
        const data = getReportsData();
        if (!data.length) {
            alert('No hay reportes para exportar.');
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
        let totalAsis = 0;
        let totalOfr = 0;

        data.forEach(item => {
            const asisNum = parseInt(item.asistencia) || 0;
            const ofrNum = parseFloat(item.ofrendas.replace(/,/g, '')) || 0;
            totalAsis += asisNum;
            totalOfr += ofrNum;

            rowsHtml += `
                <tr>
                    <td>${item.fecha}</td>
                    <td><strong>${item.lider}</strong></td>
                    <td>${item.cdp}</td>
                    <td style="text-align:center;">${item.asistencia}</td>
                    <td style="text-align:right;">$${item.ofrendas}</td>
                </tr>
            `;
        });

        const html = `
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Reportes de Actividad - Vino Nuevo</title>
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
                    .totals-row td {
                        font-weight: 700;
                        background-color: #f8e4e3 !important;
                        color: #390002;
                        border-top: 2px solid #390002;
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
                        <div class="meta">Consolidado de Reportes de Actividad · Casas de Paz</div>
                    </div>
                    <div class="meta">Fecha de emisión: ${today}</div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Líder</th>
                            <th>Casa de Paz</th>
                            <th style="text-align:center;">Asistencia</th>
                            <th style="text-align:right;">Ofrendas</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                        <tr class="totals-row">
                            <td colspan="3">TOTALES REGISTRADOS</td>
                            <td style="text-align:center;">${totalAsis}</td>
                            <td style="text-align:right;">$${totalOfr.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                        </tr>
                    </tbody>
                </table>
                <div class="footer">
                    Documento administrativo de auditoría generado por el sistema de Casas de Paz Vino Nuevo.
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

