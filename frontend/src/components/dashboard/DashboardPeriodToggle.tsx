import React from 'react';

export type PeriodoTipo = 'semana' | 'mes' | 'anio';

export interface DashboardPeriodToggleProps {
  periodo: PeriodoTipo;
  onChange: (periodo: PeriodoTipo) => void;
  disabled?: boolean;
}

export const DashboardPeriodToggle: React.FC<DashboardPeriodToggleProps> = ({
  periodo,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="period-toggle-bar fade-in-1">
      <div
        className="period-toggle-group"
        role="radiogroup"
        aria-label="Seleccionar período de análisis"
      >
        <button
          type="button"
          disabled={disabled}
          onClick={() => onChange('semana')}
          className={`period-btn ${periodo === 'semana' ? 'active' : ''}`}
          aria-pressed={periodo === 'semana'}
          aria-label="Filtrar por período semanal"
        >
          <span className="material-symbols-outlined">calendar_view_week</span>
          <span>Semana</span>
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={() => onChange('mes')}
          className={`period-btn ${periodo === 'mes' ? 'active' : ''}`}
          aria-pressed={periodo === 'mes'}
          aria-label="Filtrar por período mensual"
        >
          <span className="material-symbols-outlined">calendar_month</span>
          <span>Mes</span>
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={() => onChange('anio')}
          className={`period-btn ${periodo === 'anio' ? 'active' : ''}`}
          aria-pressed={periodo === 'anio'}
          aria-label="Filtrar por período anual"
        >
          <span className="material-symbols-outlined">calendar_today</span>
          <span>Año</span>
        </button>
      </div>
    </div>
  );
};

