import React from 'react';
import type { ActividadRecienteItem } from '../../types/estructura';

export interface DashboardRecentActivityProps {
  redNombre?: string;
  actividadReciente?: ActividadRecienteItem[];
}

export const DashboardRecentActivity: React.FC<DashboardRecentActivityProps> = ({
  redNombre = 'esta red',
  actividadReciente = [],
}) => {
  return (
    <article className="status-card fade-in-5" role="region" aria-labelledby="actividad-red-title" style={{ marginTop: '1rem' }}>
      <div className="status-card-header">
        <h2 id="actividad-red-title" className="section-title">Actividad Reciente</h2>
        <p className="section-subtitle">Últimos reportes enviados en {redNombre}</p>
      </div>
      <div className="activity-feed" tabIndex={0} role="region" aria-label="Historial de actividad reciente">
        {actividadReciente.length > 0 ? (
          actividadReciente.map((act, index) => (
            <article key={`${act.cdp_codigo}-${index}`} className="activity-item">
              <div className={`activity-avatar ${act.avatar_class || ''}`}>
                {act.iniciales || 'CDP'}
              </div>
              <div className="activity-info">
                <div className="activity-name-row">
                  <h4>{act.lider}</h4>
                  <span className="badge-code">{act.cdp_codigo}</span>
                </div>
                <span className="activity-meta">
                  <span className="material-symbols-outlined" style={{ fontSize: '0.8rem', verticalAlign: 'middle', marginRight: '0.2rem' }}>
                    calendar_today
                  </span>
                  {act.fecha_formateada || 'Reciente'} {act.cdp_nombre ? `· ${act.cdp_nombre}` : ''}
                </span>
                {act.tema && (
                  <span className="activity-tema">
                    <span className="material-symbols-outlined" style={{ fontSize: '0.8rem', verticalAlign: 'middle', marginRight: '0.2rem' }}>
                      menu_book
                    </span>
                    {act.tema}
                  </span>
                )}
              </div>
              <div className="activity-badge">
                <span className="activity-asist-number">{act.asistencia}</span>
                <span className="activity-asist-label">asist.</span>
              </div>
            </article>
          ))
        ) : (
          <div className="empty-state">
            <span className="material-symbols-outlined empty-icon">history</span>
            <p className="empty-message">Aún no hay reportes recientes en esta red.</p>
          </div>
        )}
      </div>
    </article>
  );
};

