import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { useEstructuraController } from '../hooks/useEstructuraController';
import { useToast } from '../context/ToastContext';
import { downloadExport } from '../utils/downloadExport';
import { RedModal } from '../components/estructura/RedModal';
import { CasaDePazModal } from '../components/estructura/CasaDePazModal';
import { RedBottomSheet } from '../components/estructura/RedBottomSheet';
import { RedesSidebar } from '../components/estructura/RedesSidebar';
import { CasasGridSection } from '../components/estructura/CasasGridSection';
import { Icon } from '../components/ui/Icon';
import '../styles/estructura.css';

export const EstructuraPage: React.FC = () => {
  useDocumentTitle('Estructura');
  const { success, error: toastError } = useToast();
  const [exportingFormat, setExportingFormat] = useState<'xlsx' | 'csv' | null>(null);

  const {
    isAdmin,
    isSupervisor,
    redes,
    casas,
    filteredCasas,
    isLoading,
    selectores,
    selectedRedId,
    effectiveRedId,
    selectedRedObj,
    selectedRedName,
    filtroEstado,
    search,
    highlightedCdpId,
    totalCasasCongregacion,
    totalPendientesCongregacion,
    pendingInScope,
    redModalData,
    setRedModalData,
    cdpModalData,
    setCdpModalData,
    isCreandoRed,
    isEditandoRed,
    isEliminandoRed,
    isCreandoCdp,
    isEditandoCdp,
    isEliminandoCdp,
    activeMenuRedId,
    activeMenuRed,
    menuPos,
    closeContextMenu,
    handleToggleContextMenu,
    isMobileSheetOpen,
    setIsMobileSheetOpen,
    showToast,
    dismissToast,
    sidebarRef,
    isTouchDevice,
    canScrollLeft,
    canScrollRight,
    handleScrollSidebar,
    handleSelectRed,
    handleFiltroEstadoChange,
    handleSearchChange,
    handleGuardarRed,
    handleToggleRed,
    handleEliminarRed,
    handleGuardarCdp,
    handleEliminarCdp,
  } = useEstructuraController();

  const handleExportCasas = async (format: 'xlsx' | 'csv') => {
    setExportingFormat(format);
    try {
      await downloadExport({
        resource: 'casas_de_paz',
        format,
        params: {
          red_id: effectiveRedId && effectiveRedId !== 'all' ? effectiveRedId : undefined,
          q: search || undefined,
          filtro: filtroEstado !== 'todas' ? filtroEstado : undefined,
        },
      });
      success(`Directorio de Casas de Paz exportado en formato ${format.toUpperCase()}.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al exportar Casas de Paz.';
      toastError(msg);
    } finally {
      setExportingFormat(null);
    }
  };

  return (
    <main className={`estructura-main ${isSupervisor ? 'supervisor-mode' : ''}`}>
      {/* Header Canónico */}
      <header className="page-header">
        <div className="header-text">
          {isSupervisor ? (
            <>
              <h1 className="title">Estructura de mi Red</h1>
              <p className="subtitle">
                Supervisa el estado de tus <span className="highlight">Casas de Paz</span> y monitorea el crecimiento espiritual de cada grupo bajo tu responsabilidad.
              </p>
            </>
          ) : (
            <>
              <h1 className="title">Estructura Organizacional</h1>
              <p className="subtitle">
                Gestiona la arquitectura de tu comunidad a través de <span className="highlight">Redes</span> y <span className="highlight">Casas de Paz</span>. Define jerarquías y supervisa el crecimiento espiritual de cada grupo.
              </p>
            </>
          )}
        </div>

        {!isSupervisor && (
          <div className="header-actions">
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => setRedModalData({ isOpen: true, red: null })}
            >
              <Icon name="hub" size={18} className="mr-1.5 shrink-0" />
              Nueva Red
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setCdpModalData({ isOpen: true, casa: null })}
            >
              <Icon name="add_home" size={18} className="mr-1.5 shrink-0" />
              Nueva Casa de Paz
            </button>
          </div>
        )}
      </header>

      {/* Grid Principal: 2 columnas en Desktop, barra de chips en móvil */}
      <div className="estructura-grid">
        <RedesSidebar
          isSupervisor={isSupervisor}
          redes={redes}
          casas={casas}
          selectedRedId={selectedRedId}
          effectiveRedId={effectiveRedId}
          totalCasasCongregacion={totalCasasCongregacion}
          totalPendientesCongregacion={totalPendientesCongregacion}
          activeMenuRedId={activeMenuRedId}
          sidebarRef={sidebarRef}
          isTouchDevice={isTouchDevice}
          canScrollLeft={canScrollLeft}
          canScrollRight={canScrollRight}
          onScrollSidebar={handleScrollSidebar}
          onSelectRed={handleSelectRed}
          onToggleContextMenu={handleToggleContextMenu}
        />

        <CasasGridSection
          isAdmin={isAdmin}
          isSupervisor={isSupervisor}
          isLoading={isLoading}
          selectedRedId={selectedRedId}
          effectiveRedId={effectiveRedId}
          selectedRedObj={selectedRedObj}
          selectedRedName={selectedRedName}
          filtroEstado={filtroEstado}
          search={search}
          filteredCasas={filteredCasas}
          highlightedCdpId={highlightedCdpId}
          pendingInScope={pendingInScope}
          onSearchChange={handleSearchChange}
          onFiltroEstadoChange={handleFiltroEstadoChange}
          onOpenMobileSheet={() => setIsMobileSheetOpen(true)}
          onOpenNewCdpModal={() => setCdpModalData({ isOpen: true, casa: null })}
          onExportCasas={handleExportCasas}
          exportingFormat={exportingFormat}
        />
      </div>

      {/* Toast Flotante de Cumplimiento Semanal */}
      {showToast && totalPendientesCongregacion > 0 && (
        <div className="toast-estructura is-visible" role="alert">
          <div className="toast-content">
            <div className="toast-icon">
              <Icon name="notification_important" size={20} className="text-amber-600 dark:text-amber-400" />
            </div>
            <div className="toast-texts">
              <strong>Cumplimiento Semanal</strong>
              <span>
                {totalPendientesCongregacion} Casa
                {totalPendientesCongregacion > 1 ? 's' : ''} de Paz activa
                {totalPendientesCongregacion > 1 ? 's' : ''} sin reporte en los últimos 7 días.
              </span>
            </div>
          </div>
          <div className="toast-actions">
            <button
              type="button"
              className="toast-btn-action"
              onClick={() => {
                dismissToast();
                handleFiltroEstadoChange('pendientes_7d');
                const sec = document.querySelector('.casas-section');
                if (sec) sec.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Ver
            </button>
            <button
              type="button"
              className="toast-btn-close"
              aria-label="Cerrar notificación"
              onClick={dismissToast}
            >
              <Icon name="close" size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Modal CRUD de Red */}
      {redModalData.isOpen && (
        <RedModal
          isOpen={redModalData.isOpen}
          onClose={() => setRedModalData({ isOpen: false, red: null })}
          red={redModalData.red}
          supervisores={selectores?.supervisores || []}
          onSave={handleGuardarRed}
          onDelete={handleEliminarRed}
          isSaving={isCreandoRed || isEditandoRed}
          isDeleting={isEliminandoRed}
        />
      )}

      {/* Modal CRUD de Casa de Paz */}
      {cdpModalData.isOpen && (
        <CasaDePazModal
          isOpen={cdpModalData.isOpen}
          onClose={() => setCdpModalData({ isOpen: false, casa: null })}
          casa={cdpModalData.casa}
          redes={redes}
          lideresDisponibles={selectores?.lideres_cdp || []}
          defaultRedId={selectedRedId && selectedRedId !== 'all' ? selectedRedId : undefined}
          onSave={handleGuardarCdp}
          onDelete={handleEliminarCdp}
          isSaving={isCreandoCdp || isEditandoCdp}
          isDeleting={isEliminandoCdp}
        />
      )}

      {/* Portal del Menú Contextual de Red para Desktop */}
      {activeMenuRed && menuPos && createPortal(
        <div
          className="red-menu is-open"
          role="menu"
          style={{
            position: 'fixed',
            top: `${menuPos.top}px`,
            right: `${menuPos.right}px`,
            zIndex: 99999,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              const target = activeMenuRed;
              closeContextMenu();
              setRedModalData({ isOpen: true, red: target });
            }}
          >
            <Icon name="edit" size={14} />
            <span>Editar red</span>
          </button>
          <button
            type="button"
            role="menuitem"
            className={activeMenuRed.is_active ? 'menu-danger' : 'menu-success'}
            onClick={() => {
              const targetId = activeMenuRed.id;
              closeContextMenu();
              handleToggleRed(targetId);
            }}
          >
            {activeMenuRed.is_active ? (
              <>
                <Icon name="pause_circle" size={14} />
                <span>Poner en pausa</span>
              </>
            ) : (
              <>
                <Icon name="play_circle" size={14} />
                <span>Reactivar red</span>
              </>
            )}
          </button>
          {isAdmin && (
            <button
              type="button"
              role="menuitem"
              className="menu-danger"
              onClick={() => {
                const targetId = activeMenuRed.id;
                closeContextMenu();
                handleEliminarRed(targetId);
              }}
            >
              <Icon name="delete" size={14} />
              <span>Eliminar red</span>
            </button>
          )}
        </div>,
        document.body
      )}

      {/* Bottom Sheet de Opciones de Red para Móvil */}
      <RedBottomSheet
        isOpen={isMobileSheetOpen}
        onClose={() => setIsMobileSheetOpen(false)}
        red={selectedRedObj}
        isAdmin={isAdmin}
        onEdit={(red) => setRedModalData({ isOpen: true, red })}
        onToggle={handleToggleRed}
        onDelete={handleEliminarRed}
      />
    </main>
  );
};
