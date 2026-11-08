import React, { useState } from 'react';
import { useAuth } from '../../../hooks/useAuth';
import { useLiderDashboard } from '../../../hooks/useLiderDashboard';
import { LiderDashboardHeader } from './LiderDashboardHeader';
import { LiderSummaryCards } from './LiderSummaryCards';
import { LiderHistoryTable } from './LiderHistoryTable';
import { LiderSidebar } from './LiderSidebar';
import { LiderDetalleModal } from './LiderDetalleModal';
import { LiderEditarModal } from './LiderEditarModal';
import { LiderEliminarModal } from './LiderEliminarModal';
import { Icon } from '../../ui/Icon';
import { Button } from '../../ui/Button';
import type { LiderReporteItem } from '../../../types/liderDashboard';
import '../../../styles/shared-tables.css';
import '../../../styles/lider_dashboard.css';

export const LiderDashboardView: React.FC = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);

  const {
    cdp,
    lideres,
    metricas,
    reportes,
    total_reportes,
    currentPage,
    totalPages,
    tieneCdp,
    isLoading,
    isError,
    error,
    refetch,
  } = useLiderDashboard({ page, per_page: 5 });

  const [selectedReporte, setSelectedReporte] = useState<LiderReporteItem | null>(null);
  const [isViewOpen, setIsViewOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  const handleOpenView = (rep: LiderReporteItem) => {
    setSelectedReporte(rep);
    setIsViewOpen(true);
  };

  const handleOpenEdit = (rep: LiderReporteItem) => {
    setSelectedReporte(rep);
    setIsEditOpen(true);
  };

  const handleOpenDelete = (rep: LiderReporteItem) => {
    setSelectedReporte(rep);
    setIsDeleteOpen(true);
  };

  const handleCloseView = () => {
    setIsViewOpen(false);
  };

  const handleCloseEdit = () => {
    setIsEditOpen(false);
  };

  const handleCloseDelete = () => {
    setIsDeleteOpen(false);
  };

  const handleMutationSuccess = () => {
    refetch();
  };

  if (isLoading && !metricas) {
    return (
      <div className="lider-dashboard-wrapper">
        <div
          data-testid="lider-dashboard-loading"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '5rem 1rem',
            gap: '1rem',
          }}
        >
          <Icon name="progress_activity" size={44} className="icon-spin text-vino" />
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Cargando panel de Casa de Paz...
          </p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="lider-dashboard-wrapper">
        <div
          data-testid="lider-dashboard-error"
          style={{
            background: 'var(--danger-bg, #fee2e2)',
            border: '1px solid var(--danger-color, #b32626)',
            borderRadius: '12px',
            padding: '2rem',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1rem',
          }}
        >
          <Icon name="warning" size={40} className="text-red-600" />
          <div>
            <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--danger-color, #b32626)' }}>
              No se pudo cargar la información del panel
            </h3>
            <p style={{ margin: 0, color: 'var(--text-main)', fontSize: '0.9rem' }}>
              {error instanceof Error ? error.message : 'Error al conectar con el servidor.'}
            </p>
          </div>
          <Button variant="secondary" onClick={() => refetch()} icon={<Icon name="refresh" size={16} />}>
            Reintentar
          </Button>
        </div>
      </div>
    );
  }

  const nombreUsuario = user?.nombre || user?.username || 'Líder';

  return (
    <div className="lider-dashboard-wrapper" data-testid="lider-dashboard-view">
      <LiderDashboardHeader usuario={nombreUsuario} cdp={cdp} />

      {!tieneCdp ? (
        <div
          className="table-container-card"
          data-testid="lider-sin-cdp"
          style={{ textAlign: 'center', padding: '3rem 1.5rem' }}
        >
          <div className="empty-icon-wrapper" style={{ margin: '0 auto 1.25rem auto' }}>
            <Icon name="warning" size={36} />
          </div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--primary)' }}>
            Sin Casa de Paz Asignada
          </h3>
          <p style={{ color: 'var(--text-muted)', maxWidth: '420px', margin: '0 auto' }}>
            Aún no tienes una Casa de Paz asignada a tu usuario. Comunícate con tu supervisor
            ministerial para la asignación correspondiente.
          </p>
        </div>
      ) : (
        <>
          <LiderSummaryCards metricas={metricas} />

          <section className="bottom-dashboard-grid">
            <LiderHistoryTable
              reportes={reportes}
              totalReportes={total_reportes}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={(newPage) => setPage(newPage)}
              onView={handleOpenView}
              onEdit={handleOpenEdit}
              onDelete={handleOpenDelete}
            />

            <LiderSidebar
              diasCierreTexto={metricas?.dias_cierre_texto}
              lideres={lideres}
            />
          </section>
        </>
      )}

      {/* Modales */}
      <LiderDetalleModal
        isOpen={isViewOpen}
        onClose={handleCloseView}
        reporte={selectedReporte}
      />

      <LiderEditarModal
        isOpen={isEditOpen}
        onClose={handleCloseEdit}
        reporte={selectedReporte}
        lideres={lideres}
        onSuccess={handleMutationSuccess}
      />

      <LiderEliminarModal
        isOpen={isDeleteOpen}
        onClose={handleCloseDelete}
        reporte={selectedReporte}
        onSuccess={handleMutationSuccess}
      />
    </div>
  );
};
