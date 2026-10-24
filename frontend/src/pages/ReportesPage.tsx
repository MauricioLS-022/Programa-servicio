import React, { useState, useMemo, useEffect } from 'react';
import { useReportes } from '../hooks/useReportes';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { useUrlFilters } from '../hooks/useUrlFilters';
import { useRedes, useCasasDePaz } from '../hooks/useDashboard';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../context/ToastContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Modal } from '../components/ui/Modal';
import { Icon } from '../components/ui/Icon';
import { ReporteModal } from '../components/reportes/ReporteModal';
import type { Reporte } from '../types/reporte';
import '../styles/reportes.css';

export const ReportesPage: React.FC = () => {
  useDocumentTitle('Reportes');

  const { user } = useAuth();
  const { success, error } = useToast();

  const isSupervisor = user?.rol === 'supervisor';
  const isAdmin = user?.rol === 'admin';

  // Configuración de filtros por defecto (Ruta limpia canónica: /reportes)
  const defaultReportesFilters = useMemo(
    () => ({
      q: '',
      red_id: '',
      cdp_id: '',
      fecha_desde: '',
      fecha_hasta: '',
      page: 1,
    }),
    []
  );

  // Sincronización bidireccional con URLSearchParams como Fuente Única de la Verdad (SSOT)
  const { filters, setFilter, setFilters, resetFilters } = useUrlFilters(defaultReportesFilters);
  const search = filters.q;
  const selectedRed = filters.red_id;
  const selectedCdp = filters.cdp_id;
  const fechaDesde = filters.fecha_desde;
  const fechaHasta = filters.fecha_hasta;
  const page = filters.page;

  // Consultar opciones de Red y Casa de Paz
  const { redes } = useRedes();
  const { casas } = useCasasDePaz({ red_id: selectedRed || undefined });

  // Cuando cambia la red, reiniciar la Casa de Paz seleccionada si ya no pertenece a la red
  useEffect(() => {
    if (selectedRed && selectedCdp) {
      const existsInRed = casas.some((c) => String(c.id) === String(selectedCdp));
      if (!existsInRed) {
        setFilter('cdp_id', '');
      }
    }
  }, [selectedRed, selectedCdp, casas, setFilter]);

  // Hook de Reportes con TanStack Query
  const {
    reportes,
    total,
    pages,
    isLoading,
    actualizarReporte,
    isActualizando,
    eliminarReporte,
    isEliminando,
  } = useReportes({
    q: search,
    red_id: selectedRed || undefined,
    cdp_id: selectedCdp || undefined,
    fecha_desde: fechaDesde,
    fecha_hasta: fechaHasta,
    page,
    per_page: 10,
  });

  // Estado para el modal unificado de Reporte (ver detalle / editar)
  const [reporteModalData, setReporteModalData] = useState<{
    reporte: Reporte | null;
    mode: 'view' | 'edit';
  }>({ reporte: null, mode: 'view' });

  // Estado para modal de confirmación de eliminación
  const [reporteEliminar, setReporteEliminar] = useState<Reporte | null>(null);

  // Guardar actualización de reporte
  const handleGuardarReporte = async (id: string, data: Partial<Reporte>) => {
    try {
      const res = await actualizarReporte({ id, data });
      if (res.success) {
        success('¡Reporte ministerial actualizado exitosamente!');
        return res;
      } else {
        error(res.error || 'Error al actualizar el reporte ministerial.');
        throw new Error(res.error);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        error(err.message || 'Error de conexión al actualizar el reporte.');
      } else {
        error('Error inesperado al actualizar el reporte.');
      }
      throw err;
    }
  };

  // Confirmar eliminación
  const handleConfirmDelete = async () => {
    if (!reporteEliminar) return;
    try {
      const res = await eliminarReporte({
        id: reporteEliminar.id,
        cdp_id: reporteEliminar.cdp_id,
      });
      if (res.success) {
        success('Reporte ministerial eliminado correctamente');
        setReporteEliminar(null);
      } else {
        error(res.error || 'No se pudo eliminar el reporte.');
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        error(err.message || 'Error al eliminar el reporte');
      } else {
        error('Error al eliminar el reporte');
      }
    }
  };

  // Limpiar todos los filtros (vuelve a URL canónica limpia /reportes)
  const handleResetFiltros = () => {
    resetFilters();
  };

  // Ventana deslizante de paginación (Sliding Window ±2)
  const paginationRange = useMemo(() => {
    const delta = 2;
    const range: number[] = [];
    for (let i = Math.max(1, page - delta); i <= Math.min(pages, page + delta); i++) {
      range.push(i);
    }
    return range;
  }, [page, pages]);

  return (
    <div className="reportes-page-container">
      {/* Hero Card - Paridad 1 a 1 reportes_admin.html (Sin botón de carga de reporte) */}
      <div className="hero-card">
        <h1 className="hero-title">
          {isSupervisor
            ? 'Reportes de mi Red'
            : isAdmin
            ? 'Reportes de Administración'
            : 'Historial de Reportes'}
        </h1>
        <p className="hero-subtitle">
          {isSupervisor
            ? 'Auditoría y seguimiento de actividad ministerial'
            : 'Gestión y análisis de actividad ministerial'}
        </p>
      </div>

      {/* Sección de Filtros Dinámicos */}
      <div className="filter-section">
        <div className="filter-grid">
          {/* Búsqueda */}
          <Input
            label="Buscar"
            placeholder="Buscar por líder, casa de paz o tema..."
            icon={<Icon name="search" size={18} />}
            value={search}
            onChange={(e) => {
              setFilters({ q: e.target.value, page: 1 });
            }}
          />

          {/* Selector de Red (Oculto para supervisor) */}
          {!isSupervisor && (
            <Select
              label="Red Ministerial"
              value={selectedRed}
              onChange={(e) => {
                setFilters({ red_id: e.target.value, cdp_id: '', page: 1 });
              }}
              options={[
                { value: '', label: 'Todas las redes' },
                ...redes.map((r) => ({ value: String(r.id), label: r.nombre })),
              ]}
            />
          )}

          {/* Selector de Casa de Paz */}
          <Select
            label="Casa de Paz"
            value={selectedCdp}
            onChange={(e) => {
              setFilters({ cdp_id: e.target.value, page: 1 });
            }}
            options={[
              { value: '', label: 'Todas las casas' },
              ...casas.map((c) => ({
                value: String(c.id),
                label: `${c.codigo}${c.nombre || c.anfitrion ? ` · ${c.nombre || c.anfitrion}` : ''}`,
              })),
            ]}
          />

          {/* Rango de Fechas */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-text-main dark:text-[#f8deda]">
              Rango de Fecha
            </label>
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={fechaDesde}
                onChange={(e) => {
                  setFilters({ fecha_desde: e.target.value, page: 1 });
                }}
                className="w-full rounded-lg border border-border-subtle dark:border-[rgba(221,192,189,0.25)] bg-white dark:bg-[#150f10] text-xs py-2 px-2.5 outline-none focus:ring-2 focus:ring-[#700204]/30 focus:border-[#700204] dark:focus:border-[#f8deda]"
                title="Fecha desde"
                aria-label="Fecha desde"
              />
              <span className="text-text-muted dark:text-[#d4c2bf] text-xs font-bold">–</span>
              <input
                type="date"
                value={fechaHasta}
                onChange={(e) => {
                  setFilters({ fecha_hasta: e.target.value, page: 1 });
                }}
                className="w-full rounded-lg border border-border-subtle dark:border-[rgba(221,192,189,0.25)] bg-white dark:bg-[#150f10] text-xs py-2 px-2.5 outline-none focus:ring-2 focus:ring-[#700204]/30 focus:border-[#700204] dark:focus:border-[#f8deda]"
                title="Fecha hasta"
                aria-label="Fecha hasta"
              />
            </div>
          </div>

          {/* Botón Reset Filtros */}
          {(search || selectedRed || selectedCdp || fechaDesde || fechaHasta) && (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleResetFiltros}
              title="Restablecer todos los filtros"
              className="h-10"
            >
              <Icon name="close" size={16} />
              <span>Limpiar</span>
            </Button>
          )}
        </div>
      </div>

      {/* Tabla de Reportes */}
      <section className="table-wrapper">
        <div className="table-header">
          <h2>Reportes de Actividad</h2>
          <span className="text-xs font-semibold text-white/85">
            {total} {total === 1 ? 'registro' : 'registros'}
          </span>
        </div>

        {isLoading ? (
          <div className="py-20 flex flex-col items-center justify-center gap-3">
            <Icon name="schedule" size={32} className="animate-spin text-vino dark:text-vino-light" />
            <p className="text-sm font-medium text-text-muted dark:text-[#d4c2bf]">
              Consultando reportes ministeriales...
            </p>
          </div>
        ) : reportes.length === 0 ? (
          <div className="py-16 text-center text-text-muted dark:text-[#d4c2bf] text-sm flex flex-col items-center gap-2">
            <Icon name="analytics" size={36} className="opacity-40" />
            <p>No se encontraron reportes con los filtros seleccionados.</p>
            {(search || selectedRed || selectedCdp || fechaDesde || fechaHasta) && (
              <button
                type="button"
                onClick={handleResetFiltros}
                className="text-xs text-vino dark:text-vino-light hover:underline font-semibold cursor-pointer"
              >
                Limpiar filtros de búsqueda
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto scroll-containment">
            <table className="w-full text-left text-xs" aria-label="Historial de reportes de actividad ministerial">
              <thead>
                <tr>
                  <th scope="col" className="py-3 px-4">Fecha</th>
                  <th scope="col" className="py-3 px-4">Líder</th>
                  <th scope="col" className="py-3 px-4">Casa de Paz</th>
                  <th scope="col" className="py-3 px-4">Tema</th>
                  <th scope="col" className="py-3 px-4 text-center">Asistencia</th>
                  <th scope="col" className="py-3 px-4 text-right">Ofrendas</th>
                  <th scope="col" className="py-3 px-4 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle/50 dark:divide-[rgba(221,192,189,0.15)]">
                {reportes.map((rep) => (
                  <tr
                    key={rep.id}
                    className="hover:bg-surface-low/50 dark:hover:bg-[#2f2225] transition-colors"
                  >
                    {/* Fecha */}
                    <td className="py-3.5 px-4 font-bold text-text-main dark:text-[#f8f2f0] whitespace-nowrap">
                      {rep.fecha_formateada || rep.fecha}
                    </td>

                    {/* Líder */}
                    <td className="py-3.5 px-4">
                      <div className="leader-cell">
                        <div className="avatar" aria-hidden="true">
                          {rep.iniciales || (rep.lider_nombre ? rep.lider_nombre.substring(0, 2).toUpperCase() : 'CD')}
                        </div>
                        <span className="font-semibold text-text-main dark:text-[#f8f2f0]">
                          {rep.lider_nombre || 'Sin líder asignado'}
                        </span>
                      </div>
                    </td>

                    {/* Casa de Paz */}
                    <td className="py-3.5 px-4">
                      <div className="font-medium text-text-main dark:text-[#f8f2f0]">
                        {rep.cdp_codigo || `CDP #${rep.cdp_id}`}
                        {rep.cdp_nombre && (
                          <span className="text-text-muted dark:text-[#d4c2bf] font-normal ml-1">
                            · {rep.cdp_nombre}
                          </span>
                        )}
                      </div>
                      {rep.red_nombre && (
                        <span className="block text-[11px] text-text-muted dark:text-[#d4c2bf] italic">
                          {rep.red_nombre}
                        </span>
                      )}
                    </td>

                    {/* Tema */}
                    <td className="py-3.5 px-4 max-w-[200px] truncate text-text-main dark:text-[#d4c2bf]" title={rep.tema}>
                      {rep.tema || <span className="text-text-muted dark:text-[#d4c2bf]/60 italic">Sin tema</span>}
                    </td>

                    {/* Asistencia */}
                    <td className="py-3.5 px-4 text-center">
                      <span className="badge">
                        {rep.asistencia}
                      </span>
                    </td>

                    {/* Ofrendas Duales */}
                    <td className="py-3.5 px-4 text-right">
                      <div className="inline-flex flex-col items-end gap-0.5">
                        <span className="font-bold text-primary dark:text-[#f3d07a]">
                          ${Number(rep.ofrendas_usd || 0).toFixed(2)}
                        </span>
                        {rep.ofrendas_bs !== undefined && rep.ofrendas_bs > 0 && (
                          <span className="text-[11px] text-text-muted dark:text-[#d4c2bf] font-medium">
                            Bs. {Number(rep.ofrendas_bs).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Acciones */}
                    <td className="py-3.5 px-4 text-center">
                      <div className="inline-flex items-center justify-center gap-1">
                        {/* Botón Ver Detalle */}
                        <button
                          type="button"
                          className="btn-icon btn-view cursor-pointer"
                          onClick={() => setReporteModalData({ reporte: rep, mode: 'view' })}
                          title={`Ver detalle del reporte de ${rep.lider_nombre}`}
                          aria-label={`Ver detalle del reporte de ${rep.lider_nombre}`}
                        >
                          <Icon name="visibility" size={18} className="text-primary dark:text-[#f8deda]" />
                        </button>

                        {/* Botón Editar (Solo admin y líder de CDP) */}
                        {!isSupervisor && (
                          <button
                            type="button"
                            className="btn-icon btn-edit cursor-pointer"
                            onClick={() => setReporteModalData({ reporte: rep, mode: 'edit' })}
                            title={`Editar reporte de ${rep.lider_nombre}`}
                            aria-label={`Editar reporte de ${rep.lider_nombre}`}
                          >
                            <Icon name="edit" size={18} className="text-[#735c00] dark:text-[#dbe786]" />
                          </button>
                        )}

                        {/* Botón Eliminar (Solo admin) */}
                        {isAdmin && (
                          <button
                            type="button"
                            className="btn-icon btn-delete cursor-pointer"
                            onClick={() => setReporteEliminar(rep)}
                            title={`Eliminar reporte de ${rep.lider_nombre}`}
                            aria-label={`Eliminar reporte de ${rep.lider_nombre}`}
                          >
                            <Icon name="delete" size={18} className="text-red-600 dark:text-[#ffb4ab]" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Paginación Deslizante */}
        {pages > 1 && (
          <div className="p-4 border-t border-border-subtle/80 dark:border-[rgba(221,192,189,0.2)] bg-surface-low/30 dark:bg-[#1f1618] flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
            <span className="text-text-muted dark:text-[#d4c2bf]">
              Mostrando página <strong>{page}</strong> de <strong>{pages}</strong> ({total} registros totales)
            </span>

            <div className="inline-flex items-center gap-1">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setFilter('page', Math.max(1, page - 1))}
                disabled={page === 1}
                aria-label="Página anterior"
              >
                <Icon name="chevron_left" size={16} />
              </Button>

              {paginationRange[0] > 1 && (
                <>
                  <Button
                    variant={page === 1 ? 'primary' : 'secondary'}
                    size="sm"
                    onClick={() => setFilter('page', 1)}
                  >
                    1
                  </Button>
                  {paginationRange[0] > 2 && <span className="px-1 text-text-muted">...</span>}
                </>
              )}

              {paginationRange.map((pNum) => (
                <Button
                  key={pNum}
                  variant={page === pNum ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setFilter('page', pNum)}
                  aria-current={page === pNum ? 'page' : undefined}
                >
                  {pNum}
                </Button>
              ))}

              {paginationRange[paginationRange.length - 1] < pages && (
                <>
                  {paginationRange[paginationRange.length - 1] < pages - 1 && (
                    <span className="px-1 text-text-muted">...</span>
                  )}
                  <Button
                    variant={page === pages ? 'primary' : 'secondary'}
                    size="sm"
                    onClick={() => setFilter('page', pages)}
                  >
                    {pages}
                  </Button>
                </>
              )}

              <Button
                variant="secondary"
                size="sm"
                onClick={() => setFilter('page', Math.min(pages, page + 1))}
                disabled={page === pages}
                aria-label="Página siguiente"
              >
                <Icon name="chevron_right" size={16} />
              </Button>
            </div>
          </div>
        )}
      </section>

      {/* ==================================================================
          MODAL REUTILIZABLE: DETALLE Y EDICIÓN DE REPORTE CON PARIDAD JINJA2
          ================================================================== */}
      <ReporteModal
        isOpen={!!reporteModalData.reporte}
        onClose={() => setReporteModalData({ reporte: null, mode: 'view' })}
        reporte={reporteModalData.reporte}
        initialMode={reporteModalData.mode}
        canEdit={!isSupervisor}
        onGuardar={handleGuardarReporte}
        isGuardando={isActualizando}
      />

      {/* ==================================================================
          MODAL DEFENSIVO: CONFIRMAR ELIMINACIÓN DE REPORTE
          ================================================================== */}
      <Modal
        isOpen={!!reporteEliminar}
        onClose={() => setReporteEliminar(null)}
        title="Confirmar Eliminación"
        description="Esta acción eliminará de forma irreversible el reporte seleccionado."
        maxWidth="md"
        headerIcon={<Icon name="delete" size={20} className="text-red-600 dark:text-red-400" />}
        footer={
          <div className="flex items-center justify-end gap-2.5 w-full">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setReporteEliminar(null)}
              disabled={isEliminando}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              variant="danger"
              icon={<Icon name="delete" size={16} />}
              onClick={handleConfirmDelete}
              disabled={isEliminando}
              isLoading={isEliminando}
            >
              Sí, eliminar
            </Button>
          </div>
        }
      >
        {reporteEliminar && (
          <div className="py-2 text-sm text-text-main dark:text-[#f8f2f0]">
            <p className="mb-3">
              ¿Estás seguro de que deseas eliminar este reporte?
            </p>
            <div className="p-3.5 rounded-xl bg-surface dark:bg-[#150f10] border border-border-subtle dark:border-[rgba(221,192,189,0.2)] flex flex-col gap-1 text-xs">
              <div>
                <span className="font-bold text-text-muted dark:text-[#d4c2bf]">Fecha:</span>{' '}
                <span className="font-semibold text-text-main dark:text-[#f8f2f0]">{reporteEliminar.fecha_formateada || reporteEliminar.fecha}</span>
              </div>
              <div>
                <span className="font-bold text-text-muted dark:text-[#d4c2bf]">Líder:</span>{' '}
                <span className="font-semibold text-text-main dark:text-[#f8f2f0]">{reporteEliminar.lider_nombre}</span>
              </div>
              <div>
                <span className="font-bold text-text-muted dark:text-[#d4c2bf]">Casa de Paz:</span>{' '}
                <span className="font-semibold text-text-main dark:text-[#f8f2f0]">{reporteEliminar.cdp_codigo} · {reporteEliminar.cdp_nombre}</span>
              </div>
              <div>
                <span className="font-bold text-text-muted dark:text-[#d4c2bf]">Tema:</span>{' '}
                <span className="font-semibold text-text-main dark:text-[#f8f2f0]">{reporteEliminar.tema || 'Sin tema'}</span>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
