import React from 'react';
import type { AlertaSeguimiento } from '../../types/estructura';

export interface DashboardAlertsCardProps {
  alertas?: AlertaSeguimiento[];
  title?: string;
  isZonal?: boolean;
}

export const DashboardAlertsCard: React.FC<DashboardAlertsCardProps> = ({
  alertas = [],
  title = 'Alertas de Seguimiento',
  isZonal = false,
}) => {
  const total = alertas.length;

  return (
    <article className="warning-card" role="region" aria-labelledby="alertas-seguimiento-title">
      <div className="status-card-header">
        <div className="status-header-title-wrap">
          <h2 id="alertas-seguimiento-title" className="section-title">
            {title}
          </h2>
          {total > 0 && (
            <span
              className="alert-header-badge"
              title={total === 1 ? '1 casa falta por reporte' : `${total} casas faltan por reporte`}
            >
              {total}
            </span>
          )}
        </div>
        <p className="section-subtitle">
          {total > 0
            ? total === 1
              ? 'Falta 1 por reporte (>2 sem)'
              : `Faltan ${total} por reporte (>2 sem)`
            : isZonal
            ? 'Sin alertas pendientes en esta red'
            : 'Todas al día'}
        </p>
      </div>

      <div className="alert-list">
        {total > 0 ? (
          alertas.map((alerta, index) => {
            const cleanPhone = alerta.telefono
              ? alerta.telefono.replace(/[\s+-]/g, '')
              : '';

            return (
              <article key={`${alerta.codigo}-${index}`} className="alert-item">
                <div className="alert-info-text">
                  <h4>
                    {alerta.nombre} <span className="badge-code">{alerta.codigo}</span>
                  </h4>
                  <p className="alert-meta">
                    {alerta.red ? `${alerta.red} · ` : ''}Líder: {alerta.lider}
                  </p>
                  <p className="alert-days">
                    <span
                      className="material-symbols-outlined text-danger"
                      style={{ fontSize: '0.9rem', verticalAlign: 'middle', marginRight: '0.2rem' }}
                    >
                      warning
                    </span>
                    {alerta.motivo}
                  </p>
                </div>
                {cleanPhone && (
                  <a
                    href={`https://wa.me/${cleanPhone}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-contact-action"
                    aria-label={`Atender a ${alerta.lider} por WhatsApp`}
                    title="Atender por WhatsApp"
                  >
                    <span className="material-symbols-outlined">support_agent</span>
                    Atender
                  </a>
                )}
              </article>
            );
          })
        ) : (
          <div className="empty-state">
            <span className="material-symbols-outlined empty-icon">task_alt</span>
            <p className="empty-message">
              {isZonal
                ? 'No hay alertas pendientes en esta red.'
                : 'No hay alertas de seguimiento pendientes.'}
            </p>
          </div>
        )}
      </div>
    </article>
  );
};

