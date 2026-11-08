import React, { useState, useMemo, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { usePerfil } from '../hooks/usePerfil';
import { useLideres, useLiderMutations } from '../hooks/useLideres';
import { useEstructuraSelectores } from '../hooks/useEstructura';
import { useToast } from '../context/ToastContext';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { LiderFormModal } from '../components/lideres/LiderFormModal';
import { DeleteLiderModal } from '../components/lideres/DeleteLiderModal';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Icon } from '../components/ui/Icon';
import { Pagination } from '../components/ui/Pagination';
import type { Lider, LiderInput } from '../types/estructura';
import '../styles/shared-tables.css';
import '../styles/lideres.css';

const ITEMS_PER_PAGE = 5;

export const LideresPage: React.FC = () => {
  useDocumentTitle('Directorio de Liderazgo - Vino Nuevo');
  const { user: currentUser } = useAuth();
  const { perfil } = usePerfil();
  const { success, error: toastError, info } = useToast();

  const isSupervisor = currentUser?.rol === 'supervisor';
  const isAdmin = currentUser?.rol === 'admin';
  const supervisorRedId = isSupervisor ? perfil?.red_id : null;

  // Selectores para filtros y asignación
  const { redes, casasDePaz } = useEstructuraSelectores();

  // Filtros client-side y reactivos
  const [searchQuery, setSearchQuery] = useState('');
  const [rolFiltro, setRolFiltro] = useState('');
  const [cdpFiltro, setCdpFiltro] = useState('');
  const [redFiltro, setRedFiltro] = useState<string>('');
  const [page, setPage] = useState(1);

  // Efectiva red a filtrar: si es supervisor, forzada a su red
  const effectiveRedId = isSupervisor && supervisorRedId ? String(supervisorRedId) : redFiltro;

  const { lideres, isLoading, isError, error, refetch } = useLideres({
    red_id: effectiveRedId || undefined,
    cdp_id: cdpFiltro || undefined,
    rol: rolFiltro || undefined,
  });

  const {
    crearLider,
    isCreando,
    editarLider,
    isEditando,
    toggleLider,
    eliminarLider,
    isEliminando,
  } = useLiderMutations();

  // Modales
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedLider, setSelectedLider] = useState<Lider | null>(null);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [liderToDelete, setLiderToDelete] = useState<Lider | null>(null);

  // Reset de página al cambiar filtros
  useEffect(() => {
    setPage(1);
  }, [searchQuery, rolFiltro, cdpFiltro, effectiveRedId]);

  // Casas de Paz disponibles filtradas según aislamiento territorial de supervisor
  const casasDisponibles = useMemo(() => {
    if (!casasDePaz) return [];
    if (isSupervisor && supervisorRedId) {
      return casasDePaz.filter((c) => String((c as any).red_id) === String(supervisorRedId));
    }
    if (effectiveRedId) {
      return casasDePaz.filter((c) => String((c as any).red_id) === String(effectiveRedId));
    }
    return casasDePaz;
  }, [casasDePaz, isSupervisor, supervisorRedId, effectiveRedId]);

  // Live Search Client-Side instantáneo (Requerimiento #25)
  const filteredLideres = useMemo(() => {
    return lideres.filter((l) => {
      const q = searchQuery.toLowerCase().trim();
      const cleanDigits = q.replace(/[^0-9]/g, '');
      const matchPhone =
        cleanDigits.length > 0 && l.telefono
          ? l.telefono.replace(/[^0-9]/g, '').includes(cleanDigits)
          : false;

      const matchSearch =
        !q ||
        (l.nombre && l.nombre.toLowerCase().includes(q)) ||
        (l.apellido && l.apellido.toLowerCase().includes(q)) ||
        matchPhone;

      const matchRol = !rolFiltro || (l.rol && l.rol.toLowerCase() === rolFiltro.toLowerCase());
      const matchCdp = !cdpFiltro || String(l.cdp_id) === String(cdpFiltro);
      const matchRed = !effectiveRedId || String(l.red_id) === String(effectiveRedId);

      return matchSearch && matchRol && matchCdp && matchRed;
    });
  }, [lideres, searchQuery, rolFiltro, cdpFiltro, effectiveRedId]);

  // Paginación de 5 resultados por página
  const totalPages = Math.max(1, Math.ceil(filteredLideres.length / ITEMS_PER_PAGE));
  const paginatedLideres = useMemo(() => {
    const start = (page - 1) * ITEMS_PER_PAGE;
    return filteredLideres.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredLideres, page]);

  // Handlers
  const handleOpenCreate = () => {
    setSelectedLider(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (lider: Lider) => {
    setSelectedLider(lider);
    setIsModalOpen(true);
  };

  const handleOpenDelete = (lider: Lider) => {
    setLiderToDelete(lider);
    setIsDeleteModalOpen(true);
  };

  const handleSaveLider = async (data: LiderInput) => {
    if (selectedLider) {
      await editarLider({ id: selectedLider.id, data });
      success('Líder actualizado correctamente.');
    } else {
      await crearLider(data);
      success('Líder registrado correctamente.');
    }
  };

  const handleToggleLider = async (l: Lider) => {
    try {
      const res = await toggleLider(l.id);
      success(res.message || 'Estado del líder actualizado.');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al cambiar estado del líder.';
      toastError(msg);
    }
  };

  const handleConfirmDelete = async (liderId: number) => {
    try {
      const res = await eliminarLider(liderId);
      success(res.message || 'Líder eliminado del sistema.');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al eliminar el líder.';
      toastError(msg);
      throw err;
    }
  };

  const handleExportCSV = () => {
    if (!filteredLideres.length) {
      info('No hay líderes para exportar.');
      return;
    }
    const headers = ['ID', 'Nombre', 'Apellido', 'Rol', 'Red', 'Casa de Paz', 'Teléfono', 'Estado'];
    const rows = filteredLideres.map((l) => [
      l.id,
      `"${l.nombre || ''}"`,
      `"${l.apellido || ''}"`,
      `"${l.rol || ''}"`,
      `"${l.red_nombre || ''}"`,
      `"${l.cdp_codigo || ''}"`,
      `"${l.telefono || ''}"`,
      l.is_active ? 'Activo' : 'Inactivo',
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `directorio_lideres_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="lideres-page-wrapper">
      {/* Header */}
      <header className="page-header">
        <div className="header-text">
          <p className="subtitle">Gestión de líderes</p>
          <h1 className="title">Directorio de Liderazgo</h1>
          <p className="description">
            Consulta rápida de información de contacto de líderes y sublíderes en la red de Casas de Paz.
          </p>
        </div>
        {isAdmin && (
          <div>
            <Button
              variant="primary"
              onClick={handleOpenCreate}
              icon={<Icon name="person_add" size={16} />}
            >
              Agregar Líder
            </Button>
          </div>
        )}
      </header>

      {/* Circuit Breaker / Error State */}
      {isError && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-sm text-red-800 dark:text-red-200 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Icon name="warning" size={20} className="text-red-600 dark:text-red-400 shrink-0" />
            <span>
              {error instanceof Error
                ? error.message
                : 'Error al consultar el directorio de líderes. El servidor puede estar operando en modo degradado.'}
            </span>
          </div>
          <Button variant="secondary" size="sm" onClick={() => refetch()} icon={<Icon name="refresh" size={16} />}>
            Reintentar
          </Button>
        </div>
      )}

      {/* Barra de Filtros y Live Search */}
      <section className="filter-card">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Live Search */}
          <div>
            <label htmlFor="ldr-search" className="block text-xs font-semibold text-text-muted dark:text-[#d4c2bf] mb-1">
              Buscar
            </label>
            <Input
              id="ldr-search"
              placeholder="Buscar por nombre o teléfono..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              icon={<Icon name="search" size={16} className="text-text-muted" />}
            />
          </div>

          {/* Filtro Rol */}
          <div>
            <label htmlFor="ldr-rol" className="block text-xs font-semibold text-text-muted dark:text-[#d4c2bf] mb-1">
              Rol
            </label>
            <Select
              id="ldr-rol"
              value={rolFiltro}
              onChange={(e) => setRolFiltro(e.target.value)}
              options={[
                { value: '', label: 'Todos los Roles' },
                { value: 'Lider', label: 'Líder Principal' },
                { value: 'Sublider', label: 'Sublíder' },
              ]}
            />
          </div>

          {/* Filtro Casa de Paz */}
          <div>
            <label htmlFor="ldr-cdp" className="block text-xs font-semibold text-text-muted dark:text-[#d4c2bf] mb-1">
              Casa de Paz
            </label>
            <Select
              id="ldr-cdp"
              value={cdpFiltro}
              onChange={(e) => setCdpFiltro(e.target.value)}
              options={[
                { value: '', label: 'Todas las Casas' },
                ...casasDisponibles.map((c) => ({
                  value: String(c.id),
                  label: `${c.codigo}${c.anfitrion ? ` (${c.anfitrion})` : ''}`,
                })),
              ]}
            />
          </div>

          {/* Filtro Red Ministerial con aislamiento de supervisor */}
          <div>
            <label htmlFor="ldr-red" className="block text-xs font-semibold text-text-muted dark:text-[#d4c2bf] mb-1">
              Red Ministerial
            </label>
            {isSupervisor ? (
              <div className="p-2.5 rounded-lg bg-surface-low dark:bg-[#150f10] border border-border-subtle dark:border-[#382628] text-sm font-semibold text-vino dark:text-vino-light flex items-center justify-between">
                <span>{perfil?.red_nombre || 'Tu Red Asignada'}</span>
                <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-vino/10 dark:bg-vino-light/20 text-vino dark:text-vino-light">
                  Supervisión
                </span>
              </div>
            ) : (
              <Select
                id="ldr-red"
                value={redFiltro}
                onChange={(e) => setRedFiltro(e.target.value)}
                options={[
                  { value: '', label: 'Todas las Redes' },
                  ...redes.map((r) => ({
                    value: String(r.id),
                    label: r.nombre,
                  })),
                ]}
              />
            )}
          </div>
        </div>
      </section>

      {/* Tabla de Líderes */}
      <section className="table-wrapper">
        <div className="table-header">
          <h2>Registro Activo</h2>
          <div className="table-header-meta">
            Mostrando <strong>{paginatedLideres.length}</strong> de <strong>{filteredLideres.length}</strong> líderes
          </div>
        </div>

        <div className="overflow-x-auto custom-scrollbar">
          <table className="leader-table">
            <thead>
              <tr>
                <th scope="col">Nombre</th>
                <th scope="col">Rol</th>
                <th scope="col">Red</th>
                <th scope="col">Casa de Paz</th>
                <th scope="col">Teléfono / WhatsApp</th>
                <th scope="col">Estado</th>
                {isAdmin && (
                  <th scope="col" className="text-center">
                    Acciones
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={isAdmin ? 7 : 6} className="py-4 text-center text-text-muted">
                      Cargando directorio de liderazgo...
                    </td>
                  </tr>
                ))
              ) : paginatedLideres.length === 0 ? (
                <tr>
                  <td colSpan={isAdmin ? 7 : 6} className="py-8 text-center text-text-muted dark:text-neutral-400">
                    No se encontraron líderes con los filtros seleccionados.
                  </td>
                </tr>
              ) : (
                paginatedLideres.map((l) => {
                  const nombreCompleto = `${l.nombre || ''} ${l.apellido || ''}`.trim();
                  const iniciales = `${(l.nombre || '')[0] || ''}${(l.apellido || '')[0] || ''}`.toUpperCase();
                  const isActivo = l.is_active !== undefined ? Boolean(l.is_active) : true;
                  const isSub = l.rol?.toLowerCase().includes('sub');
                  const cleanPhone = l.telefono ? l.telefono.replace(/[^0-9]/g, '') : '';

                  return (
                    <tr key={l.id}>
                      {/* Avatar e iniciales */}
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="avatar-initials" aria-hidden="true">
                            {iniciales}
                          </div>
                          <span className="font-semibold text-text-main dark:text-neutral-100">
                            {nombreCompleto}
                          </span>
                        </div>
                      </td>

                      {/* Rol */}
                      <td>
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                            isSub
                              ? 'bg-amber-100 text-amber-900 dark:bg-amber-950/40 dark:text-amber-300'
                              : 'bg-rose-100 text-rose-900 dark:bg-rose-950/40 dark:text-rose-300'
                          }`}
                        >
                          {isSub ? 'Sublíder' : 'Líder Principal'}
                        </span>
                      </td>

                      {/* Red */}
                      <td className="text-text-muted dark:text-neutral-300">
                        {l.red_nombre || 'Sin asignar'}
                      </td>

                      {/* Casa de Paz */}
                      <td className="font-medium text-text-main dark:text-neutral-200">
                        {l.cdp_codigo || 'Sin asignar'}
                      </td>

                      {/* Teléfono y WhatsApp Directo (Sin texto de número plano según feedback) */}
                      <td>
                        {l.telefono ? (
                          <div className="inline-flex items-center gap-2">
                            <a
                              href={`https://wa.me/${cleanPhone}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-green-50 hover:bg-green-100 dark:bg-green-950/40 dark:hover:bg-green-900/50 text-green-700 dark:text-green-300 text-xs font-semibold transition-colors"
                              title={`Enviar WhatsApp a ${nombreCompleto}`}
                              aria-label={`WhatsApp a ${nombreCompleto}`}
                            >
                              <Icon name="chat" size={16} />
                              <span>WhatsApp</span>
                            </a>
                            <a
                              href={`tel:${cleanPhone}`}
                              className="btn-call"
                              title={`Llamar a ${nombreCompleto}`}
                              aria-label={`Llamar a ${nombreCompleto}`}
                            >
                              <Icon name="call" size={16} />
                              <span>Llamar</span>
                            </a>
                          </div>
                        ) : (
                          <span className="text-xs text-text-muted">Sin teléfono</span>
                        )}
                      </td>

                      {/* Estado */}
                      <td>
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              isActivo
                                ? 'bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.5)]'
                                : 'bg-neutral-400'
                            }`}
                            aria-hidden="true"
                          />
                          <span
                            className={`text-xs font-medium ${
                              isActivo ? 'text-green-700 dark:text-green-400' : 'text-text-muted'
                            }`}
                          >
                            {isActivo ? 'Activo' : 'Inactivo'}
                          </span>
                        </div>
                      </td>

                      {/* Acciones para Admin estilo ReportesPage */}
                      {isAdmin && (
                        <td className="text-center">
                          <div className="inline-flex items-center justify-center gap-1">
                            <button
                              type="button"
                              onClick={() => handleToggleLider(l)}
                              className="btn-icon btn-toggle cursor-pointer"
                              title={isActivo ? 'Pausar Líder' : 'Reactivar Líder'}
                              aria-label={isActivo ? `Pausar a ${l.nombre}` : `Reactivar a ${l.nombre}`}
                            >
                              <Icon
                                name={isActivo ? 'pause_circle' : 'play_circle'}
                                size={18}
                                className={isActivo ? 'text-primary dark:text-[#f8deda]' : 'text-green-600 dark:text-green-400'}
                              />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenEdit(l)}
                              className="btn-icon btn-edit cursor-pointer"
                              title="Editar Líder"
                              aria-label={`Editar ${l.nombre}`}
                            >
                              <Icon name="edit" size={18} className="text-[#735c00] dark:text-[#dbe786]" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenDelete(l)}
                              className="btn-icon btn-delete cursor-pointer"
                              title="Eliminar Líder"
                              aria-label={`Eliminar ${l.nombre}`}
                            >
                              <Icon name="delete" size={18} className="text-red-600 dark:text-[#ffb4ab]" />
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Paginación Permanente Reutilizable (5 registros por página) */}
        <Pagination
          currentPage={page}
          totalPages={totalPages}
          totalItems={filteredLideres.length}
          itemsPerPage={ITEMS_PER_PAGE}
          onPageChange={setPage}
          itemLabel="líderes"
        />
      </section>

      {/* Footer Info y Cita Bíblica */}
      <footer className="footer-info">
        <div className="quote-box">
          <p className="quote-text">
            "Porque donde están dos o tres congregados en mi nombre, allí estoy yo en medio de ellos."
          </p>
          <p className="quote-author">Mateo 18:20</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportCSV}
            icon={<Icon name="table_chart" size={16} />}
          >
            Exportar Excel / CSV
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => window.print()}
            icon={<Icon name="download" size={16} />}
          >
            Imprimir Directorio
          </Button>
        </div>
      </footer>

      {/* Modales */}
      <LiderFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        lider={selectedLider}
        casasDePaz={casasDePaz}
        supervisorRedId={supervisorRedId}
        onSave={handleSaveLider}
        isSaving={isCreando || isEditando}
      />

      <DeleteLiderModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        lider={liderToDelete}
        onConfirmDelete={handleConfirmDelete}
        isDeleting={isEliminando}
      />
    </div>
  );
};


