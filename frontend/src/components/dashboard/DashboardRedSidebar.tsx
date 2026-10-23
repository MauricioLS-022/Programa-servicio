import React from 'react';
import type { AlertaSeguimiento, TopCrecimiento, LiderRedItem } from '../../types/estructura';
import { DashboardAlertsCard } from './DashboardAlertsCard';

export interface DashboardRedSidebarProps {
  redNombre?: string;
  alertas?: AlertaSeguimiento[];
  topCrecimiento?: TopCrecimiento;
  cumplimiento?: number;
  casasConReporte?: number;
  casasPendientes?: number;
  casasActivas?: number;
  periodo?: string;
  periodoNombre?: string;
  lideresRed?: LiderRedItem[];
}

export const DashboardRedSidebar: React.FC<DashboardRedSidebarProps> = ({
  redNombre = 'esta red',
  alertas = [],
  topCrecimiento,
  cumplimiento = 0,
  casasConReporte = 0,
  casasPendientes = 0,
  casasActivas = 0,
  periodo = 'semana',
  periodoNombre = '',
  lideresRed = [],
}) => {
  const cumplimientoTitle =
    periodo === 'mes'
      ? `Cumplimiento Mensual (${periodoNombre || 'Mes'})`
      : periodo === 'anio'
      ? `Cumplimiento Anual (${periodoNombre || 'Año'})`
      : 'Cumplimiento Semanal';

  const cumplimientoSub =
    periodo === 'mes'
      ? `Casas con reporte en ${periodoNombre || 'el mes activo'}`
      : periodo === 'anio'
      ? `Casas con reporte en ${periodoNombre || 'el año activo'}`
      : 'Casas con reporte enviado esta semana';

  return (
    <aside className="sidebar-column fade-in-6">
      {/* 1. Alertas Zonal */}
      <DashboardAlertsCard
        alertas={alertas}
        isZonal={true}
        title="Alertas Zonal"
      />

      {/* 2. Top Crecimiento */}
      <article className="participation-card">
        <div className="status-card-header">
          <h2 className="section-title">Top Crecimiento</h2>
          <p className="section-subtitle">Mayor retención de visitas y consolidación</p>
        </div>
        {topCrecimiento && topCrecimiento.nombre ? (
          <div className="top-growth-box">
            <div className="growth-badge-icon">
              <span className="material-symbols-outlined">workspace_premium</span>
            </div>
            <div className="growth-details">
              <h3>
                {topCrecimiento.nombre} <span className="badge-code">{topCrecimiento.codigo}</span>
              </h3>
              <p className="growth-rate">
                <strong className="text-success">{topCrecimiento.tasa || 'Sin datos'}</strong> indicador destacado
              </p>
              <p className="growth-sub">
                {topCrecimiento.visitas || 0} visitas registradas · Líder: {topCrecimiento.lider || 'Sin asignar'}
              </p>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <span className="material-symbols-outlined empty-icon">workspace_premium</span>
            <p className="empty-message">Aún no hay datos de crecimiento para destacar.</p>
          </div>
        )}
      </article>

      {/* 3. Cumplimiento de la Red */}
      <article className="participation-card">
        <div className="status-card-header">
          <h2 className="section-title" id="lblCumplimientoTitleRed">{cumplimientoTitle}</h2>
          <p className="section-subtitle" id="lblCumplimientoSubRed">{cumplimientoSub}</p>
        </div>
        <div className="cumplimiento-zonal-box">
          <div className="cumplimiento-header-row">
            <span className="cumplimiento-percentage" id="cumplimientoPctRed">{cumplimiento}%</span>
            <span className="cumplimiento-fraction" id="cumplimientoFractionRed">
              {casasConReporte} de {casasActivas} casas
            </span>
          </div>
          <div className="progress-bar-track">
            <div
              className="progress-bar-fill"
              id="cumplimientoBarRed"
              style={{
                width: `${cumplimiento}%`,
                ['--bar-width' as string]: `${cumplimiento}%`,
              }}
            />
          </div>
          <div className="cumplimiento-pills">
            <span className="cumplimiento-pill al-dia" id="pillAlDiaRed">
              <span className="material-symbols-outlined">check_circle</span>
              <span id="pillAlDiaNumRed">{casasConReporte}</span> Al día
            </span>
            <span className="cumplimiento-pill pendientes" id="pillPendientesRed">
              <span className="material-symbols-outlined">schedule</span>
              <span id="pillPendientesNumRed">{casasPendientes}</span> Pendientes
            </span>
          </div>
        </div>
      </article>

      {/* 4. Directorio de Líderes de la Red */}
      <article className="participation-card">
        <div className="status-card-header">
          <h2 className="section-title">Líderes de la Red</h2>
          <p className="section-subtitle">Equipo asignado a {redNombre}</p>
        </div>
        <div className="lideres-red-list">
          {lideresRed.length > 0 ? (
            lideresRed.map((lid, idx) => {
              const cleanTel = lid.telefono ? lid.telefono.replace(/[\s+-]/g, '') : '';
              return (
                <div key={`${lid.nombre}-${idx}`} className="leader-card-item">
                  <div className="leader-avatar">
                    <span className="material-symbols-outlined">person</span>
                  </div>
                  <div className="leader-info">
                    <h4>
                      {lid.nombre} <span className="badge-role">{lid.rol || 'Líder'}</span>
                    </h4>
                    <p>
                      {lid.cdp_codigo && <span className="badge-code">{lid.cdp_codigo}</span>}
                      {lid.cdp_anfitrion ? ` · ${lid.cdp_anfitrion}` : ''}
                    </p>
                  </div>
                  <div className="leader-actions">
                    {cleanTel && (
                      <>
                        <a
                          href={`https://wa.me/${cleanTel}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-icon-wa"
                          aria-label={`WhatsApp a ${lid.nombre}`}
                          title="Contactar por WhatsApp"
                        >
                          <span className="material-symbols-outlined">chat</span>
                        </a>
                        <a
                          href={`tel:${cleanTel}`}
                          className="btn-icon-call"
                          aria-label={`Llamar a ${lid.nombre}`}
                          title={`Llamar a ${lid.nombre}`}
                        >
                          <span className="material-symbols-outlined">call</span>
                        </a>
                      </>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="empty-state">
              <span className="material-symbols-outlined empty-icon">group</span>
              <p className="empty-message">No hay líderes asignados en las casas de esta red.</p>
            </div>
          )}
        </div>
      </article>
    </aside>
  );
};

