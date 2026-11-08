import React, { useState, useMemo, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useUsuarios, useUsuarioMutations } from '../hooks/useUsuarios';
import { useToast } from '../context/ToastContext';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { UsuarioModal } from '../components/usuarios/UsuarioModal';
import { DeleteUsuarioModal } from '../components/usuarios/DeleteUsuarioModal';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Icon } from '../components/ui/Icon';
import { Pagination } from '../components/ui/Pagination';
import type { Usuario, UsuarioInput } from '../types/usuario';
import '../styles/shared-tables.css';
import '../styles/usuarios.css';

const ITEMS_PER_PAGE = 5;

export const UsuariosPage: React.FC = () => {
  useDocumentTitle('Usuarios del Sistema - Vino Nuevo');
  const { user: currentUser } = useAuth();
  const { success, error: toastError, info } = useToast();

  const { usuarios, totalActivos, isLoading, isError, error, refetch } = useUsuarios();
  const {
    crearUsuario,
    isCreando,
    editarUsuario,
    isEditando,
    toggleUsuario,
    eliminarUsuario,
    isEliminando,
  } = useUsuarioMutations();

  // Estados de filtros client-side (Live Search instantáneo Requerimiento #25)
  const [searchQuery, setSearchQuery] = useState('');
  const [rolFiltro, setRolFiltro] = useState('');
  const [page, setPage] = useState(1);

  // Modales
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUsuario, setSelectedUsuario] = useState<Usuario | null>(null);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [usuarioToDelete, setUsuarioToDelete] = useState<Usuario | null>(null);

  // Reset page when filter changes
  useEffect(() => {
    setPage(1);
  }, [searchQuery, rolFiltro]);

  // Filtrado reactivo en memoria (0ms latency)
  const filteredUsuarios = useMemo(() => {
    return usuarios.filter((u) => {
      const q = searchQuery.toLowerCase().trim();
      const matchSearch =
        !q ||
        (u.nombre && u.nombre.toLowerCase().includes(q)) ||
        (u.apellido && u.apellido.toLowerCase().includes(q)) ||
        (u.username && u.username.toLowerCase().includes(q));

      const uRol = (u.tipo_usuario || u.rol || '').toLowerCase();
      const matchRol =
        !rolFiltro ||
        (rolFiltro === 'lider_cdp' ? uRol === 'lider_cdp' || uRol === 'cdp' : uRol === rolFiltro);

      return matchSearch && matchRol;
    });
  }, [usuarios, searchQuery, rolFiltro]);

  // Paginación de 5 resultados por página
  const totalPages = Math.max(1, Math.ceil(filteredUsuarios.length / ITEMS_PER_PAGE));
  const paginatedUsuarios = useMemo(() => {
    const start = (page - 1) * ITEMS_PER_PAGE;
    return filteredUsuarios.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredUsuarios, page]);

  // Handlers
  const handleOpenCreate = () => {
    setSelectedUsuario(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (usuario: Usuario) => {
    setSelectedUsuario(usuario);
    setIsModalOpen(true);
  };

  const handleOpenDelete = (usuario: Usuario) => {
    setUsuarioToDelete(usuario);
    setIsDeleteModalOpen(true);
  };

  const handleSaveUsuario = async (data: UsuarioInput) => {
    if (selectedUsuario) {
      await editarUsuario({ id: selectedUsuario.id, data });
      success('Usuario actualizado exitosamente.');
    } else {
      await crearUsuario(data);
      success('Usuario creado exitosamente.');
    }
  };

  const handleToggleEstado = async (u: Usuario) => {
    try {
      const res = await toggleUsuario(u.id);
      success(res.message || 'Estado del usuario actualizado.');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al cambiar el estado del usuario.';
      toastError(msg);
    }
  };

  const handleConfirmDelete = async (usuarioId: string) => {
    try {
      const res = await eliminarUsuario(usuarioId);
      success(res.message || 'Usuario eliminado permanentemente.');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al eliminar el usuario.';
      toastError(msg);
      throw err;
    }
  };

  const handleExportCSV = () => {
    if (!filteredUsuarios.length) {
      info('No hay usuarios para exportar con los filtros actuales.');
      return;
    }
    const headers = ['ID', 'Nombre', 'Apellido', 'Username', 'Rol', 'Estado', 'Red', 'Casa de Paz'];
    const rows = filteredUsuarios.map((u) => [
      u.id,
      `"${u.nombre || ''}"`,
      `"${u.apellido || ''}"`,
      `"@${u.username}"`,
      `"${u.tipo_usuario || u.rol || ''}"`,
      u.is_active ? 'Activo' : 'Inactivo',
      `"${u.red_nombre || ''}"`,
      `"${u.cdp_codigo || ''}"`,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `usuarios_vino_nuevo_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="usuarios-page-wrapper">
      {/* Header */}
      <header className="page-header">
        <div className="header-text">
          <p className="subtitle">Gestión Administrativa</p>
          <h1 className="title">Usuarios del Sistema</h1>
          <p className="description">
            Administra los accesos y roles de la comunidad Vino Nuevo desde un panel centralizado y seguro.
          </p>
        </div>
        <div>
          <Button
            variant="primary"
            onClick={handleOpenCreate}
            icon={<Icon name="person_add" size={16} />}
          >
            Agregar Usuario
          </Button>
        </div>
      </header>

      {/* Circuit Breaker / Error State */}
      {isError && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-sm text-red-800 dark:text-red-200 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Icon name="warning" size={20} className="text-red-600 dark:text-red-400 shrink-0" />
            <span>
              {error instanceof Error
                ? error.message
                : 'Error al conectar con el servicio de usuarios. Es posible que el Circuit Breaker esté abierto.'}
            </span>
          </div>
          <Button variant="secondary" size="sm" onClick={() => refetch()} icon={<Icon name="refresh" size={16} />}>
            Reintentar
          </Button>
        </div>
      )}

      {/* Bento Grid */}
      <div className="bento-grid">
        {/* Sidebar de Estadísticas */}
        <aside className="stats-sidebar">
          <div className="stat-card stat-primary">
            <div className="icon-box">
              <Icon name="group" size={24} />
            </div>
            <div>
              <h3>{isLoading ? '...' : totalActivos}</h3>
              <p>Usuarios Activos</p>
            </div>
          </div>

          <div className="stat-card stat-info">
            <h3 className="info-title">
              <Icon name="verified_user" size={16} className="text-amber-700 dark:text-amber-400" />
              Seguridad de Roles
            </h3>
            <p className="info-desc">
              Solo los administradores pueden modificar estructuras de jerarquía y reportes financieros.
            </p>
          </div>
        </aside>

        {/* Sección de Tabla */}
        <section className="table-section table-wrapper">
          <div className="table-header">
            <h2>Directorio General</h2>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleExportCSV}
                title="Exportar a CSV"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-white/10 hover:bg-white/20 border border-white/20 transition-all cursor-pointer"
              >
                <Icon name="download" size={14} />
                <span>Exportar CSV</span>
              </button>
            </div>
          </div>

          {/* Filtros y Live Search */}
          <div className="p-4 border-b border-border-subtle/80 dark:border-neutral-800 flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <Input
                placeholder="Buscar por nombre o usuario..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                icon={<Icon name="search" size={16} className="text-text-muted" />}
              />
            </div>
            <div className="w-full sm:w-56">
              <Select
                value={rolFiltro}
                onChange={(e) => setRolFiltro(e.target.value)}
                options={[
                  { value: '', label: 'Todos los Roles' },
                  { value: 'admin', label: 'Admin' },
                  { value: 'supervisor', label: 'Supervisor' },
                  { value: 'lider_cdp', label: 'Líder' },
                ]}
              />
            </div>
          </div>

          {/* Tabla Responsive */}
          <div className="overflow-x-auto custom-scrollbar">
            <table className="user-table">
              <thead>
                <tr>
                  <th scope="col">Usuario</th>
                  <th scope="col">Username</th>
                  <th scope="col">Rol</th>
                  <th scope="col">Status</th>
                  <th scope="col" className="text-right">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  Array.from({ length: 4 }).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan={5} className="py-4 px-6 text-center text-text-muted">
                        Cargando usuarios...
                      </td>
                    </tr>
                  ))
                ) : paginatedUsuarios.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-text-muted dark:text-neutral-400">
                      No se encontraron usuarios con los filtros seleccionados.
                    </td>
                  </tr>
                ) : (
                  paginatedUsuarios.map((u) => {
                    const nombreCompleto = `${u.nombre || ''} ${u.apellido || ''}`.trim() || 'Sin nombre';
                    const rawRol = (u.tipo_usuario || u.rol || 'lider_cdp').toLowerCase();
                    const rolLabel =
                      rawRol === 'admin'
                        ? 'Admin'
                        : rawRol === 'supervisor'
                        ? 'Supervisor'
                        : 'Líder';
                    const rolClass =
                      rawRol === 'admin'
                        ? 'badge-admin'
                        : rawRol === 'supervisor'
                        ? 'badge-supervisor'
                        : 'badge-lider';

                    const isActive = Boolean(u.is_active);

                    return (
                      <tr key={u.id}>
                        <td>
                          <strong>{nombreCompleto}</strong>
                          {u.red_nombre && (
                            <span className="block text-[11px] text-text-muted">Red: {u.red_nombre}</span>
                          )}
                          {u.cdp_codigo && (
                            <span className="block text-[11px] text-text-muted">CDP: {u.cdp_codigo}</span>
                          )}
                        </td>
                        <td className="text-text-muted">@{u.username}</td>
                        <td>
                          <span className={`badge ${rolClass}`}>{rolLabel}</span>
                        </td>
                        <td>
                          <div className="flex items-center gap-2">
                            <span
                              className={`status-dot ${isActive ? 'dot-active' : 'dot-inactive'}`}
                              aria-hidden="true"
                            />
                            <span className={isActive ? 'text-green-700 dark:text-green-400 font-medium' : 'text-text-muted'}>
                              {isActive ? 'Activo' : 'Inactivo'}
                            </span>
                          </div>
                        </td>
                        <td className="text-right">
                          <div className="inline-flex items-center justify-end gap-1">
                            <button
                              type="button"
                              onClick={() => handleToggleEstado(u)}
                              className="btn-icon btn-toggle cursor-pointer"
                              title={isActive ? 'Desactivar Usuario' : 'Reactivar Usuario'}
                              aria-label={isActive ? `Desactivar ${u.username}` : `Reactivar ${u.username}`}
                            >
                              <Icon
                                name={isActive ? 'pause_circle' : 'play_circle'}
                                size={18}
                                className={isActive ? 'text-primary dark:text-[#f8deda]' : 'text-green-600 dark:text-green-400'}
                              />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenEdit(u)}
                              className="btn-icon btn-edit cursor-pointer"
                              title="Editar Usuario"
                              aria-label={`Editar ${u.username}`}
                            >
                              <Icon name="edit" size={18} className="text-[#735c00] dark:text-[#dbe786]" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenDelete(u)}
                              className="btn-icon btn-delete cursor-pointer"
                              title="Eliminar Usuario"
                              aria-label={`Eliminar ${u.username}`}
                            >
                              <Icon name="delete" size={18} className="text-red-600 dark:text-[#ffb4ab]" />
                            </button>
                          </div>
                        </td>
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
            totalItems={filteredUsuarios.length}
            itemsPerPage={ITEMS_PER_PAGE}
            onPageChange={setPage}
            itemLabel="usuarios"
          />
        </section>
      </div>

      {/* Modales */}
      <UsuarioModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        usuario={selectedUsuario}
        onSave={handleSaveUsuario}
        isSaving={isCreando || isEditando}
      />

      <DeleteUsuarioModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        usuario={usuarioToDelete}
        currentUserId={currentUser?.id}
        onConfirmDelete={handleConfirmDelete}
        isDeleting={isEliminando}
      />
    </div>
  );
};

