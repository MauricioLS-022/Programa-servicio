import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Icon } from '../ui/Icon';
import type { Usuario } from '../../types/usuario';

export interface DeleteUsuarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  usuario: Usuario | null;
  currentUserId?: string | null;
  onConfirmDelete: (usuarioId: string) => Promise<void>;
  isDeleting?: boolean;
}

export const DeleteUsuarioModal: React.FC<DeleteUsuarioModalProps> = ({
  isOpen,
  onClose,
  usuario,
  currentUserId,
  onConfirmDelete,
  isDeleting = false,
}) => {
  const [confirmText, setConfirmText] = useState('');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  useEffect(() => {
    setConfirmText('');
    setErrorLocal(null);
  }, [isOpen, usuario]);

  if (!usuario) return null;

  const isSelf = Boolean(currentUserId && String(currentUserId) === String(usuario.id));
  const hasDependencies = Boolean(usuario.red_nombre || usuario.cdp_codigo);

  // Candado 1 y 2: Bloqueo de auto-eliminación o de responsabilidades activas
  if (isSelf || hasDependencies) {
    let reasonText = '';
    let hintText = '';

    if (isSelf) {
      reasonText = 'No puedes eliminar tu propia cuenta de usuario en esta sesión.';
      hintText = 'Por motivos de seguridad e integridad administrativa, la cuenta en uso no puede ser dada de baja por sí misma.';
    } else if (usuario.red_nombre) {
      reasonText = `Este usuario está asignado actualmente como supervisor de la red "${usuario.red_nombre}".`;
      hintText = 'Para eliminarlo, primero debes reasignar la supervisión de dicha red en el módulo de Estructura Ministerial.';
    } else {
      reasonText = `Este usuario está vinculado actualmente a la Casa de Paz "${usuario.cdp_codigo}".`;
      hintText = 'Para eliminarlo, primero debes desvincular o reasignar la Casa de Paz correspondiente.';
    }

    return (
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title="No es posible eliminar el usuario"
        headerIcon={<Icon name="block" size={20} className="text-red-600 dark:text-red-400" />}
        maxWidth="md"
        footer={
          <div className="flex justify-end w-full">
            <button type="button" className="btn-modal btn-modal-cancel" onClick={onClose}>
              Entendido
            </button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-sm text-text-main dark:text-[#f8f2f0]">{reasonText}</p>
          <p className="text-xs text-text-muted dark:text-[#d4c2bf] bg-surface-low dark:bg-[#150f10] p-3 rounded-lg border border-border-subtle dark:border-[#382628]">
            {hintText}
          </p>
        </div>
      </Modal>
    );
  }

  // Candado 3: Confirmación escribiendo 'ELIMINAR'
  const isDeleteEnabled = confirmText.trim().toUpperCase() === 'ELIMINAR';

  const handleDelete = async () => {
    if (!isDeleteEnabled) return;
    try {
      setErrorLocal(null);
      await onConfirmDelete(usuario.id);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorLocal(err.message);
      } else {
        setErrorLocal('Error al eliminar el usuario.');
      }
    }
  };

  const nombreCompleto = `${usuario.nombre || ''} ${usuario.apellido || ''}`.trim() || `@${usuario.username}`;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Confirmar Eliminación"
      headerIcon={<Icon name="warning" size={20} className="text-red-600 dark:text-red-400" />}
      maxWidth="md"
      footer={
        <div className="flex items-center justify-end gap-3 w-full">
          <button type="button" className="btn-modal btn-modal-cancel" onClick={onClose} disabled={isDeleting}>
            Cancelar
          </button>
          <button
            type="button"
            className="btn-modal btn-modal-delete"
            onClick={handleDelete}
            disabled={!isDeleteEnabled || isDeleting}
          >
            <Icon name="delete" size={16} />
            <span>{isDeleting ? 'Eliminando...' : 'Eliminar'}</span>
          </button>
        </div>
      }
    >
      <div className="space-y-4">
        {errorLocal && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 text-xs text-red-700 dark:text-red-300">
            {errorLocal}
          </div>
        )}

        <p className="text-sm text-text-main dark:text-[#f8f2f0]">
          ¿Estás seguro de que deseas eliminar al usuario <strong>{nombreCompleto}</strong>? Esta
          acción dará de baja su cuenta de forma permanente e irreversible.
        </p>

        <div>
          <label
            htmlFor="delete-confirm-input"
            className="block text-xs font-semibold text-text-muted dark:text-neutral-300 mb-1.5"
          >
            Escribe <span className="font-bold text-red-600 dark:text-red-400">ELIMINAR</span> para confirmar:
          </label>
          <Input
            id="delete-confirm-input"
            placeholder="ELIMINAR"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            autoComplete="off"
            autoFocus
          />
        </div>
      </div>
    </Modal>
  );
};

