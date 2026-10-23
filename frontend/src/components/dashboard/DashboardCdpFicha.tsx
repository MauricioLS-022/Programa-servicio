import React from 'react';
import type { DashboardMetricas } from '../../types/estructura';

export interface DashboardCdpFichaProps {
  metricas?: DashboardMetricas;
}

export const DashboardCdpFicha: React.FC<DashboardCdpFichaProps> = ({ metricas }) => {
  const liderNombre = metricas?.lider || 'Sin asignar';
  const telefonoLider = String(metricas?.telefono || metricas?.telefono_contacto || '');
  const cleanPhone = telefonoLider.replace(/\D/g, '');
  const reporteAlDia = metricas?.estado_reporte === 'enviado' || metricas?.reporte_al_dia;
  const diasSinReporte = metricas?.dias_desde_reporte;
  const historial = metricas?.historial || [];

  return (
    <section className="cdp-header-card fade-in-1">
      <div className="lider-info">
        <div className="lider-avatar" aria-hidden="true">
          <span className="material-symbols-outlined">person</span>
        </div>
        <div className="lider-details">
          <h3>{liderNombre}</h3>
          <p>{metricas?.lider ? 'Líder principal' : 'Falta asignar líder'}</p>
        </div>
      </div>

      <div className="cdp-header-meta">
        {/* Trazabilidad de Último Reporte */}
        <div className={`trazabilidad-box ${reporteAlDia ? 'enviado' : 'pendiente'}`}>
          <span className="material-symbols-outlined trazabilidad-icon">
            {reporteAlDia ? 'verified' : 'pending_actions'}
          </span>
          <div className="trazabilidad-text">
            <span className="trazabilidad-label">
              {reporteAlDia ? 'Reporte de esta semana recibido' : 'Reporte de esta semana pendiente'}
            </span>
            {reporteAlDia ? (
              <span className="trazabilidad-author">
                Por: <strong>{metricas?.ultimo_reporte_por || 'Sin identificar'}</strong> · {metricas?.ultimo_reporte_fecha || 'Fecha no disponible'}
              </span>
            ) : historial.length > 0 ? (
              <span className="trazabilidad-author">
                Último servicio registrado: {metricas?.ultimo_reporte_fecha}
                {typeof diasSinReporte === 'number' && diasSinReporte > 0 ? ` (hace ${diasSinReporte} días)` : ''} · Enviado por: <strong>{metricas?.ultimo_reporte_por || 'Líder'}</strong>
              </span>
            ) : (
              <span className="trazabilidad-author">
                Todavía no hay reportes registrados para esta casa.
              </span>
            )}
          </div>
        </div>

        {cleanPhone && (
          <div className="lider-actions">
            <a
              href={`https://wa.me/${cleanPhone}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-full-outline"
              aria-label="Contactar líder de Casa de Paz por WhatsApp"
            >
              <span className="material-symbols-outlined">chat</span>
              WhatsApp
            </a>
          </div>
        )}
      </div>
    </section>
  );
};
