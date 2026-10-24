import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Network, AlertTriangle, ShieldAlert, Trash2 } from 'lucide-react';
import type { Red } from '../../types/estructura';

interface RedModalProps {
  isOpen: boolean;
  onClose: () => void;
  red: Red | null; // Si es null => modo creación
  supervisores: Array<{ id: number; nombre: string; apellido: string; username: string }>;
  onSave: (data: { nombre: string; supervisor_id?: number | string | null }) => Promise<void>;
  onDelete?: (id: number) => Promise<void>;
  isSaving?: boolean;
  isDeleting?: boolean;
}

export const RedModal: React.FC<RedModalProps> = ({
  isOpen,
  onClose,
  red,
  supervisores,
  onSave,
  onDelete,
  isSaving = false,
  isDeleting = false,
}) => {
  const isEdit = Boolean(red);
  const [nombre, setNombre] = useState('');
  const [supervisorId, setSupervisorId] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteInputText, setDeleteInputText] = useState('');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  useEffect(() => {
    if (red) {
      setNombre(red.nombre || '');
      setSupervisorId(red.supervisor_id ? String(red.supervisor_id) : '');
    } else {
      setNombre('');
      setSupervisorId('');
    }
    setShowDeleteConfirm(false);
    setDeleteInputText('');
    setErrorLocal(null);
  }, [red, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nombre.trim()) {
      setErrorLocal('El nombre de la red es obligatorio.');
      return;
    }
    setErrorLocal(null);
    try {
      await onSave({
        nombre: nombre.trim(),
        supervisor_id: supervisorId ? Number(supervisorId) : null,
      });
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorLocal(err.message);
      } else {
        setErrorLocal('Error al guardar la red.');
      }
    }
  };

  const totalCasas = (red as any)?.total_casas || 0;
  const isDeleteBlocked = totalCasas > 0;

  const handleConfirmDelete = async () => {
    if (!red || !onDelete) return;
    try {
      await onDelete(red.id);
      setShowDeleteConfirm(false);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorLocal(err.message);
      } else {
        setErrorLocal('Error al eliminar la red.');
      }
    }
  };

  return (
    <>
      <Modal
        isOpen={isOpen && !showDeleteConfirm}
        onClose={onClose}
        title={isEdit ? `Editar Red: ${red?.nombre}` : 'Nueva Red Ministerial'}
        headerIcon={<Network className="w-5 h-5 text-vino dark:text-vino-light" />}
        maxWidth="md"
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
                  Eliminar Red
                </Button>
              )}
            </div>
            <div className="flex items-center justify-end gap-2.5">
              <Button type="button" variant="secondary" onClick={onClose} disabled={isSaving}>
                Cancelar
              </Button>
              <Button
                type="submit"
                form="form-red-modal"
                variant="primary"
                isLoading={isSaving}
              >
                {isEdit ? 'Actualizar Red' : 'Guardar Red'}
              </Button>
            </div>
          </div>
        }
      >
        <form id="form-red-modal" onSubmit={handleSubmit} className="flex flex-col gap-4">
          {errorLocal && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-800 dark:text-red-300 text-xs">
              {errorLocal}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
              Nombre de la Red <span className="text-red-500">*</span>
            </label>
            <Input
              id="nombreRed"
              name="nombre"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Ej. Red de Crecimiento Norte"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-300 mb-1.5">
              Supervisor Asignado
            </label>
            <Select
              id="supervisorId"
              name="supervisor_id"
              value={supervisorId}
              onChange={(e) => setSupervisorId(e.target.value)}
              options={[
                { value: '', label: '-- Sin supervisor asignado --' },
                ...supervisores.map((s) => ({
                  value: String(s.id),
                  label: `${s.nombre} ${s.apellido} (@${s.username})`,
                })),
              ]}
            />
            <p className="text-[11px] text-text-muted dark:text-neutral-400 mt-1">
              Muestra los usuarios del sistema con rol de supervisor disponibles para asignación.
            </p>
          </div>
        </form>
      </Modal>

      {/* Modal de Confirmación Defensiva / Bloqueo de Eliminación */}
      {showDeleteConfirm && (
        <Modal
          isOpen={showDeleteConfirm}
          onClose={() => setShowDeleteConfirm(false)}
          title={isDeleteBlocked ? 'No es posible eliminar la red' : 'Confirmar Eliminación'}
          headerIcon={
            isDeleteBlocked ? (
              <ShieldAlert className="w-5 h-5 text-amber-500" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-red-500" />
            )
          }
          maxWidth="md"
          footer={
            <div className="flex items-center justify-end gap-2.5 w-full">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setShowDeleteConfirm(false)}
              >
                {isDeleteBlocked ? 'Entendido' : 'Cancelar'}
              </Button>
              {!isDeleteBlocked && (
                <Button
                  type="button"
                  variant="danger"
                  onClick={handleConfirmDelete}
                  disabled={deleteInputText !== 'ELIMINAR' || isDeleting}
                  isLoading={isDeleting}
                  icon={<Trash2 className="w-4 h-4" />}
                >
                  Eliminar Definitivamente
                </Button>
              )}
            </div>
          }
        >
          {isDeleteBlocked ? (
            <div className="flex flex-col gap-3 text-sm text-text-main dark:text-neutral-200">
              <p>
                La red <strong>{red?.nombre}</strong> tiene actualmente{' '}
                <strong>{totalCasas}</strong> {totalCasas === 1 ? 'Casa de Paz vinculada' : 'Casas de Paz vinculadas'}.
              </p>
              <p className="text-text-muted dark:text-neutral-400 text-xs">
                Para poder eliminarla, primero debes reasignar o desvincular sus Casas de Paz.
                Si deseas suspender sus actividades sin perder la información histórica, puedes{' '}
                <strong>poner la red en pausa</strong> desde el menú de la vista de estructura.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-3 text-sm text-text-main dark:text-neutral-200">
              <p>
                ¿Estás seguro de que deseas eliminar la red <strong>{red?.nombre}</strong>? Esta acción
                dará de baja la red del sistema de forma permanente.
              </p>
              <div className="mt-2">
                <label className="block text-xs font-bold text-text-main dark:text-neutral-200 mb-1.5">
                  Escribe <span className="text-red-600 dark:text-red-400 font-extrabold">ELIMINAR</span> para confirmar:
                </label>
                <Input
                  id="deleteInput"
                  value={deleteInputText}
                  onChange={(e) => setDeleteInputText(e.target.value)}
                  placeholder="ELIMINAR"
                  autoComplete="off"
                />
              </div>
            </div>
          )}
        </Modal>
      )}
    </>
  );
};
