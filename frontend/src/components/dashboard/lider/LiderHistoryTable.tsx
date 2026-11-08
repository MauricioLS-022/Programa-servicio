import React from 'react';
import { Link } from 'react-router-dom';
import { Icon } from '../../ui/Icon';
import { Pagination } from '../../ui/Pagination';
import { LiderEmptyState } from './LiderEmptyState';
import type { LiderReporteItem } from '../../../types/liderDashboard';

export interface LiderHistoryTableProps {
  reportes: LiderReporteItem[];
  totalReportes: number;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onView: (reporte: LiderReporteItem) => void;
  onEdit: (reporte: LiderReporteItem) => void;
  onDelete: (reporte: LiderReporteItem) => void;
}

const formatMoneda = (val?: number) => {
  return Number(val || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

export const LiderHistoryTable: React.FC<LiderHistoryTableProps> = ({
  reportes,
  totalReportes,
  currentPage,
  totalPages,
  onPageChange,
  onView,
  onEdit,
  onDelete,
}) => {
  const hasReportes = reportes && reportes.length > 0;

  return (
    <article className="table-container-card" role="region" aria-labelledby="mis-reportes-title" data-testid="table-container-card">
      <div className="table-top-bar">
        <div>
          <h2 id="mis-reportes-title" className="section-title">
            Últimos Reportes
          </h2>
          <p className="section-subtitle">
            {hasReportes
              ? `Historial de ${reportes.length} reunión(es) registrada(s)`
              : 'No hay reportes registrados aún.'}
          </p>
        </div>
        {hasReportes && (
          <Link to="/generar-reporte" className="btn-new" data-testid="btn-nuevo-reporte-table">
            <Icon name="add_circle" size={16} />
            <span>Nuevo Reporte</span>
          </Link>
        )}
      </div>

      {!hasReportes ? (
        <LiderEmptyState />
      ) : (
        <>
          <div className="table-responsive">
            <table className="lider-table" aria-label="Historial de reportes de Casa de Paz">
              <thead>
                <tr>
                  <th scope="col">Fecha y Hora</th>
                  <th scope="col">Líder Encargado</th>
                  <th scope="col">Tema de la Clase</th>
                  <th scope="col" style={{ textAlign: 'center' }}>
                    Asistencia
                  </th>
                  <th scope="col" style={{ textAlign: 'right' }}>
                    Ofrendas
                  </th>
                  <th scope="col" style={{ textAlign: 'center' }}>
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody>
                {reportes.map((rep) => {
                  const asistenciaTooltip = `Regulares: ${rep.nro_regulares || 0}, Niños: ${rep.nro_niños || 0}, Visitas: ${rep.nro_visitas || 0}, Comprometidos: ${rep.nro_comprometidos || 0}`;
                  const iniciales = rep.iniciales || rep.lider_nombre?.substring(0, 2).toUpperCase() || 'CD';

                  return (
                    <tr key={rep.id} data-testid={`reporte-row-${rep.id}`}>
                      <td>
                        <div className="date-badge">
                          <span className="date-primary">{rep.fecha_formateada || rep.fecha}</span>
                          {rep.hr_inicio && (
                            <span className="time-sub">
                              {rep.hr_inicio}
                              {rep.hr_fin ? ` - ${rep.hr_fin}` : ''}
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="leader-pill">
                          <div className="avatar-mini" aria-hidden="true">
                            {iniciales}
                          </div>
                          <span style={{ fontWeight: 600 }}>{rep.lider_nombre}</span>
                        </div>
                      </td>
                      <td>
                        <div className="tema-cell" title={rep.tema}>
                          {rep.tema}
                        </div>
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <span className="badge-asistencia" title={asistenciaTooltip}>
                          {rep.asistencia}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div
                          style={{
                            display: 'inline-flex',
                            flexDirection: 'column',
                            alignItems: 'flex-end',
                            gap: '2px',
                          }}
                        >
                          <span className="badge-ofrenda">${formatMoneda(rep.ofrendas_usd)}</span>
                          {Boolean(rep.ofrendas_bs && rep.ofrendas_bs > 0) && (
                            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                              Bs. {formatMoneda(rep.ofrendas_bs)}
                            </span>
                          )}
                        </div>
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <div className="action-buttons-group">
                          <button
                            type="button"
                            className="btn-table-action view"
                            onClick={() => onView(rep)}
                            title="Ver detalles completos"
                            aria-label={`Ver detalles del reporte del ${rep.fecha_formateada || rep.fecha}`}
                            data-testid={`btn-view-${rep.id}`}
                          >
                            <Icon name="visibility" size={18} />
                          </button>
                          <button
                            type="button"
                            className="btn-table-action edit"
                            onClick={() => onEdit(rep)}
                            title="Editar este reporte"
                            aria-label={`Editar reporte del ${rep.fecha_formateada || rep.fecha}`}
                            data-testid={`btn-edit-${rep.id}`}
                          >
                            <Icon name="edit" size={18} />
                          </button>
                          <button
                            type="button"
                            className="btn-table-action delete"
                            onClick={() => onDelete(rep)}
                            title="Eliminar este reporte"
                            aria-label={`Eliminar reporte del ${rep.fecha_formateada || rep.fecha}`}
                            data-testid={`btn-delete-${rep.id}`}
                          >
                            <Icon name="delete" size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalReportes}
            itemsPerPage={5}
            onPageChange={onPageChange}
            itemLabel="reportes"
          />
        </>
      )}
    </article>
  );
};
