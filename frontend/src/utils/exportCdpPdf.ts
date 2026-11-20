import type { CdpDetalle } from '../types/estructura';

const HTML_ESCAPE_MAP: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
};

/**
 * Escapa caracteres especiales HTML para prevenir inyección/XSS en documentos generados dinámicamente.
 */
export function escapeHtml(value: unknown): string {
  if (value === null || value === undefined) return '';
  return String(value).replace(/[&<>"']/g, (ch) => HTML_ESCAPE_MAP[ch] ?? ch);
}

/**
 * Genera el documento HTML institucional imprimible para la Ficha Técnica de una Casa de Paz.
 */
export function buildCdpFichaHtml(cdp: CdpDetalle, emissionDate?: string): string {
  const today = escapeHtml(
    emissionDate ||
      new Date().toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
  );

  const teamRows = (cdp.lideres || [])
    .map(
      (m) => `
      <tr>
        <td style="padding: 6px 8px; border-bottom: 1px solid #eee;"><strong>${escapeHtml(m.nombre_completo)}</strong></td>
        <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">${escapeHtml(m.rol)}</td>
        <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">${escapeHtml(m.telefono || 'No registrado')}</td>
      </tr>`
    )
    .join('');

  const reportRows = (cdp.reportes || [])
    .map(
      (r) => `
      <tr>
        <td style="padding: 6px 8px; border-bottom: 1px solid #eee;"><strong>${escapeHtml(r.fecha_formateada || r.fecha || '')}</strong></td>
        <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">
          <strong>${escapeHtml(r.tema || 'Sin tema registrado')}</strong>
          ${r.observaciones ? `<div style="font-size: 10px; color: #666; margin-top: 2px;">${escapeHtml(r.observaciones)}</div>` : ''}
        </td>
        <td style="text-align: center; padding: 6px 8px; border-bottom: 1px solid #eee;"><strong>${Number(r.asistencia || 0)}</strong></td>
        <td style="font-size: 11px; padding: 6px 8px; border-bottom: 1px solid #eee;">Reg: ${Number(r.nro_regulares || 0)} · Niñ: ${Number(r.nro_ninos || r.nro_niños || 0)} · Vis: ${Number(r.nro_visitas || 0)}</td>
        <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">$${Number(r.ofrendas_usd || 0).toFixed(2)} · Bs. ${Number(r.ofrendas_bs || 0).toFixed(2)}</td>
        <td style="text-align: center; padding: 6px 8px; border-bottom: 1px solid #eee;">${r.cesta_amor ? 'Sí' : 'No'}</td>
      </tr>`
    )
    .join('');

  const safeCodigo = escapeHtml(cdp.codigo);
  const safeRedNombre = escapeHtml(cdp.red_nombre);
  const safeSupervisor = escapeHtml(cdp.supervisor_nombre);
  const safeDireccion = escapeHtml(cdp.direccion || 'No registrada');
  const safeAnfitrion = escapeHtml(cdp.anfitrion || 'Sin asignar');
  const safeTelefono = escapeHtml(cdp.telefono || 'No registrado');
  const safeHorario = escapeHtml(cdp.horario || 'Miércoles · 7:00 PM');

  return `
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <title>Ficha Técnica Oficial - Casa de Paz ${safeCodigo}</title>
      <style>
        @page { size: letter portrait; margin: 12mm 15mm; }
        * { box-sizing: border-box; }
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
        }
        .brand-subtitle {
          font-size: 12px;
          color: #564240;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          font-weight: 600;
        }
        .section-title {
          font-size: 13px;
          font-weight: 700;
          color: #390002;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border-bottom: 1px solid #e8d0cc;
          padding-bottom: 4px;
          margin: 14px 0 8px 0;
        }
        .kpi-container {
          display: flex;
          gap: 8px;
          margin-bottom: 14px;
        }
        .kpi-box {
          flex: 1;
          background: #faf5f3;
          border: 1px solid #e8d0cc;
          border-radius: 6px;
          padding: 8px 10px;
          text-align: center;
        }
        .kpi-label { font-size: 9.5px; text-transform: uppercase; font-weight: 700; color: #5a4240; }
        .kpi-val { font-size: 16px; font-weight: 800; color: #390002; margin: 3px 0; }
        .kpi-sub { font-size: 9.5px; color: #700204; font-weight: 600; }
        table { width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 12px; }
        th {
          background-color: #f8e4e3;
          color: #390002;
          font-weight: 700;
          text-align: left;
          padding: 6px 8px;
          border-bottom: 1.5px solid #ddc0bd;
          font-size: 10px;
          text-transform: uppercase;
        }
      </style>
    </head>
    <body>
      <div class="doc-header">
        <div>
          <div class="brand-title">Comunidad Cristiana Vino Nuevo</div>
          <div class="brand-subtitle">Ficha Técnica Oficial · Casa "${safeCodigo}"</div>
        </div>
        <div style="text-align: right; font-size: 11px;">
          <div>Emisión: ${today}</div>
          <div>Red: <strong>${safeRedNombre}</strong> · Supervisor: <strong>${safeSupervisor}</strong></div>
        </div>
      </div>

      <div class="section-title">1. Resumen de Desempeño y Crecimiento</div>
      <div class="kpi-container">
        <div class="kpi-box">
          <div class="kpi-label">Asistencia Prom.</div>
          <div class="kpi-val">${Number(cdp.asistencia_promedio || 0)}</div>
          <div class="kpi-sub">personas / reunión</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-label">Reportes Totales</div>
          <div class="kpi-val">${Number(cdp.total_reportes || 0)}</div>
          <div class="kpi-sub">semanas reportadas</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-label">Ofrendas Totales</div>
          <div class="kpi-val">$${Number(cdp.ofrendas_usd_totales || 0).toFixed(2)}</div>
          <div class="kpi-sub">Bs. ${Number(cdp.ofrendas_bs_totales || 0).toFixed(2)}</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-label">Visitas & Conversiones</div>
          <div class="kpi-val">${Number(cdp.visitas_totales || 0)}</div>
          <div class="kpi-sub">${Number(cdp.conversiones_totales || 0)} conversiones</div>
        </div>
      </div>

      <div class="section-title">2. Información del Centro</div>
      <table>
        <tr>
          <td style="width: 25%; font-weight: bold; padding: 4px 6px;">Dirección:</td>
          <td style="width: 25%; padding: 4px 6px;">${safeDireccion}</td>
          <td style="width: 25%; font-weight: bold; padding: 4px 6px;">Anfitrión:</td>
          <td style="width: 25%; padding: 4px 6px;">${safeAnfitrion}</td>
        </tr>
        <tr>
          <td style="font-weight: bold; padding: 4px 6px;">Teléfono:</td>
          <td style="padding: 4px 6px;">${safeTelefono}</td>
          <td style="font-weight: bold; padding: 4px 6px;">Horario:</td>
          <td style="padding: 4px 6px;">${safeHorario}</td>
        </tr>
      </table>

      <div class="section-title">3. Equipo de Liderazgo Responsable</div>
      <table>
        <thead>
          <tr>
            <th style="width: 45%;">Nombre Completo</th>
            <th style="width: 30%;">Rol</th>
            <th style="width: 25%;">Teléfono</th>
          </tr>
        </thead>
        <tbody>
          ${teamRows || '<tr><td colspan="3" style="text-align: center; padding: 8px;">No hay líderes asignados.</td></tr>'}
        </tbody>
      </table>

      <div class="section-title">4. Historial Reciente de Reportes</div>
      <table>
        <thead>
          <tr>
            <th style="width: 14%;">Fecha</th>
            <th style="width: 34%;">Tema</th>
            <th style="width: 12%; text-align: center;">Asistencia</th>
            <th style="width: 20%;">Desglose</th>
            <th style="width: 12%;">Ofrendas</th>
            <th style="width: 8%; text-align: center;">Cesta</th>
          </tr>
        </thead>
        <tbody>
          ${reportRows || '<tr><td colspan="6" style="text-align: center; padding: 8px;">Sin reportes registrados aún.</td></tr>'}
        </tbody>
      </table>
    </body>
    </html>
  `;
}

/**
 * Abre un iframe oculto de impresión para exportar la Ficha Técnica de una Casa de Paz a PDF.
 */
export function exportCdpPdf(cdp: CdpDetalle): void {
  try {
    const oldIframe = document.getElementById('print-cdp-iframe');
    if (oldIframe) oldIframe.remove();

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

    const html = buildCdpFichaHtml(cdp);
    const frameDoc = printIframe.contentWindow?.document;
    if (frameDoc) {
      frameDoc.open();
      frameDoc.write(html);
      frameDoc.close();
      setTimeout(() => {
        printIframe.contentWindow?.focus();
        printIframe.contentWindow?.print();
      }, 300);
    }
  } catch (err) {
    console.error('Error exportando PDF:', err);
    window.print();
  }
}
