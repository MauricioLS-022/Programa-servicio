/**
 * static/scripts/admin/detalles_cdp.js
 * Generación y exportación de Ficha Técnica Oficial de Casa de Paz a PDF.
 * Comunidad Cristiana Vino Nuevo.
 */

(function () {
    'use strict';

    /**
     * Extrae de forma segura el texto de un ítem de información en base a su etiqueta.
     */
    function getInfoItemValue(labelText) {
        const items = document.querySelectorAll('.info-card .info-item');
        for (const item of items) {
            const label = item.querySelector('.info-label');
            if (label && label.textContent.trim().toLowerCase().includes(labelText.toLowerCase())) {
                const valEl = item.querySelector('.info-value');
                return valEl ? valEl.textContent.trim().replace(/\s+/g, ' ') : '';
            }
        }
        return '';
    }

    /**
     * Recopila todos los datos estructurados visibles en la vista de detalle.
     */
    function getCdpData() {
        // 1. Encabezado principal
        const titleEl = document.querySelector('.detail-title');
        let codigo = titleEl ? titleEl.textContent.trim() : 'CDP';
        codigo = codigo.replace(/^Casa\s*["“]?/i, '').replace(/["”]?$/, '').trim();

        const redEl = document.querySelector('.badge-network');
        const red = redEl ? redEl.textContent.trim() : '';

        const subtitleEl = document.querySelector('.detail-subtitle strong');
        const supervisor = subtitleEl ? subtitleEl.textContent.trim() : 'Sin asignar';

        const statusPill = document.querySelector('.status-pill');
        const estado = statusPill ? statusPill.textContent.trim() : 'Activa';
        const isActiva = statusPill ? !statusPill.classList.contains('inactiva') : true;

        // 2. Información del centro
        const direccion = getInfoItemValue('Dirección') || 'No registrada';
        const anfitrion = getInfoItemValue('Anfitrión') || 'Sin anfitrión asignado';
        const usuarioSistema = getInfoItemValue('Usuario del Sistema') || 'Sin cuenta vinculada';
        const liderAsignado = getInfoItemValue('Líder Asignado') || 'Sin líder asignado';
        const telefono = getInfoItemValue('Teléfono de la Casa') || 'No registrado';
        const horario = getInfoItemValue('Horario de Reunión') || 'Miércoles · 7:00 PM';
        const estadoReporte = getInfoItemValue('Reporte Semanal') || 'Al día';

        // 3. Métricas clave (KPIs)
        const metricCards = document.querySelectorAll('.metrics-grid .metric-card');
        const kpis = {
            asistenciaProm: '0',
            reportesTotales: '0',
            ofrendasUsd: '$0.00',
            ofrendasBs: 'Bs. 0.00',
            visitas: '0',
            crecimientoSub: '0 conversiones'
        };

        if (metricCards.length >= 4) {
            kpis.asistenciaProm = metricCards[0].querySelector('.metric-value')?.textContent.trim() || '0';
            kpis.reportesTotales = metricCards[1].querySelector('.metric-value')?.textContent.trim() || '0';

            const ofrVal = metricCards[2].querySelector('.metric-value')?.textContent.trim() || '$0.00';
            const ofrSub = metricCards[2].querySelector('.metric-subtext')?.textContent.trim() || 'Bs. 0.00';
            kpis.ofrendasUsd = ofrVal;
            kpis.ofrendasBs = ofrSub;

            kpis.visitas = metricCards[3].querySelector('.metric-value')?.textContent.trim() || '0';
            kpis.crecimientoSub = metricCards[3].querySelector('.metric-subtext')?.textContent.trim() || '0 conversiones';
        }

        // 4. Equipo de líderes
        const teamMembers = [];
        const memberEls = document.querySelectorAll('.team-card .team-member');
        memberEls.forEach(function (m) {
            const nameEl = m.querySelector('.team-member-info strong');
            const roleEl = m.querySelector('.team-member-info p');
            const phoneEl = m.querySelector('.member-phone');
            if (nameEl) {
                teamMembers.push({
                    nombre: nameEl.textContent.trim(),
                    rol: roleEl ? roleEl.textContent.trim() : 'Líder',
                    telefono: phoneEl ? phoneEl.textContent.trim() : 'No registrado'
                });
            }
        });

        // 5. Historial reciente de reportes
        const reportes = [];
        const rows = document.querySelectorAll('.reports-table tbody tr');
        rows.forEach(function (tr) {
            const dateEl = tr.querySelector('.td-date strong') || tr.querySelector('.td-date');
            const themeEl = tr.querySelector('.td-theme strong');
            const obsEl = tr.querySelector('.td-theme .report-note');
            const asisEl = tr.querySelector('.td-attendance');
            const breakEl = tr.querySelector('.td-breakdown');
            const ofrEl = tr.querySelector('.td-offering');
            const cestaEl = tr.querySelector('.td-cesta');

            if (dateEl) {
                let ofrendaTxt = ofrEl ? ofrEl.textContent.trim().replace(/\s+/g, ' ') : '$0.00';
                let cestaTxt = cestaEl && cestaEl.textContent.includes('Sí') ? 'Sí' : 'No';

                reportes.push({
                    fecha: dateEl.textContent.trim(),
                    tema: themeEl ? themeEl.textContent.trim() : 'Sin tema registrado',
                    obs: obsEl ? obsEl.textContent.trim() : '',
                    asistencia: asisEl ? asisEl.textContent.trim().replace(/\s*pers\.?/i, '') : '0',
                    desglose: breakEl ? breakEl.textContent.trim().replace(/\s+/g, ' ') : '',
                    ofrenda: ofrendaTxt,
                    cesta: cestaTxt
                });
            }
        });

        return {
            codigo: codigo,
            red: red,
            supervisor: supervisor,
            estado: estado,
            isActiva: isActiva,
            direccion: direccion,
            anfitrion: anfitrion,
            usuarioSistema: usuarioSistema,
            liderAsignado: liderAsignado,
            telefono: telefono,
            horario: horario,
            estadoReporte: estadoReporte,
            kpis: kpis,
            teamMembers: teamMembers,
            reportes: reportes
        };
    }

    /**
     * Construye el HTML completo de la Ficha Técnica para impresión o guardado como PDF.
     */
    function buildFichaHtml(data) {
        const today = new Date().toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        let teamHtml = '';
        if (data.teamMembers.length > 0) {
            data.teamMembers.forEach(function (m) {
                teamHtml += `
                    <tr>
                        <td><strong>${escapeHtml(m.nombre)}</strong></td>
                        <td>${escapeHtml(m.rol)}</td>
                        <td>${escapeHtml(m.telefono)}</td>
                    </tr>
                `;
            });
        } else {
            teamHtml = `
                <tr>
                    <td colspan="3" style="text-align: center; color: #888; padding: 12px;">
                        No hay líderes registrados en el equipo de esta Casa de Paz.
                    </td>
                </tr>
            `;
        }

        let reportesHtml = '';
        let totalAsistencia = 0;

        if (data.reportes.length > 0) {
            data.reportes.forEach(function (r) {
                const asisNum = parseInt(r.asistencia, 10) || 0;
                totalAsistencia += asisNum;

                reportesHtml += `
                    <tr>
                        <td><strong>${escapeHtml(r.fecha)}</strong></td>
                        <td>
                            <strong>${escapeHtml(r.tema)}</strong>
                            ${r.obs ? `<div style="font-size: 10px; color: #666; margin-top: 2px;">${escapeHtml(r.obs)}</div>` : ''}
                        </td>
                        <td style="text-align: center;"><strong>${escapeHtml(r.asistencia)}</strong></td>
                        <td style="font-size: 11px;">${escapeHtml(r.desglose)}</td>
                        <td>${escapeHtml(r.ofrenda)}</td>
                        <td style="text-align: center;">${escapeHtml(r.cesta)}</td>
                    </tr>
                `;
            });
        } else {
            reportesHtml = `
                <tr>
                    <td colspan="6" style="text-align: center; color: #888; padding: 12px;">
                        No se han registrado reportes aún para esta Casa de Paz.
                    </td>
                </tr>
            `;
        }

        return `
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Ficha Técnica Oficial - Casa de Paz ${escapeHtml(data.codigo)}</title>
                <style>
                    @page {
                        size: letter portrait;
                        margin: 12mm 15mm;
                    }
                    * {
                        box-sizing: border-box;
                    }
                    body {
                        font-family: 'Segoe UI', Arial, -apple-system, sans-serif;
                        color: #2b1111;
                        background: #ffffff;
                        padding: 15px;
                        margin: 0;
                        font-size: 12px;
                        line-height: 1.4;
                    }

                    .doc-header {
                        border-bottom: 2.5px solid #390002;
                        padding-bottom: 12px;
                        margin-bottom: 16px;
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-end;
                    }
                    .brand-title {
                        font-size: 22px;
                        font-weight: 800;
                        color: #390002;
                        margin: 0 0 2px 0;
                        letter-spacing: -0.02em;
                    }
                    .brand-subtitle {
                        font-size: 12px;
                        color: #564240;
                        text-transform: uppercase;
                        letter-spacing: 0.08em;
                        font-weight: 600;
                    }
                    .meta-block {
                        text-align: right;
                        font-size: 11px;
                        color: #564240;
                    }
                    .status-badge {
                        display: inline-block;
                        padding: 2px 8px;
                        border-radius: 999px;
                        font-weight: 700;
                        font-size: 10px;
                        text-transform: uppercase;
                        margin-top: 4px;
                    }
                    .status-badge.activa {
                        background: #dcfce7;
                        color: #15803d;
                        border: 1px solid #86efac;
                    }
                    .status-badge.inactiva {
                        background: #fee2e2;
                        color: #991b1b;
                        border: 1px solid #fca5a5;
                    }

                    .section {
                        margin-bottom: 16px;
                    }
                    .section-title {
                        font-size: 13px;
                        font-weight: 700;
                        color: #390002;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                        border-bottom: 1px solid #e8d0cc;
                        padding-bottom: 4px;
                        margin: 0 0 8px 0;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }

                    .info-grid {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 11.5px;
                        margin-bottom: 14px;
                    }
                    .info-grid td {
                        padding: 5px 8px;
                        vertical-align: top;
                        border-bottom: 1px solid #f3ebe9;
                    }
                    .info-grid .field-label {
                        width: 25%;
                        font-weight: 700;
                        color: #5a4240;
                        text-transform: uppercase;
                        font-size: 10px;
                        letter-spacing: 0.03em;
                    }
                    .info-grid .field-value {
                        width: 25%;
                        color: #2b1111;
                    }

                    .kpi-container {
                        display: flex;
                        gap: 8px;
                        margin-bottom: 16px;
                    }
                    .kpi-box {
                        flex: 1;
                        background: #faf5f3;
                        border: 1px solid #e8d0cc;
                        border-radius: 6px;
                        padding: 8px 10px;
                        text-align: center;
                    }
                    .kpi-box .kpi-label {
                        font-size: 9.5px;
                        text-transform: uppercase;
                        font-weight: 700;
                        color: #5a4240;
                        margin-bottom: 3px;
                    }
                    .kpi-box .kpi-val {
                        font-size: 16px;
                        font-weight: 800;
                        color: #390002;
                        line-height: 1.1;
                    }
                    .kpi-box .kpi-sub {
                        font-size: 9.5px;
                        color: #700204;
                        margin-top: 2px;
                        font-weight: 600;
                    }

                    table.data-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 11px;
                        margin-bottom: 8px;
                    }
                    table.data-table th {
                        background-color: #f8e4e3;
                        color: #390002;
                        font-weight: 700;
                        text-align: left;
                        padding: 6px 8px;
                        border-bottom: 1.5px solid #ddc0bd;
                        font-size: 10.5px;
                        text-transform: uppercase;
                        letter-spacing: 0.03em;
                    }
                    table.data-table td {
                        padding: 6px 8px;
                        border-bottom: 1px solid #eee;
                    }
                    table.data-table tr:nth-child(even) td {
                        background-color: #faf7f7;
                    }
                    .totals-row td {
                        background-color: #f8e4e3 !important;
                        color: #390002;
                        font-weight: 700;
                        border-top: 1.5px solid #390002;
                    }

                    .audit-section {
                        margin-top: 24px;
                        padding-top: 14px;
                        border-top: 1px solid #ddd;
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-end;
                        font-size: 10px;
                        color: #666;
                        break-inside: avoid;
                        page-break-inside: avoid;
                    }
                    .signature-box {
                        text-align: center;
                        width: 220px;
                    }
                    .signature-line {
                        border-top: 1px solid #2b1111;
                        margin-bottom: 4px;
                        height: 1px;
                    }
                    .signature-name {
                        font-weight: 700;
                        color: #2b1111;
                        font-size: 11px;
                    }
                    .signature-role {
                        font-size: 9.5px;
                        color: #555;
                    }

                    @media print {
                        body {
                            padding: 0;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="doc-header">
                    <div>
                        <div class="brand-title">Comunidad Cristiana Vino Nuevo</div>
                        <div class="brand-subtitle">Ficha Técnica Oficial · Red de Casas de Paz</div>
                    </div>
                    <div class="meta-block">
                        <div><strong>Emisión:</strong> ${today}</div>
                        <div>
                            <span class="status-badge ${data.isActiva ? 'activa' : 'inactiva'}">
                                ${escapeHtml(data.estado)}
                            </span>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">
                        <span>1. Identificación y Ubicación del Centro</span>
                        <span>Casa "${escapeHtml(data.codigo)}"</span>
                    </div>
                    <table class="info-grid">
                        <tr>
                            <td class="field-label">Código Oficial:</td>
                            <td class="field-value"><strong>${escapeHtml(data.codigo)}</strong></td>
                            <td class="field-label">Red Ministerial:</td>
                            <td class="field-value"><strong>${escapeHtml(data.red)}</strong></td>
                        </tr>
                        <tr>
                            <td class="field-label">Supervisor de Red:</td>
                            <td class="field-value">${escapeHtml(data.supervisor)}</td>
                            <td class="field-label">Líder Asignado:</td>
                            <td class="field-value">${escapeHtml(data.liderAsignado)}</td>
                        </tr>
                        <tr>
                            <td class="field-label">Anfitrión del Hogar:</td>
                            <td class="field-value">${escapeHtml(data.anfitrion)}</td>
                            <td class="field-label">Teléfono de Contacto:</td>
                            <td class="field-value">${escapeHtml(data.telefono)}</td>
                        </tr>
                        <tr>
                            <td class="field-label">Dirección Física:</td>
                            <td class="field-value">${escapeHtml(data.direccion)}</td>
                            <td class="field-label">Horario de Reunión:</td>
                            <td class="field-value"><strong>${escapeHtml(data.horario)}</strong></td>
                        </tr>
                        <tr>
                            <td class="field-label">Cuenta de Usuario:</td>
                            <td class="field-value">${escapeHtml(data.usuarioSistema)}</td>
                            <td class="field-label">Estado Semanal:</td>
                            <td class="field-value">${escapeHtml(data.estadoReporte)}</td>
                        </tr>
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">2. Resumen de Desempeño y Crecimiento</div>
                    <div class="kpi-container">
                        <div class="kpi-box">
                            <div class="kpi-label">Asistencia Prom.</div>
                            <div class="kpi-val">${escapeHtml(data.kpis.asistenciaProm)}</div>
                            <div class="kpi-sub">personas / reunión</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-label">Reportes Enviados</div>
                            <div class="kpi-val">${escapeHtml(data.kpis.reportesTotales)}</div>
                            <div class="kpi-sub">semanas registradas</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-label">Ofrendas Totales</div>
                            <div class="kpi-val">${escapeHtml(data.kpis.ofrendasUsd)}</div>
                            <div class="kpi-sub">${escapeHtml(data.kpis.ofrendasBs)}</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-label">Visitas & Conversiones</div>
                            <div class="kpi-val">${escapeHtml(data.kpis.visitas)}</div>
                            <div class="kpi-sub">${escapeHtml(data.kpis.crecimientoSub)}</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">
                        <span>3. Equipo de Liderazgo Responsable</span>
                        <span style="font-weight: normal; font-size: 10px;">${data.teamMembers.length} integrantes</span>
                    </div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th style="width: 45%;">Nombre Completo</th>
                                <th style="width: 30%;">Rol en la Casa</th>
                                <th style="width: 25%;">Teléfono de Contacto</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${teamHtml}
                        </tbody>
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">
                        <span>4. Historial Reciente de Reuniones y Reportes</span>
                        <span style="font-weight: normal; font-size: 10px;">Últimas semanas</span>
                    </div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th style="width: 14%;">Fecha</th>
                                <th style="width: 34%;">Tema de la Reunión</th>
                                <th style="width: 12%; text-align: center;">Asistencia</th>
                                <th style="width: 18%;">Desglose</th>
                                <th style="width: 14%;">Ofrendas</th>
                                <th style="width: 8%; text-align: center;">Cesta</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${reportesHtml}
                            ${data.reportes.length > 0 ? `
                                <tr class="totals-row">
                                    <td colspan="2">TOTAL REGISTRADO EN HISTORIAL</td>
                                    <td style="text-align: center;">${totalAsistencia}</td>
                                    <td colspan="3">${escapeHtml(data.kpis.ofrendasUsd)} · ${escapeHtml(data.kpis.ofrendasBs)}</td>
                                </tr>
                            ` : ''}
                        </tbody>
                    </table>
                </div>

                <div class="audit-section">
                    <div>
                        <strong>Vino Nuevo · Sistema de Supervisión y Gestión de Casas de Paz</strong><br>
                        Ficha técnica oficial generada para propósitos administrativos y de seguimiento pastoral.<br>
                        Fecha de emisión: ${today}.
                    </div>
                    <div class="signature-box">
                        <div class="signature-line"></div>
                        <div class="signature-name">${escapeHtml(data.supervisor)}</div>
                        <div class="signature-role">Supervisor de Red · ${escapeHtml(data.red)}</div>
                    </div>
                </div>
            </body>
            </html>
        `;
    }

    /**
     * Utilidad para evitar inyección en la plantilla impresa.
     */
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    let isExporting = false;

    /**
     * Función principal invocable globalmente.
     */
    window.exportCdpToPDF = function exportCdpToPDF(event) {
        if (event && typeof event.preventDefault === 'function') {
            event.preventDefault();
        }

        if (isExporting) {
            return;
        }
        isExporting = true;
        setTimeout(function () {
            isExporting = false;
        }, 1500);

        try {
            const data = getCdpData();
            const html = buildFichaHtml(data);

            // Remover iframe previo para evitar eventos residuales
            const oldIframe = document.getElementById('print-cdp-iframe');
            if (oldIframe) {
                oldIframe.remove();
            }

            // Crear iframe limpio e invisible
            const printIframe = document.createElement('iframe');
            printIframe.id = 'print-cdp-iframe';
            printIframe.style.position = 'fixed';
            printIframe.style.right = '0';
            printIframe.style.bottom = '0';
            printIframe.style.width = '0';
            printIframe.style.height = '0';
            printIframe.style.border = '0';
            printIframe.style.visibility = 'hidden';
            document.body.appendChild(printIframe);

            const frameDoc = printIframe.contentWindow.document;
            frameDoc.open();
            frameDoc.write(html);
            frameDoc.close();

            // Disparar la impresión una única vez
            setTimeout(function () {
                try {
                    printIframe.contentWindow.focus();
                    printIframe.contentWindow.print();
                } catch (err) {
                    console.error('Error al imprimir por iframe:', err);
                }
            }, 300);

        } catch (error) {
            console.error('Error exportando Casa de Paz a PDF:', error);
            window.print();
        }
    };
})();
