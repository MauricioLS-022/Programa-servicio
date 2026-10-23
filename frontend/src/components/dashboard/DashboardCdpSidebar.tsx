import React from 'react';
import type { DashboardMetricas } from '../../types/estructura';

export interface DashboardCdpSidebarProps {
  metricas?: DashboardMetricas;
}

export const DashboardCdpSidebar: React.FC<DashboardCdpSidebarProps> = ({ metricas }) => {
  const historial = metricas?.historial || [];
  const primerReporte = historial[0];
  const observaciones = primerReporte?.observaciones || '';
  const fechaUltimo = primerReporte?.fecha || 'Sin fecha';
  const miniHistorico = metricas?.mini_historico || [];

  return (
    <aside className="sidebar-column fade-in-6">
      {/* 1. Notas del Último Reporte */}
      <article className="warning-card">
        <div className="status-card-header">
          <h2 className="section-title">Notas del Último Reporte</h2>
          <p className="section-subtitle">
            {historial.length > 0 ? `Registrado por ${metricas?.lider || 'Líder'} el ${fechaUltimo}` : 'Sin registros'}
          </p>
        </div>
        <div className="observacion-box">
          <div className="observacion-quote">
            <span className="material-symbols-outlined quote-icon">format_quote</span>
            <p>
              {observaciones ? observaciones : 'No hay observaciones registradas en el último reporte.'}
            </p>
          </div>
        </div>
      </article>

      {/* 2. Dinámica de la Reunión */}
      <article className="participation-card">
        <div className="status-card-header">
          <h2 className="section-title">Dinámica de la Reunión</h2>
          <p className="section-subtitle">Tema y horario del último servicio</p>
        </div>
        <div className="reunion-details-box">
          <div className="reunion-topic">
            <span className="material-symbols-outlined topic-icon">menu_book</span>
            <div>
              <span className="reunion-topic-label">Tema Ministrado</span>
              <h4>{metricas?.ultimo_tema || primerReporte?.tema || 'Sin tema registrado'}</h4>
            </div>
          </div>
          <div className="reunion-meta-row">
            <div className="reunion-meta-item">
              <span className="material-symbols-outlined">schedule</span>
              <div>
                <span className="meta-label">Horario</span>
                <strong>
                  {metricas?.hr_inicio && metricas?.hr_fin
                    ? `${metricas.hr_inicio} - ${metricas.hr_fin}`
                    : metricas?.hr_inicio || 'No registrado'}
                </strong>
              </div>
            </div>
            <div className="reunion-meta-item">
              <span className="material-symbols-outlined">volunteer_activism</span>
              <div>
                <span className="meta-label">Cesta de Amor</span>
                <strong className={metricas?.cesta_amor ? 'text-success' : 'text-muted'}>
                  {metricas?.cesta_amor ? 'Entregada / Sí' : 'No requerida'}
                </strong>
              </div>
            </div>
          </div>
        </div>
      </article>

      {/* 3. Mini Histórico de Asistencia (Últimas 4 reuniones) */}
      <article className="participation-card">
        <div className="status-card-header">
          <h2 className="section-title">Mini Histórico de Asistencia</h2>
          <p className="section-subtitle">Últimas 4 reuniones en gráfico de barras</p>
        </div>
        {miniHistorico.length > 0 ? (
          <div className="mini-chart-container">
            <div className="mini-bars-row">
              {miniHistorico.map((bar, idx) => (
                <div key={`${bar.fecha}-${idx}`} className="mini-bar-col">
                  <div className="mini-bar-track">
                    <div
                      className="mini-bar-fill"
                      style={{
                        ['--bar-height' as string]: `${bar.altura ?? 0}%`,
                        height: `${bar.altura ?? 0}%`,
                      }}
                    >
                      <span className="mini-bar-value">{bar.asistencia}</span>
                    </div>
                  </div>
                  <span className="mini-bar-lbl">{bar.fecha}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <span className="material-symbols-outlined empty-icon">bar_chart</span>
            <p className="empty-message">Aún no hay reuniones para mostrar.</p>
          </div>
        )}
      </article>

      {/* 4. Datos del Anfitrión */}
      <article className="participation-card">
        <div className="status-card-header">
          <h2 className="section-title">Datos del Anfitrión</h2>
          <p className="section-subtitle">Ubicación y contacto geográfico</p>
        </div>
        <div className="anfitrion-details-list">
          <div className="anfitrion-detail-item">
            <span className="material-symbols-outlined">family_restroom</span>
            <div>
              <h4>Anfitrión</h4>
              <p>{metricas?.anfitrion || 'Sin registrar'}</p>
            </div>
          </div>
          <div className="anfitrion-detail-item">
            <span className="material-symbols-outlined">pin_drop</span>
            <div>
              <h4>Dirección</h4>
              <p>{metricas?.direccion || 'Sin registrar'}</p>
            </div>
          </div>
          <div className="anfitrion-detail-item">
            <span className="material-symbols-outlined">call</span>
            <div>
              <h4>Contacto</h4>
              <p>{String(metricas?.telefono_contacto || metricas?.telefono || 'Sin registrar')}</p>
            </div>
          </div>
        </div>
      </article>
    </aside>
  );
};
