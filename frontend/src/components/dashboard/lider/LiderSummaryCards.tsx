import React from 'react';
import { Link } from 'react-router-dom';
import { Icon } from '../../ui/Icon';
import type { LiderMetricas } from '../../../types/liderDashboard';

export interface LiderSummaryCardsProps {
  metricas: LiderMetricas | null;
}

const formatMoneda = (val?: number) => {
  return Number(val || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

export const LiderSummaryCards: React.FC<LiderSummaryCardsProps> = ({ metricas }) => {
  const totalReportes = metricas?.total_reportes || 0;
  const asistenciaProm =
    totalReportes > 0 && metricas?.asistencia_promedio !== undefined
      ? Number(metricas.asistencia_promedio).toFixed(1)
      : '—';

  const ofrendasUsd = formatMoneda(metricas?.ofrendas_usd_totales);
  const ofrendasBs = formatMoneda(metricas?.ofrendas_bs_totales);

  return (
    <section className="summary-grid" aria-label="Métricas de Casa de Paz" data-testid="summary-grid">
      {/* Acción rápida: Nuevo Reporte */}
      <Link to="/generar-reporte" className="summary-card action-card" data-testid="action-nuevo-reporte">
        <span className="card-icon text-primary">
          <Icon name="add_circle" size={32} />
        </span>
        <h3 className="card-title">Nuevo Reporte</h3>
        <p className="card-subtitle">Registrar reunión de esta semana</p>
      </Link>

      {/* Mis Reportes */}
      <article className="summary-card" data-testid="card-mis-reportes">
        <span className="card-icon text-secondary">
          <Icon name="history" size={28} />
        </span>
        <h3 className="card-title">Mis Reportes</h3>
        <div className="card-number">{totalReportes}</div>
        <span className="watermark-icon" aria-hidden="true">
          <Icon name="description" size={88} />
        </span>
      </article>

      {/* Asistencia Promedio */}
      <article className="summary-card" data-testid="card-asistencia-promedio">
        <span className="card-icon text-primary-container">
          <Icon name="groups" size={28} />
        </span>
        <h3 className="card-title">Asistencia Promedio</h3>
        <div className="card-number">{asistenciaProm}</div>
        <span className="watermark-icon" aria-hidden="true">
          <Icon name="groups" size={88} />
        </span>
      </article>

      {/* Ofrendas Totales */}
      <article className="summary-card" data-testid="card-ofrendas-totales">
        <span className="card-icon text-secondary">
          <Icon name="attach_money" size={28} />
        </span>
        <h3 className="card-title">Ofrendas Totales</h3>
        <div className="card-number" style={{ fontSize: '1.25rem', lineHeight: 1.3 }}>
          <div>${ofrendasUsd}</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            Bs. {ofrendasBs}
          </div>
        </div>
        <span className="watermark-icon" aria-hidden="true">
          <Icon name="savings" size={88} />
        </span>
      </article>
    </section>
  );
};
