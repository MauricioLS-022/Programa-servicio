import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Icon } from '../ui/Icon';
import type { Lider } from '../../types/estructura';

export interface DeleteLiderModalProps {
  isOpen: boolean;
  onClose: () => void;
  lider: Lider | null;
  onConfirmDelete: (liderId: number) => Promise<void>;
  isDeleting?: boolean;
}

export const DeleteLiderModal: React.FC<DeleteLiderModalProps> = ({
  isOpen,
  onClose,
  lider,
  onConfirmDelete,
  isDeleting = false,
}) => {
  const [confirmText, setConfirmText] = useState('');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  useEffect(() => {
    setConfirmText('');
    setErrorLocal(null);
  }, [isOpen, lider]);

  if (!lider) return null;

  const isDeleteEnabled = confirmText.trim().toUpperCase() === 'ELIMINAR';

  const handleDelete = async () => {
    if (!isDeleteEnabled) return;
    try {
      setErrorLocal(null);
      await onConfirmDelete(lider.id);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorLocal(err.message);
      } else {
        setErrorLocal('Error al eliminar el líder.');
      }
    }
  };

  const nombreCompleto = `${lider.nombre} ${lider.apellido}`.trim();

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

        <p className="text-sm text-text-main dark:text-neutral-200">
          ¿Estás seguro de que deseas eliminar al líder <strong>{nombreCompleto}</strong>? Esta
          acción dará de baja su registro en el sistema.
        </p>

        <div>
          <label
            htmlFor="delete-lider-input"
            className="block text-xs font-semibold text-text-muted dark:text-neutral-300 mb-1.5"
          >
            Escribe <span className="font-bold text-red-600 dark:text-red-400">ELIMINAR</span> para confirmar:
          </label>
          <Input
            id="delete-lider-input"
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

