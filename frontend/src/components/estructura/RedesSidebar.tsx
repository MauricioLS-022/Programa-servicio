import React from 'react';
import { Icon } from '../ui/Icon';
import { cleanRedName } from '../../hooks/useEstructuraController';
import type { Red, CasaDePaz } from '../../types/estructura';

interface RedesSidebarProps {
  isSupervisor: boolean;
  redes: Red[];
  casas: CasaDePaz[];
  selectedRedId: string;
  effectiveRedId: string;
  totalCasasCongregacion: number;
  totalPendientesCongregacion: number;
  activeMenuRedId: number | null;
  sidebarRef: React.RefObject<HTMLElement | null>;
  isTouchDevice: boolean;
  canScrollLeft: boolean;
  canScrollRight: boolean;
  onScrollSidebar: (direction: 'left' | 'right') => void;
  onSelectRed: (id: number | string) => void;
  onToggleContextMenu: (red: Red, triggerEl: HTMLElement) => void;
}

export const RedesSidebar: React.FC<RedesSidebarProps> = ({
  isSupervisor,
  redes,
  casas,
  selectedRedId,
  effectiveRedId,
  totalCasasCongregacion,
  totalPendientesCongregacion,
  activeMenuRedId,
  sidebarRef,
  isTouchDevice,
  canScrollLeft,
  canScrollRight,
  onScrollSidebar,
  onSelectRed,
  onToggleContextMenu,
}) => {
  return (
    <div className="redes-sidebar-wrapper">
      {!isTouchDevice && (
        <>
          <button
            type="button"
            className={`scroll-arrow scroll-arrow-left ${canScrollLeft ? 'visible' : ''}`}
            onClick={() => onScrollSidebar('left')}
            aria-label="Desplazar a la izquierda"
          >
            <Icon name="chevron_left" size={18} />
          </button>
          <button
            type="button"
            className={`scroll-arrow scroll-arrow-right ${canScrollRight ? 'visible' : ''}`}
            onClick={() => onScrollSidebar('right')}
            aria-label="Desplazar a la derecha"
          >
            <Icon name="chevron_right" size={18} />
          </button>
        </>
      )}

      <aside className="redes-sidebar" ref={sidebarRef}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">{isSupervisor ? 'Mi Red' : 'Redes Activas'}</h2>
          <span className="badge badge-secondary">
            {redes.length} {redes.length === 1 ? 'Red' : 'Redes'}
          </span>
        </div>

        <div className="redes-list">
          {!isSupervisor && (
            <div
              className={`red-card red-card-all ${
                !selectedRedId || selectedRedId === 'all' ? 'active' : ''
              }`}
            >
              <button
                type="button"
                className="red-filter-trigger"
                onClick={() => onSelectRed('')}
                aria-pressed={!selectedRedId || selectedRedId === 'all'}
              >
                <div className="red-header">
                  <span className="red-name">Todas las redes</span>
                  {totalPendientesCongregacion > 0 && (
                    <span className="red-pending-badge">
                      {totalPendientesCongregacion} pend.
                    </span>
                  )}
                </div>
                <p className="red-leader">Vista general</p>
                <div className="red-stats">
                  <span className="red-count">
                    {totalCasasCongregacion}{' '}
                    {totalCasasCongregacion === 1 ? 'Casa Vinculada' : 'Casas Vinculadas'}
                  </span>
                </div>
              </button>
            </div>
          )}

          {redes.map((r) => {
            const isSelected = String(effectiveRedId) === String(r.id);
            const isPaused = !r.is_active;
            const casasInRed = casas.filter((c) => Number(c.red_id) === Number(r.id)).length;
            const pendientesInRed = casas.filter(
              (c) => Number(c.red_id) === Number(r.id) && c.sin_reporte_7d && c.is_active
            ).length;
            const displayName = cleanRedName(r.nombre);
            const isMenuOpen = activeMenuRedId === r.id;

            return (
              <div
                key={r.id}
                className={`red-card ${isSelected ? 'active' : ''} ${
                  isPaused ? 'red-card-paused' : ''
                } ${isMenuOpen ? 'menu-open' : ''}`}
                style={{ zIndex: isMenuOpen ? 50 : undefined }}
              >
                <button
                  type="button"
                  className="red-filter-trigger"
                  onClick={() => onSelectRed(r.id)}
                  aria-pressed={isSelected}
                >
                  <div className="red-header">
                    <span className="red-name">Red {displayName}</span>
                    {isPaused && <span className="badge badge-warning">En pausa</span>}
                    {pendientesInRed > 0 && (
                      <span className="red-pending-badge">{pendientesInRed} pend.</span>
                    )}
                  </div>
                  <p className="red-leader">
                    Supervisor: {r.supervisor_nombre || r.supervisor || 'Sin asignar'}
                  </p>
                  <div className="red-stats">
                    {casasInRed > 0 && (
                      <div className="avatars">
                        <span className="avatar-circle avatar-maroon">
                          <Icon name="home" size={14} />
                        </span>
                        {casasInRed > 1 && (
                          <span className="avatar-circle avatar-maroon">
                            <Icon name="home" size={14} />
                          </span>
                        )}
                        {casasInRed > 2 && (
                          <span className="avatar-circle avatar-count">
                            +{casasInRed - 2}
                          </span>
                        )}
                      </div>
                    )}
                    <span className="red-count">
                      {casasInRed} {casasInRed === 1 ? 'Casa Vinculada' : 'Casas Vinculadas'}
                    </span>
                  </div>
                </button>

                {!isSupervisor && (
                  <button
                    type="button"
                    className="icon-more menu-trigger"
                    aria-label={`Opciones de ${r.nombre}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleContextMenu(r, e.currentTarget);
                    }}
                  >
                    <Icon name="more_vert" size={16} />
                  </button>
                )}
              </div>
            );
          })}

          {redes.length === 0 && (
            <div className="empty-state empty-state-sidebar">
              <Icon name="hub" size={24} />
              <strong>Sin redes registradas</strong>
              <span>Crea una red para comenzar.</span>
            </div>
          )}
        </div>

        {/* Tarjeta de Resumen de Impacto */}
        <div className="impact-card">
          <div className="impact-content">
            <h3>{isSupervisor ? 'Estado de Salud de mi Red' : 'Resumen de Impacto'}</h3>
            <p className="impact-subtitle">
              {isSupervisor
                ? 'Casas de Paz activas y reportando'
                : 'Total alcance de redes'}
            </p>
            <div className="impact-number">{totalCasasCongregacion}</div>
            <p className="impact-note">Casas de Paz registradas</p>
          </div>
          <div className="watermark-icon">
            <Icon name="group" size={48} />
          </div>
        </div>
      </aside>
    </div>
  );
};
