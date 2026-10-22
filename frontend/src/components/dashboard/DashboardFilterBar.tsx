import React from 'react';
import type { Red, CasaDePaz } from '../../types/estructura';

export interface DashboardFilterBarProps {
  rol?: string;
  nivel: 'general' | 'red' | 'cdp';
  onNivelChange: (nivel: 'general' | 'red' | 'cdp') => void;
  redId?: number | string;
  onRedChange: (redId: number | string) => void;
  redes: Red[];
  cdpId?: number | string;
  onCdpChange: (cdpId: number | string) => void;
  casas: CasaDePaz[];
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onReset: () => void;
}

export const DashboardFilterBar: React.FC<DashboardFilterBarProps> = ({
  rol,
  nivel,
  onNivelChange,
  redId = '',
  onRedChange,
  redes,
  cdpId = '',
  onCdpChange,
  casas,
  searchQuery,
  onSearchChange,
  onReset,
}) => {
  const isSupervisor = rol === 'supervisor';

  // Filtrar casas pertenecientes a la red seleccionada si aplica
  const casasFiltradas = React.useMemo(() => {
    if (!redId) return casas;
    const rIdNum = typeof redId === 'string' ? parseInt(redId, 10) : redId;
    return casas.filter((c) => c.red_id === rIdNum);
  }, [casas, redId]);

  return (
    <section className="filter-bar-card">
      <div className="filter-form">
        {/* Selector de Nivel de Vista */}
        <div className="filter-group">
          <label htmlFor="selectNivel" className="filter-label">
            Nivel de Vista
          </label>
          <select
            id="selectNivel"
            value={nivel}
            onChange={(e) => onNivelChange(e.target.value as 'general' | 'red' | 'cdp')}
            className="filter-select"
            aria-label="Seleccionar nivel de vista del panel"
          >
            {isSupervisor ? (
              <>
                <option value="red">Mi Red (Zonal)</option>
                <option value="cdp">Por Casa de Paz</option>
              </>
            ) : (
              <>
                <option value="general">Vista General (Iglesia)</option>
                <option value="red">Por Red / Zonal</option>
                <option value="cdp">Por Casa de Paz</option>
              </>
            )}
          </select>
        </div>

        {/* Selector de Red (Visible en Admin cuando nivel != 'general') */}
        {!isSupervisor && nivel !== 'general' && (
          <div className="filter-group" id="groupRed">
            <label htmlFor="selectRed" className="filter-label">
              Seleccionar Red
            </label>
            <select
              id="selectRed"
              value={redId}
              onChange={(e) => {
                onRedChange(e.target.value);
                onCdpChange(''); // Reiniciar CDP al cambiar de red
              }}
              className="filter-select"
              aria-label="Seleccionar red ministerial"
            >
              <option value="">-- Seleccionar Red --</option>
              {redes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.nombre}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Selector de Casa de Paz (Visible cuando nivel == 'cdp') */}
        {nivel === 'cdp' && (
          <div className="filter-group" id="groupCdp">
            <label htmlFor="selectCdp" className="filter-label">
              Casa de Paz
            </label>
            <select
              id="selectCdp"
              value={cdpId}
              onChange={(e) => onCdpChange(e.target.value)}
              className="filter-select"
              aria-label="Seleccionar casa de paz"
            >
              <option value="">-- Seleccionar Casa de Paz --</option>
              {casasFiltradas.length === 0 ? (
                <option value="" disabled>
                  Sin Casas de Paz en esta red
                </option>
              ) : (
                casasFiltradas.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.codigo} {c.anfitrion ? `· ${c.anfitrion}` : ''}
                  </option>
                ))
              )}
            </select>
          </div>
        )}

        {/* Barra de búsqueda rápida */}
        <div className="filter-group search-group">
          <label htmlFor="searchInput" className="filter-label">
            <span className="material-symbols-outlined" style={{ fontSize: '0.8rem', marginRight: '0.2rem' }}>
              search
            </span>
            Buscar rápido
          </label>
          <div className="search-input-wrapper">
            <input
              type="text"
              id="searchInput"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="filter-search"
              aria-label="Buscar rápido por red, código de casa o líder"
              placeholder="Buscar por Red, código CDP o líder..."
            />
            {searchQuery && (
              <button
                type="button"
                id="clearSearch"
                onClick={() => onSearchChange('')}
                className="clear-search-btn"
                aria-label="Limpiar campo de búsqueda"
                title="Limpiar búsqueda"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            )}
          </div>
        </div>

        {/* Botón de restablecimiento */}
        <div className="filter-actions">
          <button
            type="button"
            onClick={onReset}
            className="btn-reset"
            aria-label="Restablecer filtros del dashboard"
            title="Restablecer filtros"
          >
            <span className="material-symbols-outlined">restart_alt</span>
          </button>
        </div>
      </div>
    </section>
  );
};

