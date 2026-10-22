import React from 'react';
import type { DashboardMetricas } from '../../types/estructura';

export interface DashboardCdpDetailProps {
  metricas?: DashboardMetricas;
  periodo?: string;
  periodoNombre?: string;
}

export const DashboardCdpDetail: React.FC<DashboardCdpDetailProps> = ({
  metricas,
}) => {
  const liderNombre = metricas?.lider || 'Sin líder asignado';
  const telefonoLider = metricas?.telefono || '';
  const cleanPhone = telefonoLider.replace(/\D/g, '');
  const reporteAlDia = metricas?.estado_reporte === 'enviado' || metricas?.reporte_al_dia;
  const diasSinReporte = metricas?.dias_desde_reporte;
  const historial = metricas?.historial || [];

  return (
    <section className="cdp-detail-container fade-in-6" style={{ marginTop: '1.25rem' }}>
      {/* 1. Ficha del Líder & Trazabilidad de Reporte Semanal */}
      <section className="cdp-header-card">
        <div className="lider-info">
          <div className="lider-avatar" aria-hidden="true">
            <span className="material-symbols-outlined" style={{ fontSize: '1.75rem' }}>
              person
            </span>
          </div>
          <div className="lider-details">
            <h3>{liderNombre}</h3>
            <p>{metricas?.lider ? 'Líder principal de Casa de Paz' : 'Falta asignar líder principal'}</p>
          </div>
        </div>

        <div className="cdp-header-meta" style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
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
                  Por: <strong>{metricas?.ultimo_reporte_por || 'Líder'}</strong>
                  {metricas?.ultimo_reporte_fecha ? ` · ${metricas.ultimo_reporte_fecha}` : ''}
                </span>
              ) : (
                <span className="trazabilidad-author">
                  {metricas?.ultimo_reporte_fecha ? (
                    <>
                      Último servicio: <strong>{metricas.ultimo_reporte_fecha}</strong>
                      {typeof diasSinReporte === 'number' && diasSinReporte > 0
                        ? ` (hace ${diasSinReporte} días)`
                        : ''}
                      {metricas?.ultimo_reporte_por ? ` · Por: ${metricas.ultimo_reporte_por}` : ''}
                    </>
                  ) : (
                    'Sin reportes previos registrados en el sistema'
                  )}
                </span>
              )}
            </div>
          </div>

          {/* Botón directo de contacto por WhatsApp */}
          {cleanPhone && (
            <a
              href={`https://wa.me/${cleanPhone}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-contact-action"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.55rem 1rem',
                borderRadius: '0.65rem',
                fontSize: '0.85rem',
                fontWeight: 600,
                textDecoration: 'none',
              }}
              title={`Contactar a ${liderNombre} por WhatsApp (${telefonoLider})`}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '1.1rem', color: '#25D366' }}>
                chat
              </span>
              <span>WhatsApp Líder</span>
            </a>
          )}
        </div>
      </section>

      {/* 2. Dinámica del Último Servicio Registrado */}
      {(metricas?.ultimo_tema || metricas?.hr_inicio) && (
        <article className="participation-card" style={{ marginBottom: '1.25rem' }}>
          <div className="status-card-header">
            <h2 className="section-title">Dinámica del Último Servicio</h2>
            <p className="section-subtitle">Detalles pedagógicos y operativos del reporte reciente</p>
          </div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1rem',
              padding: '0.5rem 0',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span className="material-symbols-outlined text-primary" style={{ fontSize: '1.5rem', marginTop: '0.15rem' }}>
                menu_book
              </span>
              <div>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted, #64748b)', fontWeight: 600 }}>
                  Tema Ministrado
                </span>
                <strong style={{ fontSize: '0.95rem', color: 'var(--primary, #390002)' }}>
                  {metricas?.ultimo_tema || 'Sin tema registrado'}
                </strong>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span className="material-symbols-outlined text-secondary" style={{ fontSize: '1.5rem', marginTop: '0.15rem' }}>
                schedule
              </span>
              <div>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted, #64748b)', fontWeight: 600 }}>
                  Horario de Reunión
                </span>
                <strong style={{ fontSize: '0.95rem' }}>
                  {metricas?.hr_inicio && metricas?.hr_fin
                    ? `${metricas.hr_inicio} - ${metricas.hr_fin}`
                    : metricas?.hr_inicio || 'No registrado'}
                </strong>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span
                className="material-symbols-outlined"
                style={{
                  fontSize: '1.5rem',
                  marginTop: '0.15rem',
                  color: metricas?.cesta_amor ? '#22c55e' : 'var(--text-muted, #64748b)',
                }}
              >
                volunteer_activism
              </span>
              <div>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted, #64748b)', fontWeight: 600 }}>
                  Cesta de Amor
                </span>
                <strong style={{ fontSize: '0.95rem', color: metricas?.cesta_amor ? '#22c55e' : undefined }}>
                  {metricas?.cesta_amor ? 'Entregada a familia en necesidad' : 'No requerida'}
                </strong>
              </div>
            </div>
          </div>
        </article>
      )}

      {/* 3. Tabla de Historial Reciente de Reportes */}
      <section className="table-container-card">
        <div className="table-top-bar" style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid rgba(221, 192, 189, 0.25)' }}>
          <h2 className="section-title">Historial de Reportes</h2>
          <p className="section-subtitle">Registro de actividad y asistencia en los servicios de esta Casa de Paz</p>
        </div>

        <div className="table-scroll" style={{ overflowX: 'auto', padding: '0 1rem 1rem' }}>
          {historial.length > 0 ? (
            <table className="cdp-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr>
                  <th style={{ padding: '0.85rem 1rem' }}>Fecha</th>
                  <th style={{ padding: '0.85rem 1rem', textAlign: 'center' }}>Total Asistencia</th>
                  <th style={{ padding: '0.85rem 1rem', textAlign: 'center' }}>Desglose (R / N / V / C)</th>
                  <th style={{ padding: '0.85rem 1rem', textAlign: 'right' }}>Ofrendas USD</th>
                  <th style={{ padding: '0.85rem 1rem', textAlign: 'right' }}>Ofrendas Bs</th>
                  <th style={{ padding: '0.85rem 1rem', textAlign: 'center' }}>Confesiones</th>
                  <th style={{ padding: '0.85rem 1rem' }}>Tema / Observaciones</th>
                </tr>
              </thead>
              <tbody>
                {historial.map((rep, idx) => {
                  const reg = rep.nro_regulares ?? 0;
                  const nin = rep.nro_niños ?? 0;
                  const vis = rep.nro_visitas ?? 0;
                  const com = rep.nro_comprometidos ?? 0;
                  const asist = rep.asistencia ?? (reg + nin + vis + com);
                  const ofrUsd = Number(rep.ofrendas_usd || 0);
                  const ofrBs = Number(rep.ofrendas_bs || 0);
                  const conf = rep.confesiones || 0;
                  const obs = rep.observaciones || rep.tema || '-';

                  return (
                    <tr key={rep.id ? `rep-${rep.id}` : `rep-${idx}`}>
                      <td style={{ padding: '0.85rem 1rem', fontWeight: 600 }}>{rep.fecha || 'Sin fecha'}</td>
                      <td style={{ padding: '0.85rem 1rem', textAlign: 'center', fontWeight: 700 }}>
                        <span
                          style={{
                            display: 'inline-block',
                            padding: '0.2rem 0.6rem',
                            borderRadius: '999px',
                            background: 'rgba(122, 34, 34, 0.12)',
                            color: 'var(--primary, #390002)',
                          }}
                        >
                          {asist}
                        </span>
                      </td>
                      <td style={{ padding: '0.85rem 1rem', textAlign: 'center', fontSize: '0.82rem', color: 'var(--text-muted, #64748b)' }}>
                        {reg} / {nin} / {vis} / {com}
                      </td>
                      <td style={{ padding: '0.85rem 1rem', textAlign: 'right', fontWeight: 600 }}>
                        ${ofrUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td style={{ padding: '0.85rem 1rem', textAlign: 'right', fontWeight: 600, color: 'var(--text-muted, #64748b)' }}>
                        {ofrBs > 0
                          ? `Bs. ${ofrBs.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                          : '-'}
                      </td>
                      <td style={{ padding: '0.85rem 1rem', textAlign: 'center' }}>
                        {conf > 0 ? (
                          <span style={{ color: '#22c55e', fontWeight: 700 }}>+{conf}</span>
                        ) : (
                          '0'
                        )}
                      </td>
                      <td style={{ padding: '0.85rem 1rem', maxWidth: '240px', whiteSpace: 'normal', fontSize: '0.85rem' }}>
                        {obs}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="empty-state" style={{ padding: '3rem 1rem', textAlign: 'center' }}>
              <span className="material-symbols-outlined empty-icon" style={{ fontSize: '3rem', opacity: 0.4 }}>
                event_busy
              </span>
              <p className="empty-message" style={{ marginTop: '0.5rem', color: 'var(--text-muted, #64748b)' }}>
                Esta Casa de Paz aún no registra reportes históricos en el período activo.
              </p>
            </div>
          )}
        </div>
      </section>
    </section>
  );
};

