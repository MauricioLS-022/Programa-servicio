import React from 'react';
import type { DashboardMetricas } from '../../types/estructura';

export interface DashboardKpiCardsProps {
  metricas?: DashboardMetricas;
  nivel?: 'general' | 'red' | 'cdp';
  periodo?: string;
  hasData?: boolean;
}

export const DashboardKpiCards: React.FC<DashboardKpiCardsProps> = ({
  metricas,
  nivel = 'general',
  periodo = 'semana',
  hasData,
}) => {
  const formatCurrency = (val: number | undefined, currency: 'USD' | 'Bs') => {
    const num = Number(val || 0);
    if (currency === 'USD') {
      return `$${num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    return `Bs. ${num.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  // Coherencia con reglas de Jinja para presencia real de datos
  const isGeneralWithData = Boolean(metricas?.total_casas && metricas.total_casas > 0);
  const isRedWithData = Boolean(
    (metricas?.casas && metricas.casas.length > 0) ||
    (metricas?.casas_activas && metricas.casas_activas > 0)
  );
  const isCdpWithData = Boolean(metricas?.historial && metricas.historial.length > 0);

  const effectiveHasData =
    hasData !== undefined
      ? hasData
      : nivel === 'general'
      ? isGeneralWithData
      : nivel === 'red'
      ? isRedWithData
      : isCdpWithData;

  const totalAsistencia = metricas?.total_asistencia ?? metricas?.asistencia_total ?? metricas?.kpis?.total_asistencia ?? 0;
  const cumplimiento = metricas?.cumplimiento ?? 0;
  const totalCasas = metricas?.total_casas ?? metricas?.casas_activas ?? 0;
  const casasConReporte = metricas?.casas_con_reporte ?? metricas?.reportes_enviados ?? 0;
  const ofrendasUsd = metricas?.ofrendas_usd ?? metricas?.kpis?.total_ofrenda_usd ?? 0;
  const ofrendasBs = metricas?.ofrendas_bs ?? metricas?.kpis?.total_ofrenda_bs ?? 0;
  const conversiones = metricas?.conversiones ?? 0;
  const promedioCasa = metricas?.promedio_casa ?? 0;

  const cumplimientoTitle =
    periodo === 'mes'
      ? `Cumplimiento Mensual (${metricas?.periodo_nombre || 'Mes'})`
      : periodo === 'anio'
      ? `Cumplimiento Anual (${metricas?.periodo_nombre || 'Año'})`
      : 'Cumplimiento Semanal';

  if (nivel === 'cdp') {
    const asistUltimo = metricas?.asistencia_ultimo ?? 0;
    const promHist = metricas?.promedio_historico ?? 0;
    const reporteAlDia = metricas?.estado_reporte === 'enviado' || metricas?.reporte_al_dia;
    const cdpOfrendasUsd = metricas?.ofrendas_usd ?? (metricas?.historial?.[0]?.ofrendas_usd ?? 0);
    const cdpOfrendasBs = metricas?.ofrendas_bs ?? (metricas?.historial?.[0]?.ofrendas_bs ?? 0);

    return (
      <section className="summary-grid">
        <article className="summary-card fade-in-1">
          <span className="material-symbols-outlined card-icon text-primary">event_available</span>
          <h3 className="card-title">Asistencia Último Servicio</h3>
          <div className="card-number" id="kpiAsistenciaCdp">
            {effectiveHasData ? asistUltimo : 'Sin datos'}
          </div>
          <span className="material-symbols-outlined watermark-icon">event_available</span>
        </article>

        <article className="summary-card fade-in-2">
          <span className="material-symbols-outlined card-icon text-secondary">insights</span>
          <h3 className="card-title">Promedio Histórico</h3>
          <div className="card-number" id="kpiPromedioCdp">
            {effectiveHasData ? promHist : 'Sin datos'}
          </div>
          <span className="material-symbols-outlined watermark-icon">insights</span>
        </article>

        <article className="summary-card fade-in-3">
          <span className="material-symbols-outlined card-icon text-secondary">savings</span>
          <h3 className="card-title">Ofrendas Último Servicio</h3>
          <div className="card-number" id="kpiOfrendasCdp" style={{ fontSize: '1.15rem', lineHeight: 1.3 }}>
            {effectiveHasData ? (
              <>
                <div id="kpiOfrendasUsdCdp">{formatCurrency(cdpOfrendasUsd, 'USD')}</div>
                {Number(cdpOfrendasBs) > 0 && (
                  <div id="kpiOfrendasBsCdp" style={{ fontSize: '0.85rem', color: 'var(--text-muted, #64748b)', fontWeight: 600 }}>
                    {formatCurrency(cdpOfrendasBs, 'Bs')}
                  </div>
                )}
              </>
            ) : (
              'Sin datos'
            )}
          </div>
          <span className="material-symbols-outlined watermark-icon">savings</span>
        </article>

        <article className="summary-card fade-in-4">
          <span className="material-symbols-outlined card-icon text-secondary">send</span>
          <h3 className="card-title">Estado del Reporte</h3>
          <div className="card-number" id="kpiEstadoCdp" style={{ display: 'flex', alignItems: 'center' }}>
            {effectiveHasData ? (
              <span className={`badge-status ${reporteAlDia ? 'badge-success' : 'badge-warning'}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.82rem', padding: '0.35rem 0.65rem' }}>
                <span className="material-symbols-outlined" style={{ fontSize: '0.95rem' }}>
                  {reporteAlDia ? 'check_circle' : 'schedule'}
                </span>
                {reporteAlDia ? 'Al día (Esta semana)' : 'Pendiente esta semana'}
              </span>
            ) : (
              'Sin datos'
            )}
          </div>
          <span className="material-symbols-outlined watermark-icon">send</span>
        </article>
      </section>
    );
  }

  if (nivel === 'red') {
    return (
      <section className="summary-grid">
        <article className="summary-card fade-in-1">
          <span className="material-symbols-outlined card-icon text-primary">groups</span>
          <h3 className="card-title">Asistencia Total</h3>
          <div className="card-number" id="kpiTotalAsistenciaRed">
            {effectiveHasData ? totalAsistencia : 'Sin datos'}
          </div>
          <span className="material-symbols-outlined watermark-icon">groups</span>
        </article>

        <article className="summary-card fade-in-2">
          <span className="material-symbols-outlined card-icon text-secondary">home_work</span>
          <h3 className="card-title">Promedio por Casa</h3>
          <div className="card-number" id="kpiPromedioCasaRed">
            {effectiveHasData ? promedioCasa : 'Sin datos'}
          </div>
          <span className="material-symbols-outlined watermark-icon">home_work</span>
        </article>

        <article className="summary-card fade-in-3">
          <span className="material-symbols-outlined card-icon text-primary-container">person_add</span>
          <h3 className="card-title">Confesiones de Fe</h3>
          <div className="card-number" id="kpiConversionesRed">
            {effectiveHasData ? conversiones : 'Sin datos'}
          </div>
          <span className="material-symbols-outlined watermark-icon">person_add</span>
        </article>

        <article className="summary-card fade-in-4">
          <span className="material-symbols-outlined card-icon text-secondary">volunteer_activism</span>
          <h3 className="card-title">Ofrendas de Red</h3>
          <div className="card-number" id="kpiOfrendasRed" style={{ fontSize: '1.15rem', lineHeight: 1.3 }}>
            {effectiveHasData ? (
              <>
                <div id="kpiOfrendasUsdRed">{formatCurrency(ofrendasUsd, 'USD')}</div>
                <div id="kpiOfrendasBsRed" style={{ fontSize: '0.85rem', color: 'var(--text-muted, #64748b)', fontWeight: 600 }}>
                  {formatCurrency(ofrendasBs, 'Bs')}
                </div>
              </>
            ) : (
              'Sin datos'
            )}
          </div>
          <span className="material-symbols-outlined watermark-icon">volunteer_activism</span>
        </article>
      </section>
    );
  }

  // Vista General y por defecto
  return (
    <section className="summary-grid">
      {/* 1. Asistencia Total */}
      <article className="summary-card fade-in-1">
        <span className="material-symbols-outlined card-icon text-primary">groups</span>
        <h3 className="card-title">Total Asistencia</h3>
        <div className="card-number" id="kpiTotalAsistenciaGen">
          {effectiveHasData ? totalAsistencia : 'Sin datos'}
        </div>
        <span className="material-symbols-outlined watermark-icon">groups</span>
      </article>

      {/* 2. Cumplimiento */}
      <article className="summary-card fade-in-2">
        <span className="material-symbols-outlined card-icon text-secondary">check_circle</span>
        <h3 className="card-title" id="lblCumplimientoTitleGen">
          {cumplimientoTitle}
        </h3>
        <div className="card-number" id="kpiCumplimientoGen" style={{ fontSize: '1.15rem', lineHeight: 1.3 }}>
          {effectiveHasData ? (
            <>
              <div id="kpiCumplimientoPctGen">{cumplimiento}%</div>
              <div id="kpiCumplimientoSubGen" style={{ fontSize: '0.85rem', color: 'var(--text-muted, #64748b)', fontWeight: 600 }}>
                {casasConReporte} de {totalCasas} CDP
              </div>
            </>
          ) : (
            'Sin datos'
          )}
        </div>
        <span className="material-symbols-outlined watermark-icon">check_circle</span>
      </article>

      {/* 3. Ofrendas Acumuladas */}
      <article className="summary-card fade-in-3">
        <span className="material-symbols-outlined card-icon text-primary-container">volunteer_activism</span>
        <h3 className="card-title">Ofrendas Acumuladas</h3>
        <div className="card-number" id="kpiOfrendasGen" style={{ fontSize: '1.15rem', lineHeight: 1.3 }}>
          {effectiveHasData ? (
            <>
              <div id="kpiOfrendasUsdGen">{formatCurrency(ofrendasUsd, 'USD')}</div>
              <div id="kpiOfrendasBsGen" style={{ fontSize: '0.85rem', color: 'var(--text-muted, #64748b)', fontWeight: 600 }}>
                {formatCurrency(ofrendasBs, 'Bs')}
              </div>
            </>
          ) : (
            'Sin datos'
          )}
        </div>
        <span className="material-symbols-outlined watermark-icon">volunteer_activism</span>
      </article>

      {/* 4. Confesiones de Fe */}
      <article className="summary-card fade-in-4">
        <span className="material-symbols-outlined card-icon text-secondary">trending_up</span>
        <h3 className="card-title">Confesiones de Fe</h3>
        <div className="card-number" id="kpiConversionesGen">
          {effectiveHasData ? conversiones : 'Sin datos'}
        </div>
        <span className="material-symbols-outlined watermark-icon">trending_up</span>
      </article>
    </section>
  );
};

