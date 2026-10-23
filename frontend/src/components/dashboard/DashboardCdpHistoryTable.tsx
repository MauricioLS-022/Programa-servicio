import React from 'react';
import type { HistorialReporte } from '../../types/estructura';

export interface DashboardCdpHistoryTableProps {
  historial?: HistorialReporte[];
}

export const DashboardCdpHistoryTable: React.FC<DashboardCdpHistoryTableProps> = ({ historial = [] }) => {
  return (
    <article className="status-card fade-in-5" role="region" aria-labelledby="historial-title">
      <div className="status-card-header">
        <h2 id="historial-title" className="section-title">Historial de Reportes</h2>
        <p className="section-subtitle">Últimos reportes registrados de la Casa de Paz</p>
      </div>
      <div className="table-scroll" tabIndex={0} role="region" aria-label="Tabla de historial de reportes">
        <table className="cdp-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Asistencia</th>
              <th>Niños</th>
              <th>Visitas</th>
              <th>Ofrenda</th>
            </tr>
          </thead>
          <tbody>
            {historial.length > 0 ? (
              historial.map((reporte, idx) => {
                const ofrUsd = Number(reporte.ofrendas_usd || 0);
                const ofrBs = Number(reporte.ofrendas_bs || 0);

                return (
                  <tr key={reporte.id ? `rep-${reporte.id}` : `rep-${idx}`}>
                    <td data-label="Fecha"><strong>{reporte.fecha}</strong></td>
                    <td data-label="Asistencia">
                      <span className="asist-pill">{reporte.asistencia}</span>
                    </td>
                    <td data-label="Niños">{Number(reporte.ninos ?? reporte.nro_niños ?? 0)}</td>
                    <td data-label="Visitas">{Number(reporte.visitas ?? reporte.nro_visitas ?? 0)}</td>
                    <td data-label="Ofrenda">
                      <div>
                        <strong>${ofrUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
                      </div>
                      {ofrBs > 0 && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                          Bs. {ofrBs.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={5}>
                  <div className="empty-state">
                    <span className="material-symbols-outlined empty-icon">description</span>
                    <p className="empty-message">Aún no hay reportes registrados para esta Casa de Paz.</p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </article>
  );
};
