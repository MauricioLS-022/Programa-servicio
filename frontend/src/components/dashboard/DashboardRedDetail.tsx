import React from 'react';
import type {
  CasaDetalleZonal,
  ActividadRecienteItem,
  LiderRedItem,
  TopCrecimiento,
} from '../../types/estructura';

export interface DashboardRedDetailProps {
  redNombre?: string;
  casas?: CasaDetalleZonal[];
  actividadReciente?: ActividadRecienteItem[];
  lideresRed?: LiderRedItem[];
  topCrecimiento?: TopCrecimiento;
  cumplimiento?: number;
  casasConReporte?: number;
  casasPendientes?: number;
  casasActivas?: number;
  periodo?: string;
  periodoNombre?: string;
  onSelectCdp?: (cdpId: number) => void;
}

export const DashboardRedDetail: React.FC<DashboardRedDetailProps> = ({
  redNombre = 'Red',
  casas = [],
  actividadReciente = [],
  lideresRed = [],
  topCrecimiento,
  cumplimiento = 0,
  casasConReporte = 0,
  casasPendientes = 0,
  casasActivas = 0,
  periodo = 'semana',
  periodoNombre = '',
  onSelectCdp,
}) => {
  return (
    <div className="red-detail-section" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Tabla / Listado de Casas de Paz de la Red */}
      <article className="status-card fade-in-5" role="region" aria-label="Casas de Paz de la Red">
        <div className="status-card-header">
          <div>
            <h2 className="section-title">Casas de Paz ({casas.length})</h2>
            <p className="section-subtitle">Listado de células activas en {redNombre}</p>
          </div>
        </div>

        <div className="table-scroll" style={{ overflowX: 'auto' }}>
          <table className="cdp-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem' }}>Código / Casa</th>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem' }}>Líder</th>
                <th style={{ textAlign: 'center', padding: '0.75rem 1rem' }}>Asistencia</th>
                <th style={{ textAlign: 'center', padding: '0.75rem 1rem' }}>Visitas</th>
                <th style={{ textAlign: 'right', padding: '0.75rem 1rem' }}>Contacto</th>
              </tr>
            </thead>
            <tbody>
              {casas.length > 0 ? (
                casas.map((c) => {
                  const cleanTel = c.telefono ? c.telefono.replace(/[\s+-]/g, '') : '';
                  return (
                    <tr
                      key={c.id}
                      style={{ borderBottom: '1px solid rgba(221, 192, 189, 0.15)', cursor: onSelectCdp ? 'pointer' : 'default' }}
                      onClick={() => onSelectCdp && onSelectCdp(c.id)}
                    >
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <strong>{c.codigo}</strong>
                        {c.anfitrion && (
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted, #64748b)' }}>
                            {c.anfitrion}
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>{c.lider || 'Sin asignar'}</td>
                      <td style={{ textAlign: 'center', padding: '0.75rem 1rem' }}>
                        <span className="asist-pill" style={{ fontWeight: 700 }}>
                          {c.asistencia}
                        </span>
                      </td>
                      <td style={{ textAlign: 'center', padding: '0.75rem 1rem' }}>{c.visitas}</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem 1rem' }}>
                        {cleanTel ? (
                          <a
                            href={`https://wa.me/${cleanTel}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="btn-icon-wa"
                            aria-label={`WhatsApp a ${c.lider}`}
                            title="Contactar por WhatsApp"
                            style={{ display: 'inline-flex', padding: '0.35rem', borderRadius: '6px' }}
                          >
                            <span className="material-symbols-outlined" style={{ fontSize: '1.1rem' }}>
                              chat
                            </span>
                          </a>
                        ) : (
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>-</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={5} style={{ padding: '2rem', textAlign: 'center' }}>
                    <div className="empty-state">
                      <span className="material-symbols-outlined empty-icon">home_work</span>
                      <p className="empty-message">No hay Casas de Paz registradas en esta red.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </article>

      {/* 2. Actividad Reciente */}
      <article className="status-card fade-in-5" role="region" aria-labelledby="actividad-red-title">
        <div className="status-card-header">
          <h2 id="actividad-red-title" className="section-title">
            Actividad Reciente
          </h2>
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
                    <span
                      className="material-symbols-outlined"
                      style={{ fontSize: '0.8rem', verticalAlign: 'middle', marginRight: '0.2rem' }}
                    >
                      calendar_today
                    </span>
                    {act.fecha_formateada || 'Reciente'} {act.cdp_nombre ? `· ${act.cdp_nombre}` : ''}
                  </span>
                  {act.tema && (
                    <span className="activity-tema">
                      <span
                        className="material-symbols-outlined"
                        style={{ fontSize: '0.8rem', verticalAlign: 'middle', marginRight: '0.2rem' }}
                      >
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

      {/* 3. Panel Zonal Adicional: Top Crecimiento y Cumplimiento Zonal */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        {/* Top Crecimiento */}
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
                  <strong className="text-success">{topCrecimiento.tasa || 'Destacado'}</strong> indicador destacado
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

        {/* Cumplimiento de la Red */}
        <article className="participation-card">
          <div className="status-card-header">
            <h2 className="section-title">
              {periodo === 'mes'
                ? `Cumplimiento Mensual (${periodoNombre || 'Mes'})`
                : periodo === 'anio'
                ? `Cumplimiento Anual (${periodoNombre || 'Año'})`
                : 'Cumplimiento Semanal'}
            </h2>
            <p className="section-subtitle">
              Casas con reporte en {periodoNombre || 'el período activo'}
            </p>
          </div>
          <div className="cumplimiento-zonal-box">
            <div className="cumplimiento-header-row">
              <span className="cumplimiento-percentage">{cumplimiento}%</span>
              <span className="cumplimiento-fraction">
                {casasConReporte} de {casasActivas || casas.length} casas
              </span>
            </div>
            <div className="progress-bar-track">
              <div
                className="progress-bar-fill"
                style={{
                  width: `${cumplimiento}%`,
                  ['--bar-width' as string]: `${cumplimiento}%`,
                }}
              />
            </div>
            <div className="cumplimiento-pills">
              <span className="cumplimiento-pill al-dia">
                <span className="material-symbols-outlined">check_circle</span>
                <span>{casasConReporte}</span> Al día
              </span>
              <span className="cumplimiento-pill pendientes">
                <span className="material-symbols-outlined">schedule</span>
                <span>{casasPendientes}</span> Pendientes
              </span>
            </div>
          </div>
        </article>
      </div>

      {/* 4. Directorio de Líderes de la Red */}
      {lideresRed.length > 0 && (
        <article className="participation-card">
          <div className="status-card-header">
            <h2 className="section-title">Líderes de la Red</h2>
            <p className="section-subtitle">Equipo asignado a {redNombre}</p>
          </div>
          <div className="lideres-red-list">
            {lideresRed.map((lid, idx) => {
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
            })}
          </div>
        </article>
      )}
    </div>
  );
};

