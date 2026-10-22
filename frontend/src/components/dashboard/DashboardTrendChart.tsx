import React from 'react';
import type { TendenciaItem } from '../../types/estructura';

export interface DashboardTrendChartProps {
  tendencia?: TendenciaItem[];
  promedioTendencia?: number;
  periodo?: string;
  periodoNombre?: string;
  nivel?: 'general' | 'red' | 'cdp';
  redNombre?: string;
}

export const DashboardTrendChart: React.FC<DashboardTrendChartProps> = ({
  tendencia = [],
  promedioTendencia = 0,
  periodo = 'semana',
  periodoNombre = '',
  nivel = 'general',
  redNombre = '',
}) => {
  // Título y subtítulo dinámicos
  let title = 'Asistencia por Red esta Semana';
  let subtitle = 'Desglose por Red del último reporte recibido';

  if (nivel === 'red') {
    if (periodo === 'mes') {
      title = `Evolución Semanal del Mes (${periodoNombre || 'Mes'})`;
      subtitle = `Histórico semanal de ${periodoNombre || 'el mes en curso'} en ${redNombre}`;
    } else if (periodo === 'anio') {
      title = `Evolución Mensual del Año (${periodoNombre || 'Año'})`;
      subtitle = `Histórico mes a mes de ${periodoNombre || 'el año en curso'} en ${redNombre}`;
    } else {
      title = 'Asistencia por Casa esta Semana';
      subtitle = `Desglose por Casa de Paz en ${redNombre}`;
    }
  } else if (nivel === 'cdp') {
    title = 'Historial de Asistencia';
    subtitle = 'Evolución de las últimas reuniones en esta Casa de Paz';
  } else {
    if (periodo === 'mes') {
      title = `Evolución Semanal del Mes (${periodoNombre || 'Mes'})`;
      subtitle = `Histórico semanal de ${periodoNombre || 'el mes en curso'}`;
    } else if (periodo === 'anio') {
      title = `Evolución Mensual del Año (${periodoNombre || 'Año'})`;
      subtitle = `Histórico mes a mes de ${periodoNombre || 'el año en curso'}`;
    }
  }

  // Cálculo de variación porcentual
  let variacion: number | null = null;
  let variacionTipo: 'vs anterior' | 'vs promedio' = 'vs anterior';

  if (tendencia.length > 1) {
    const curr = tendencia[tendencia.length - 1]?.asistencia || 0;
    const prev = tendencia[tendencia.length - 2]?.asistencia || 0;
    if (prev > 0) {
      variacion = Math.round(((curr - prev) / prev) * 1000) / 10;
      variacionTipo = 'vs anterior';
    } else if (promedioTendencia > 0) {
      variacion = Math.round(((curr - promedioTendencia) / promedioTendencia) * 1000) / 10;
      variacionTipo = 'vs promedio';
    } else {
      variacion = 0;
    }
  }

  const hasScroll = tendencia.length > 7;

  return (
    <section className="chart-card fade-in-5">
      <div className="chart-header">
        <div>
          <h2 className="section-title">{title}</h2>
          <p className="section-subtitle">{subtitle}</p>
        </div>

        {variacion !== null && (
          <div id="trendBadge">
            <div
              className={`trend-badge-pill ${variacion < 0 ? 'negative' : ''}`}
              role="status"
              aria-label={`Variación: ${variacion > 0 ? `+${variacion}` : variacion}% respecto a la medición ${variacionTipo}`}
            >
              <span className="material-symbols-outlined">
                {variacion > 0 ? 'trending_up' : variacion < 0 ? 'trending_down' : 'trending_flat'}
              </span>
              <span>
                {variacion > 0 ? `+${variacion}` : variacion}% {variacionTipo}
              </span>
            </div>
          </div>
        )}
      </div>

      <div className={`trend-chart-area ${hasScroll ? 'has-scroll' : ''}`}>
        <div
          className={`trend-bars-container ${hasScroll ? 'has-scroll' : ''}`}
          role="region"
          aria-label="Gráfica de tendencia de asistencia"
        >
          {tendencia.length > 0 ? (
            tendencia.map((item, idx) => {
              const pct = item.porcentaje ?? 0;
              const tipId = `trend-tip-${idx}`;
              return (
                <div
                  key={`${item.semana}-${idx}`}
                  className="trend-bar-col"
                  tabIndex={0}
                  role="graphics-symbol"
                  aria-roledescription="barra de asistencia"
                  aria-describedby={tipId}
                  aria-label={`${item.semana}: ${item.asistencia} asistentes, ${pct}% del pico`}
                >
                  <div className="trend-bar-track">
                    <div
                      className="trend-bar-fill"
                      style={{
                        height: `${pct}%`,
                        ['--bar-height' as string]: `${pct}%`,
                      }}
                    >
                      <span className="trend-bar-val">{item.asistencia}</span>
                    </div>
                  </div>
                  <span className="trend-bar-lbl">
                    {item.semana}
                    {item.rango_fecha && <span className="trend-bar-sublbl">{item.rango_fecha}</span>}
                  </span>
                  <div className="trend-tooltip" id={tipId} role="tooltip" aria-hidden="true">
                    <span className="tooltip-date">{item.fecha_completa || item.semana}</span>
                    <span className="tooltip-val">
                      <strong>{item.asistencia}</strong> asistentes
                    </span>
                    <span className="tooltip-pct">{pct}% del pico</span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="empty-state" style={{ padding: '2.5rem 1rem', width: '100%' }}>
              <span className="material-symbols-outlined empty-icon">monitoring</span>
              <p className="empty-message">Aún no hay reportes para mostrar una tendencia.</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

