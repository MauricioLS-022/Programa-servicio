import React, { useState } from 'react';
import type { DistribucionAsistencia } from '../../types/estructura';

export interface DashboardCategoryDonutProps {
  distribucion?: DistribucionAsistencia;
  total?: number;
  periodo?: string;
  periodoNombre?: string;
  nivel?: 'general' | 'red' | 'cdp';
  redNombre?: string;
}

export const DashboardCategoryDonut: React.FC<DashboardCategoryDonutProps> = ({
  distribucion,
  total = 0,
  periodo = 'semana',
  periodoNombre = '',
  nivel = 'general',
  redNombre = '',
}) => {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const regulares = distribucion?.regulares ?? 0;
  const ninos = distribucion?.ninos ?? 0;
  const visitas = distribucion?.visitas ?? 0;
  const comprometidos = distribucion?.comprometidos ?? 0;

  const sumTotal = regulares + ninos + visitas + comprometidos;
  const displayTotal = total || sumTotal;
  const pctBase = sumTotal > 0 ? sumTotal : 1;

  const categories = [
    {
      key: 'regular',
      label: 'Regulares',
      count: regulares,
      pct: Math.round((regulares / pctBase) * 100),
      color: 'var(--metric-regular, #7a2222)',
      dotClass: 'dot regular',
    },
    {
      key: 'ninos',
      label: 'Niños',
      count: ninos,
      pct: Math.round((ninos / pctBase) * 100),
      color: 'var(--metric-ninos, #c86b6b)',
      dotClass: 'dot ninos',
    },
    {
      key: 'visitas',
      label: 'Visitas',
      count: visitas,
      pct: Math.round((visitas / pctBase) * 100),
      color: 'var(--metric-visitas, #e9b9b9)',
      dotClass: 'dot visitas',
    },
    {
      key: 'comprometidos',
      label: 'Comprometidos',
      count: comprometidos,
      pct: Math.round((comprometidos / pctBase) * 100),
      color: 'var(--metric-comprometidos, #2b0000)',
      dotClass: 'dot comprometidos',
    },
  ];

  // SVG Donut calculation
  const C = 2 * Math.PI * 38; // ~238.761
  let accumulatedPct = 0;

  const segments = categories.map((cat) => {
    const exactPct = sumTotal > 0 ? (cat.count / sumTotal) * 100 : 0;
    const strokeLen = (exactPct / 100) * C;
    const strokeOffset = -((accumulatedPct / 100) * C);
    accumulatedPct += exactPct;

    return {
      ...cat,
      strokeLen,
      strokeOffset,
    };
  });

  const activeData = activeCategory ? categories.find((c) => c.key === activeCategory) : null;
  const centerValue = activeData ? activeData.count : displayTotal;
  const centerLabel = activeData ? activeData.label.toUpperCase() : 'TOTAL';

  // Subtítulo dinámico
  let subtitle = 'Composición de membresía y consolidación de la semana activa';
  if (nivel === 'red') {
    if (periodo === 'mes') {
      subtitle = `Composición de miembros en el mes activo`;
    } else if (periodo === 'anio') {
      subtitle = `Composición de miembros en el año activo`;
    } else {
      subtitle = `Composición de asistentes en ${redNombre || 'la red'}`;
    }
  } else {
    if (periodo === 'mes') {
      subtitle = `Composición acumulada de la membresía en ${periodoNombre || 'el mes en curso'}`;
    } else if (periodo === 'anio') {
      subtitle = `Composición de membresía y consolidación de ${periodoNombre || 'el año activo'}`;
    }
  }

  return (
    <section className="chart-card fade-in-6" style={{ marginTop: '1rem' }}>
      <div className="chart-header">
        <div>
          <h2 className="section-title">
            {nivel === 'red' ? 'Distribución de Asistencia' : 'Distribución por Categoría'}
          </h2>
          <p className="section-subtitle">{subtitle}</p>
        </div>
      </div>

      <div className="chart-area">
        <ul className="chart-legend" role="list" aria-label="Leyenda de distribución de asistencia">
          {categories.map((cat) => (
            <li
              key={cat.key}
              className={`legend-item ${activeCategory === cat.key ? 'active' : ''}`}
              tabIndex={0}
              role="listitem"
              data-category={cat.key}
              data-count={cat.count}
              data-percent={cat.pct}
              aria-label={`${cat.label}: ${cat.count} personas (${cat.pct}%)`}
              onMouseEnter={() => setActiveCategory(cat.key)}
              onMouseLeave={() => setActiveCategory(null)}
              onFocus={() => setActiveCategory(cat.key)}
              onBlur={() => setActiveCategory(null)}
            >
              <span className={cat.dotClass} /> {cat.label} ({cat.count})
              <div
                className="legend-tooltip"
                role="tooltip"
                aria-hidden={activeCategory !== cat.key}
                style={{ display: activeCategory === cat.key ? 'block' : undefined }}
              >
                <span className="tooltip-title">{cat.label}</span>
                <span className="tooltip-val">
                  <strong>{cat.count}</strong> personas
                </span>
                <span className="tooltip-pct">{cat.pct}% del total</span>
              </div>
            </li>
          ))}
        </ul>

        <div
          className="donut-wrapper"
          role="region"
          aria-label="Gráfico de distribución total de asistencia"
          style={{
            position: 'relative',
            width: '220px',
            height: '220px',
            minHeight: '220px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto',
            flexShrink: 0,
          }}
        >
          <div
            className="donut-ring has-svg"
            style={{
              position: 'relative',
              width: '180px',
              height: '180px',
              minWidth: '180px',
              minHeight: '180px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            {/* SVG Anillo */}
            <svg
              className="donut-svg"
              viewBox="0 0 100 100"
              width="100%"
              height="100%"
              role="graphics-document"
              aria-label="Segmentos interactivos del gráfico circular"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                borderRadius: '50%',
                zIndex: 2,
                overflow: 'visible',
                pointerEvents: 'auto',
                display: 'block',
              }}
            >
              {sumTotal === 0 ? (
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="none"
                  stroke="rgba(137, 114, 111, 0.2)"
                  strokeWidth="16"
                  pointerEvents="none"
                />
              ) : (
                segments.map((seg) => {
                  if (seg.count <= 0) return null;
                  const isHovered = activeCategory === seg.key;
                  return (
                    <circle
                      key={seg.key}
                      cx="50"
                      cy="50"
                      r="38"
                      fill="none"
                      className={`donut-segment segment-${seg.key} ${isHovered ? 'active' : ''}`}
                      stroke={seg.color}
                      strokeWidth={isHovered ? 20 : 16}
                      strokeDasharray={`${seg.strokeLen} ${C - seg.strokeLen}`}
                      strokeDashoffset={`${seg.strokeOffset}`}
                      transform="rotate(-90 50 50)"
                      tabIndex={0}
                      role="graphics-symbol"
                      aria-roledescription="segmento de gráfico circular"
                      aria-label={`${seg.label}: ${seg.count} (${seg.pct}%)`}
                      style={{
                        pointerEvents: 'stroke',
                        cursor: 'pointer',
                        transition: 'stroke-width 0.2s ease',
                      }}
                      onMouseEnter={() => setActiveCategory(seg.key)}
                      onMouseLeave={() => setActiveCategory(null)}
                      onFocus={() => setActiveCategory(seg.key)}
                      onBlur={() => setActiveCategory(null)}
                    />
                  );
                })
              )}
            </svg>

            {/* Centro con Total o Categoría Activa */}
            <div
              className="donut-center"
              aria-live="polite"
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                pointerEvents: 'none',
                zIndex: 10,
                width: '100px',
                height: '100px',
                margin: 0,
                padding: 0,
                boxSizing: 'border-box',
              }}
            >
              <span
                className="donut-label"
                style={{
                  display: 'block',
                  fontSize: '0.75rem',
                  marginBottom: '0.2rem',
                  lineHeight: 1.2,
                  letterSpacing: '0.05em',
                  fontWeight: 700,
                  color: 'var(--text-muted, #64748b)',
                }}
              >
                {centerLabel}
              </span>
              <span
                className="donut-number"
                style={{
                  display: 'block',
                  fontSize: '1.6rem',
                  fontWeight: 800,
                  lineHeight: 1,
                  color: 'var(--primary, #390002)',
                }}
              >
                {centerValue.toLocaleString()}
              </span>
            </div>
          </div>

          {/* Tooltip flotante interactivo para los segmentos del Donut */}
          {activeData && (
            <div
              className="donut-tooltip visible"
              role="tooltip"
              aria-live="polite"
              style={{
                position: 'absolute',
                bottom: '-14px',
                left: '50%',
                transform: 'translateX(-50%) translateY(100%)',
                zIndex: 40,
                pointerEvents: 'none',
              }}
            >
              <span className="tooltip-title">{activeData.label}</span>
              <span className="tooltip-val">
                <strong>{activeData.count}</strong> personas
              </span>
              <span className="tooltip-pct">{activeData.pct}% del total</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

