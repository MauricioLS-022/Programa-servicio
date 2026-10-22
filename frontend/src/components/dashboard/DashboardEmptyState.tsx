import React from 'react';
import { Link } from 'react-router-dom';

export interface DashboardEmptyStateProps {
  type?: 'sin_red' | 'sin_casas' | 'generic';
  title?: string;
  message?: string;
  icon?: string;
  onActionClick?: () => void;
  actionText?: string;
}

export const DashboardEmptyState: React.FC<DashboardEmptyStateProps> = ({
  type = 'sin_red',
  title,
  message,
  icon,
  onActionClick,
  actionText,
}) => {
  if (type === 'sin_red') {
    return (
      <section className="empty-state-card" style={{ margin: '2rem auto', maxWidth: '640px', textAlign: 'center', padding: '3.5rem 2rem' }}>
        <span
          className="material-symbols-outlined"
          style={{ fontSize: '3.8rem', color: 'var(--color5, #96292b)', marginBottom: '1rem', display: 'block' }}
        >
          link_off
        </span>
        <h2
          style={{
            fontFamily: "var(--font-headline, 'Noto Serif', serif)",
            color: 'var(--primary, #390002)',
            marginBottom: '0.75rem',
            fontSize: '1.5rem',
            fontWeight: 700,
          }}
        >
          Sin Red Asignada
        </h2>
        <p style={{ color: 'var(--text-muted, #64748b)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
          Tu cuenta de supervisor aún no está vinculada a una red ministerial. Para poder visualizar las métricas, asistencia y Casas de Paz correspondientes a tu zona, solicita a un administrador que asigne tu usuario a una red.
        </p>
        <span
          className="badge"
          style={{
            background: 'rgba(120, 2, 4, 0.08)',
            color: 'var(--color2, #780204)',
            padding: '0.45rem 1rem',
            borderRadius: '20px',
            fontSize: '0.85rem',
            fontWeight: 600,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '1rem' }}>info</span>
          Estado: Pendiente de Asignación
        </span>
      </section>
    );
  }

  if (type === 'sin_casas') {
    return (
      <section className="empty-state-card" style={{ margin: '2rem auto', maxWidth: '640px', textAlign: 'center', padding: '3.5rem 2rem' }}>
        <span
          className="material-symbols-outlined"
          style={{ fontSize: '3.8rem', color: 'var(--color5, #96292b)', marginBottom: '1rem', display: 'block' }}
        >
          home_work
        </span>
        <h2
          style={{
            fontFamily: "var(--font-headline, 'Noto Serif', serif)",
            color: 'var(--primary, #390002)',
            marginBottom: '0.75rem',
            fontSize: '1.5rem',
            fontWeight: 700,
          }}
        >
          {title || 'Sin Casas de Paz Asignadas'}
        </h2>
        <p style={{ color: 'var(--text-muted, #64748b)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
          {message || 'La red seleccionada aún no tiene Casas de Paz registradas o activas. Puedes seleccionar otra red en el filtro superior o registrar nuevas Casas de Paz desde la sección de Estructura.'}
        </p>
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          {onActionClick && (
            <button
              type="button"
              onClick={onActionClick}
              className="quick-action-btn"
              style={{ padding: '0.55rem 1.15rem', borderRadius: '8px', fontWeight: 600, fontSize: '0.9rem' }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '1.1rem' }}>arrow_back</span>
              {actionText || 'Ver Vista Zonal'}
            </button>
          )}
          <Link
            to="/estructura"
            className="quick-action-btn"
            style={{ padding: '0.55rem 1.15rem', borderRadius: '8px', fontWeight: 600, fontSize: '0.9rem' }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '1.1rem' }}>account_tree</span>
            Estructura y Redes
          </Link>
        </div>
      </section>
    );
  }

  return (
    <div className="empty-state" style={{ padding: '3rem 1.5rem', textAlign: 'center' }}>
      <span className="material-symbols-outlined empty-icon" style={{ fontSize: '3rem', color: 'var(--text-muted)' }}>
        {icon || 'info'}
      </span>
      <h3 style={{ fontSize: '1.2rem', margin: '0.5rem 0', color: 'var(--primary)' }}>
        {title || 'Sin información'}
      </h3>
      <p className="empty-message" style={{ margin: 0, color: 'var(--text-muted)' }}>
        {message || 'No hay datos disponibles para mostrar en este momento.'}
      </p>
    </div>
  );
};

