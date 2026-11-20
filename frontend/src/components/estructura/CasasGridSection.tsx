import React from 'react';
import { Link } from 'react-router-dom';
import { Icon } from '../ui/Icon';
import { CumplimientoBanner } from './CumplimientoBanner';
import type { FiltroEstadoEstructura } from '../../hooks/useEstructuraController';
import type { CasaDePaz, Red } from '../../types/estructura';

interface CasasGridSectionProps {
  isAdmin: boolean;
  isSupervisor: boolean;
  isLoading: boolean;
  selectedRedId: string;
  effectiveRedId: string;
  selectedRedObj: Red | null;
  selectedRedName: string;
  filtroEstado: FiltroEstadoEstructura;
  search: string;
  filteredCasas: CasaDePaz[];
  highlightedCdpId: string | null;
  pendingInScope: number;
  onSearchChange: (value: string) => void;
  onFiltroEstadoChange: (estado: FiltroEstadoEstructura) => void;
  onOpenMobileSheet: () => void;
  onOpenNewCdpModal: () => void;
  onExportCasas?: (format: 'xlsx' | 'csv') => void;
  exportingFormat?: 'xlsx' | 'csv' | null;
}

export const CasasGridSection: React.FC<CasasGridSectionProps> = ({
  isAdmin,
  isSupervisor,
  isLoading,
  selectedRedId,
  effectiveRedId,
  selectedRedObj,
  selectedRedName,
  filtroEstado,
  search,
  filteredCasas,
  highlightedCdpId,
  pendingInScope,
  onSearchChange,
  onFiltroEstadoChange,
  onOpenMobileSheet,
  onOpenNewCdpModal,
  onExportCasas,
  exportingFormat = null,
}) => {
  return (
    <section className="casas-section">
      <div className="casas-header">
        <div>
          <h3 className="section-title">Casas de Paz</h3>
          <p className="section-subtitle">
            Mostrando las casas de{' '}
            <strong id="casasFilterLabel">
              {filtroEstado === 'pendientes_7d'
                ? `${selectedRedName} (solo pendientes)`
                : selectedRedName}
            </strong>
            {selectedRedObj && !isSupervisor && (
              <button
                type="button"
                className="btn-mobile-manage-red"
                onClick={onOpenMobileSheet}
                aria-label={`Gestionar ${selectedRedObj.nombre}`}
                title="Gestionar red"
              >
                <Icon name="more_vert" size={14} />
                <span>Opciones</span>
              </button>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className="search-bar">
            <span className="icon-search">
              <Icon name="search" size={16} />
            </span>
            <input
              type="text"
              id="casasSearchInput"
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Buscar por código, líder, anfitrión o zona..."
              aria-label="Buscar Casas de Paz"
            />
          </div>
          {onExportCasas && (isAdmin || isSupervisor) && (
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => onExportCasas('xlsx')}
                disabled={exportingFormat !== null}
                aria-label="Exportar Casas de Paz a Excel"
                title="Exportar Casas de Paz a Excel (.xlsx)"
                className="btn btn-outline text-xs py-1.5 px-2.5 inline-flex items-center gap-1.5 disabled:opacity-50"
              >
                <Icon name="table_chart" size={15} />
                <span>{exportingFormat === 'xlsx' ? 'Generando...' : 'Excel'}</span>
              </button>
              <button
                type="button"
                onClick={() => onExportCasas('csv')}
                disabled={exportingFormat !== null}
                aria-label="Exportar Casas de Paz a CSV"
                title="Exportar Casas de Paz a CSV"
                className="btn btn-outline text-xs py-1.5 px-2.5 inline-flex items-center gap-1.5 disabled:opacity-50"
              >
                <Icon name="download" size={15} />
                <span>{exportingFormat === 'csv' ? 'Generando...' : 'CSV'}</span>
              </button>
            </div>
          )}
        </div>
      </div>

      <CumplimientoBanner
        pendingInScope={pendingInScope}
        effectiveRedId={effectiveRedId}
        selectedRedName={selectedRedName}
        filtroEstado={filtroEstado}
        hasFilteredCasas={filteredCasas.length > 0}
        onFiltroEstadoChange={onFiltroEstadoChange}
      />

      {isLoading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <Icon name="progress_activity" size={32} className="text-vino dark:text-vino-light icon-spin" />
          <p className="text-sm font-medium text-text-muted dark:text-neutral-400">
            Cargando estructura de Casas de Paz...
          </p>
        </div>
      ) : (
        <div className="casas-grid">
          {filteredCasas.map((casa) => {
            const isHighlighted = highlightedCdpId === String(casa.id);
            const isPaused = !casa.is_active;
            const hasPending = Boolean(casa.sin_reporte_7d && casa.is_active);

            return (
              <article
                key={casa.id}
                className={`casa-card ${isHighlighted ? 'casa-card-highlighted' : ''}`}
                id={`cdp-${casa.id}`}
              >
                <div className="casa-header">
                  <div className="casa-info-top">
                    <div className="casa-icon">
                      <Icon name="home" size={20} />
                    </div>
                    <div>
                      <h4 className="casa-name">Casa "{casa.codigo || casa.nombre}"</h4>
                      <span className="casa-zone">
                        {casa.zona || casa.direccion || 'Sin zona asignada'}
                      </span>
                    </div>
                  </div>
                  <div className="casa-status-wrap">
                    {isPaused ? (
                      <span className="status status-pausada" title="Casa en pausa / inactiva">
                        <span className="status-dot status-inactive-dot" aria-hidden="true" />{' '}
                        PAUSADA
                      </span>
                    ) : hasPending ? (
                      <span
                        className="status status-pendiente"
                        title="Sin reporte en los últimos 7 días"
                      >
                        <Icon name="schedule" size={12} className="inline mr-1" /> SIN REPORTE
                      </span>
                    ) : (
                      <span className="status status-activa" title="Reportó en los últimos 7 días">
                        <span className="status-dot status-active-dot" aria-hidden="true" /> AL DÍA
                      </span>
                    )}
                  </div>
                </div>

                <div className="casa-details">
                  {casa.lider && (
                    <div className="detail-row">
                      <Icon name="verified_user" size={16} />
                      <span>
                        Líder: <strong>{casa.lider}</strong>
                      </span>
                    </div>
                  )}
                  <div className="detail-row">
                    <Icon name="person" size={16} />
                    <span>
                      Anfitrión: <strong>{casa.anfitrion || 'Sin anfitrión'}</strong>
                    </span>
                  </div>
                  {casa.usuario_username ? (
                    <div className="detail-row">
                      <Icon name="verified" size={16} />
                      <span>
                        Usuario: <strong>@{casa.usuario_username}</strong>
                        {casa.usuario_nombre && (
                          <small className="text-subtle"> ({casa.usuario_nombre})</small>
                        )}
                      </span>
                    </div>
                  ) : casa.usuario_nombre ? (
                    <div className="detail-row">
                      <Icon name="verified" size={16} />
                      <span>
                        Usuario: <strong>{casa.usuario_nombre}</strong>
                      </span>
                    </div>
                  ) : null}
                  <div className="detail-row">
                    <Icon name="calendar_today" size={16} />
                    <span>
                      {casa.horario || `${casa.dia_semana || 'Miércoles'} · ${casa.hora || '7:00 PM'}`}
                    </span>
                  </div>
                </div>

                <div className="casa-footer">
                  <div className="attendance">
                    <Icon name="group" size={16} />
                    <span>{casa.asistencia || 0} Asistentes promedio</span>
                  </div>
                  <Link to={`/casa-de-paz/${casa.id}`} className="btn-manage">
                    <span>Gestionar</span>
                    <Icon name="arrow_forward" size={14} />
                  </Link>
                </div>
              </article>
            );
          })}

          {isAdmin &&
            selectedRedId &&
            selectedRedId !== 'all' &&
            filtroEstado !== 'pendientes_7d' &&
            !search && (
              <button
                type="button"
                className="casa-add-card"
                onClick={onOpenNewCdpModal}
              >
                <div className="add-icon">
                  <Icon name="add" size={24} />
                </div>
                <h4>Registrar Nueva Casa</h4>
                <p>Asigna un nuevo anfitrión y vincula la ubicación a esta red.</p>
              </button>
            )}

          {filteredCasas.length === 0 && (
            <div className="empty-state empty-state-casas">
              {filtroEstado === 'pendientes_7d' ? (
                <>
                  <Icon name="check_circle" size={40} className="text-emerald-600 mb-2" />
                  <strong className="text-emerald-700">¡Al día con los reportes!</strong>
                  <span>
                    No hay Casas de Paz activas pendientes de reporte en esta vista.
                  </span>
                  <button
                    type="button"
                    className="btn-banner-filter btn-banner-all mt-3 cursor-pointer"
                    onClick={() => onFiltroEstadoChange('todas')}
                  >
                    <Icon name="restart_alt" size={16} className="mr-1" />
                    <span>Ver todas las casas</span>
                  </button>
                </>
              ) : (
                <>
                  <Icon name="home" size={40} className="text-neutral-400 mb-2" />
                  <strong>Sin Casas de Paz registradas</strong>
                  <span>Esta red todavía no tiene casas vinculadas.</span>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  );
};
