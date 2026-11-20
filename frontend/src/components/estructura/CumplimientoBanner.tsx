import React from 'react';
import { Icon } from '../ui/Icon';
import type { FiltroEstadoEstructura } from '../../hooks/useEstructuraController';

interface CumplimientoBannerProps {
  pendingInScope: number;
  effectiveRedId: string;
  selectedRedName: string;
  filtroEstado: FiltroEstadoEstructura;
  hasFilteredCasas: boolean;
  onFiltroEstadoChange: (estado: FiltroEstadoEstructura) => void;
}

export const CumplimientoBanner: React.FC<CumplimientoBannerProps> = ({
  pendingInScope,
  effectiveRedId,
  selectedRedName,
  filtroEstado,
  hasFilteredCasas,
  onFiltroEstadoChange,
}) => {
  if (pendingInScope > 0) {
    return (
      <div
        className="alert-banner-reportes"
        id="bannerReportesPendientes"
        data-total-pendientes={pendingInScope}
      >
        <div className="alert-banner-main">
          <Icon
            name="notification_important"
            size={26}
            className="alert-banner-icon shrink-0"
          />
          <div className="alert-banner-info">
            <strong className="alert-banner-title">
              {effectiveRedId && effectiveRedId !== 'all'
                ? `Reportes Pendientes · ${selectedRedName}`
                : 'Reportes de la Semana Pendientes'}
            </strong>
            <p className="alert-banner-text">
              <strong>
                {pendingInScope} Casa{pendingInScope !== 1 ? 's' : ''} de Paz activa
                {pendingInScope !== 1 ? 's' : ''}
              </strong>{' '}
              {effectiveRedId && effectiveRedId !== 'all'
                ? `en la ${selectedRedName}`
                : 'en la congregación'}{' '}
              no ha{pendingInScope !== 1 ? 'n' : ''} enviado reporte en los últimos 7 días.
            </p>
          </div>
        </div>
        <div className="alert-banner-actions">
          {filtroEstado === 'pendientes_7d' ? (
            <button
              type="button"
              className="btn-banner-filter btn-banner-all"
              id="btnVerTodasCasas"
              onClick={() => onFiltroEstadoChange('todas')}
              title="Mostrar todas las casas"
            >
              <Icon name="restart_alt" size={16} />
              <span>Ver todas</span>
            </button>
          ) : (
            <button
              type="button"
              className="btn-banner-filter"
              id="btnFiltrarPendientes"
              onClick={() => onFiltroEstadoChange('pendientes_7d')}
              title="Filtrar cuadrícula para ver solo casas pendientes"
            >
              <Icon name="filter_list" size={16} />
              <span>
                Ver {pendingInScope} pendiente{pendingInScope !== 1 ? 's' : ''}
              </span>
            </button>
          )}
        </div>
      </div>
    );
  }

  if (effectiveRedId && effectiveRedId !== 'all' && hasFilteredCasas) {
    return (
      <div className="alert-banner-reportes is-all-good">
        <div className="alert-banner-main">
          <div className="alert-banner-icon">
            <Icon name="check_circle" size={24} />
          </div>
          <div className="alert-banner-info">
            <strong className="alert-banner-title">¡Red al día! · {selectedRedName}</strong>
            <p className="alert-banner-text">
              Todas las Casas de Paz activas de la <strong>{selectedRedName}</strong> han
              enviado su reporte en los últimos 7 días.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return null;
};
