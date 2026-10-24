import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Home, Trash2, AlertTriangle, UserCheck, UserPlus } from 'lucide-react';
import type { CasaDePaz, CdpInput } from '../../types/estructura';

interface CasaDePazModalProps {
  isOpen: boolean;
  onClose: () => void;
  casa: CasaDePaz | null; // Si es null => modo creación
  redes: Array<{ id: number; nombre: string; is_active?: number | boolean }>;
  lideresDisponibles: Array<{ id: number; nombre: string; apellido: string; username?: string }>;
  defaultRedId?: number | string;
  onSave: (data: CdpInput) => Promise<void>;
  onDelete?: (id: number) => Promise<void>;
  isSaving?: boolean;
  isDeleting?: boolean;
}

export const CasaDePazModal: React.FC<CasaDePazModalProps> = ({
  isOpen,
  onClose,
  casa,
  redes,
  lideresDisponibles,
  defaultRedId,
  onSave,
  onDelete,
  isSaving = false,
  isDeleting = false,
}) => {
  const isEdit = Boolean(casa);

  // Form State
  const [codigo, setCodigo] = useState('');
  const [redId, setRedId] = useState('');
  const [anfitrion, setAnfitrion] = useState('');
  const [telefono, setTelefono] = useState('');
  const [direccion, setDireccion] = useState('');
  const [isActive, setIsActive] = useState('1');

  // Modo de usuario / líder
  const [modoUsuario, setModoUsuario] = useState<'existente' | 'nuevo'>('existente');
  const [liderId, setLiderId] = useState('');
  const [nuevoNombre, setNuevoNombre] = useState('');
  const [nuevoApellido, setNuevoApellido] = useState('');
  const [nuevoUsername, setNuevoUsername] = useState('');
  const [nuevoPassword, setNuevoPassword] = useState('');

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  useEffect(() => {
    if (casa) {
      setCodigo(casa.codigo || '');
      setRedId(casa.red_id ? String(casa.red_id) : '');
      setAnfitrion(casa.anfitrion || '');
      setTelefono(casa.telefono || '');
      setDireccion(casa.direccion || '');
      setIsActive(casa.is_active ? '1' : '0');
      setModoUsuario('existente');
      setLiderId('');
    } else {
      setCodigo('');
      setRedId(defaultRedId ? String(defaultRedId) : (redes.length > 0 ? String(redes[0].id) : ''));
      setAnfitrion('');
      setTelefono('');
      setDireccion('');
      setIsActive('1');
      setModoUsuario(lideresDisponibles.length > 0 ? 'existente' : 'nuevo');
      setLiderId('');
      setNuevoNombre('');
      setNuevoApellido('');
      setNuevoUsername('');
      setNuevoPassword('');
    }
    setShowDeleteConfirm(false);
    setErrorLocal(null);
  }, [casa, redes, lideresDisponibles, defaultRedId, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!codigo.trim() || !redId || !anfitrion.trim() || !telefono.trim() || !direccion.trim()) {
      setErrorLocal('Por favor completa todos los campos obligatorios del centro.');
      return;
    }

    if (!isEdit && modoUsuario === 'nuevo') {
      if (!nuevoNombre.trim() || !nuevoUsername.trim() || !nuevoPassword.trim()) {
        setErrorLocal('Por favor completa los datos de la nueva cuenta de usuario (nombre, usuario y contraseña).');
        return;
      }
    }

    setErrorLocal(null);

    const payload: CdpInput = {
      codigo: codigo.trim(),
      red_id: redId,
      anfitrion: anfitrion.trim(),
      telefono: telefono.trim(),
      direccion: direccion.trim(),
      is_active: isActive === '1',
      modo_usuario: modoUsuario,
      lider_id: modoUsuario === 'existente' && liderId ? Number(liderId) : null,
      nuevo_usuario_nombre: nuevoNombre.trim(),
      nuevo_usuario_apellido: nuevoApellido.trim(),
      nuevo_usuario_username: nuevoUsername.trim(),
      nuevo_usuario_password: nuevoPassword,
    };

    try {
      await onSave(payload);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorLocal(err.message);
      } else {
        setErrorLocal('Error al guardar la Casa de Paz.');
      }
    }
  };

  const handleConfirmDelete = async () => {
    if (!casa || !onDelete) return;
    try {
      await onDelete(casa.id);
      setShowDeleteConfirm(false);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorLocal(err.message);
      } else {
        setErrorLocal('Error al dar de baja la Casa de Paz.');
      }
    }
  };

  return (
    <>
      <Modal
        isOpen={isOpen && !showDeleteConfirm}
        onClose={onClose}
        title={isEdit ? `Editar Casa: ${casa?.codigo}` : 'Registrar Nueva Casa de Paz'}
        headerIcon={<Home className="w-5 h-5 text-vino dark:text-vino-light" />}
        maxWidth="xl"
        footer={
          <div className="flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-3 w-full">
            <div>
              {isEdit && onDelete && (
                <Button
                  type="button"
                  variant="danger-outline"
                  onClick={() => setShowDeleteConfirm(true)}
                  icon={<Trash2 className="w-4 h-4" />}
                >
                  Baja Defensiva
                </Button>
              )}
            </div>
            <div className="flex items-center justify-end gap-2.5">
              <Button type="button" variant="secondary" onClick={onClose} disabled={isSaving}>
                Cancelar
              </Button>
              <Button
                type="submit"
                form="form-cdp-modal"
                variant="primary"
                isLoading={isSaving}
              >
                {isEdit ? 'Actualizar Casa' : 'Registrar Casa'}
              </Button>
            </div>
          </div>
        }
      >
        <form id="form-cdp-modal" onSubmit={handleSubmit} className="flex flex-col gap-5">
          {errorLocal && (
            <div className="p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-800 dark:text-red-300 text-xs">
              {errorLocal}
            </div>
          )}

          {/* Sección 1: Datos del Centro */}
          <div>
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-vino dark:text-vino-light mb-3 pb-1 border-b border-border-subtle dark:border-neutral-700">
              Datos del Centro
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                  Código de la Casa <span className="text-red-500">*</span>
                </label>
                <Input
                  id="cdpCodigo"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  placeholder="Ej. SUR-001"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                  Red Ministerial <span className="text-red-500">*</span>
                </label>
                <Select
                  id="cdpRedId"
                  value={redId}
                  onChange={(e) => setRedId(e.target.value)}
                  options={[
                    { value: '', label: '-- Selecciona una red --' },
                    ...redes.map((r) => ({
                      value: String(r.id),
                      label: r.nombre,
                    })),
                  ]}
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                  Anfitrión de la Casa <span className="text-red-500">*</span>
                </label>
                <Input
                  id="cdpAnfitrion"
                  value={anfitrion}
                  onChange={(e) => setAnfitrion(e.target.value)}
                  placeholder="Ej. Familia Gómez Ríos"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                  Teléfono de Contacto <span className="text-red-500">*</span>
                </label>
                <Input
                  id="cdpTelefono"
                  value={telefono}
                  onChange={(e) => setTelefono(e.target.value)}
                  placeholder="Ej. 0414-1234567"
                  required
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                  Dirección Física <span className="text-red-500">*</span>
                </label>
                <Input
                  id="cdpDireccion"
                  value={direccion}
                  onChange={(e) => setDireccion(e.target.value)}
                  placeholder="Calle, sector, punto de referencia"
                  required
                />
              </div>

              {isEdit && (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                    Estado Operativo
                  </label>
                  <Select
                    id="cdpIsActive"
                    value={isActive}
                    onChange={(e) => setIsActive(e.target.value)}
                    options={[
                      { value: '1', label: 'Activa (En funcionamiento)' },
                      { value: '0', label: 'Pausada (Temporalmente inactiva)' },
                    ]}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Sección 2: Asignación de Líder Responsable */}
          {!isEdit && (
            <div>
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-vino dark:text-vino-light mb-3 pb-1 border-b border-border-subtle dark:border-neutral-700">
                Líder Responsable
              </h4>

              {/* Selector de Modo */}
              <div className="flex items-center gap-3 mb-4">
                <button
                  type="button"
                  className={`flex-1 py-2 px-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    modoUsuario === 'existente'
                      ? 'bg-surface-container dark:bg-vino/20 border-vino dark:border-vino-light text-vino dark:text-vino-light shadow-sm'
                      : 'border-border-subtle dark:border-neutral-700 text-text-muted hover:bg-surface-low dark:hover:bg-neutral-800'
                  }`}
                  onClick={() => setModoUsuario('existente')}
                >
                  <UserCheck className="w-4 h-4" />
                  <span>Asignar Líder Existente</span>
                </button>
                <button
                  type="button"
                  className={`flex-1 py-2 px-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    modoUsuario === 'nuevo'
                      ? 'bg-surface-container dark:bg-vino/20 border-vino dark:border-vino-light text-vino dark:text-vino-light shadow-sm'
                      : 'border-border-subtle dark:border-neutral-700 text-text-muted hover:bg-surface-low dark:hover:bg-neutral-800'
                  }`}
                  onClick={() => setModoUsuario('nuevo')}
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Crear Nuevo Usuario Líder</span>
                </button>
              </div>

              {modoUsuario === 'existente' ? (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                    Seleccionar Usuario
                  </label>
                  <Select
                    id="cdpLiderId"
                    value={liderId}
                    onChange={(e) => setLiderId(e.target.value)}
                    options={[
                      { value: '', label: '-- Selecciona un líder disponible --' },
                      ...lideresDisponibles.map((l) => ({
                        value: String(l.id),
                        label: `${l.nombre} ${l.apellido} ${l.username ? `(@${l.username})` : ''}`,
                      })),
                    ]}
                  />
                  <p className="text-[11px] text-text-muted dark:text-neutral-400 mt-1">
                    Solo se muestran usuarios disponibles sin otra Casa de Paz activa asignada.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 rounded-xl bg-surface-low dark:bg-neutral-900 border border-border-subtle dark:border-neutral-800">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                      Nombre <span className="text-red-500">*</span>
                    </label>
                    <Input
                      id="cdpNuevoNombre"
                      value={nuevoNombre}
                      onChange={(e) => setNuevoNombre(e.target.value)}
                      placeholder="Nombre del líder"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                      Apellido
                    </label>
                    <Input
                      id="cdpNuevoApellido"
                      value={nuevoApellido}
                      onChange={(e) => setNuevoApellido(e.target.value)}
                      placeholder="Apellido del líder"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                      Nombre de Usuario <span className="text-red-500">*</span>
                    </label>
                    <Input
                      id="cdpNuevoUsername"
                      value={nuevoUsername}
                      onChange={(e) => setNuevoUsername(e.target.value)}
                      placeholder="Ej. juan.perez"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
                      Contraseña Temporal <span className="text-red-500">*</span>
                    </label>
                    <Input
                      id="cdpNuevoPassword"
                      type="password"
                      value={nuevoPassword}
                      onChange={(e) => setNuevoPassword(e.target.value)}
                      placeholder="Mínimo 6 caracteres"
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </form>
      </Modal>

      {/* Modal de Confirmación Defensiva al Eliminar Casa de Paz */}
      {showDeleteConfirm && (
        <Modal
          isOpen={showDeleteConfirm}
          onClose={() => setShowDeleteConfirm(false)}
          title="Baja Defensiva de Casa de Paz"
          headerIcon={<AlertTriangle className="w-5 h-5 text-red-500" />}
          maxWidth="md"
          footer={
            <div className="flex items-center justify-end gap-2.5 w-full">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancelar
              </Button>
              <Button
                type="button"
                variant="danger"
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                isLoading={isDeleting}
                icon={<Trash2 className="w-4 h-4" />}
              >
                Confirmar Baja
              </Button>
            </div>
          }
        >
          <div className="flex flex-col gap-3 text-sm text-text-main dark:text-neutral-200">
            <p>
              ¿Estás seguro de que deseas dar de baja la Casa de Paz{' '}
              <strong>"{casa?.codigo}"</strong>?
            </p>
            <p className="text-text-muted dark:text-neutral-400 text-xs">
              Si esta casa tiene reportes históricos registrados en la base de datos, el sistema
              aplicará una <strong>desactivación defensiva</strong> para salvaguardar la auditoría ministerial.
            </p>
          </div>
        </Modal>
      )}
    </>
  );
};
