import React, { useState } from 'react';
import { Modal } from '../../ui/Modal';
import { Icon } from '../../ui/Icon';
import { api } from '../../../api/client';
import type { LiderReporteItem } from '../../../types/liderDashboard';

export interface LiderEliminarModalProps {
  isOpen: boolean;
  onClose: () => void;
  reporte: LiderReporteItem | null;
  onSuccess: () => void;
}

export const LiderEliminarModal: React.FC<LiderEliminarModalProps> = ({
  isOpen,
  onClose,
  reporte,
  onSuccess,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleDelete = async () => {
    if (!reporte) return;
    setIsLoading(true);
    setErrorMessage(null);

    try {
      await api.delete(`/reportes/${reporte.id}`);
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al eliminar el reporte.';
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  if (!reporte) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Eliminar Reporte"
      headerIcon={
        <div className="modal-header-icon danger">
          <Icon name="warning" size={20} />
        </div>
      }
      maxWidth="md"
      footer={
        <div className="flex items-center justify-end gap-3 w-full">
          <button
            type="button"
            className="btn-modal btn-modal-cancel"
            onClick={onClose}
            disabled={isLoading}
            data-testid="btn-cancelar-eliminar"
          >
            Cancelar
          </button>
          <button
            type="button"
            className="btn-modal btn-modal-delete"
            onClick={handleDelete}
            disabled={isLoading}
            data-testid="btn-confirmar-eliminar"
          >
            <Icon name="delete_forever" size={16} />
            <span>{isLoading ? 'Eliminando...' : 'Sí, Eliminar Reporte'}</span>
          </button>
        </div>
      }
    >
      <div className="lider-modal-body" data-testid="lider-modal-eliminar-body">
        {errorMessage && (
          <div
            style={{
              background: 'var(--danger-bg, #fee2e2)',
              color: 'var(--danger-color, #b32626)',
              padding: '10px 14px',
              borderRadius: '8px',
              fontSize: '0.88rem',
              fontWeight: 600,
            }}
          >
            {errorMessage}
          </div>
        )}

        <div className="delete-warning-box">
          <p className="delete-warning-text">
            <strong>¿Estás seguro de que deseas eliminar este reporte semanal?</strong>
          </p>
          <p style={{ fontSize: '0.85rem', color: '#7f1d1d', margin: 0 }}>
            Esta acción eliminará de forma permanente los registros de asistencia y ofrendas
            asociados a esta reunión. No se puede deshacer.
          </p>

          <div className="delete-reporte-info">
            <div>
              <strong>Fecha:</strong> {reporte.fecha_formateada || reporte.fecha || '—'}
            </div>
            <div>
              <strong>Tema:</strong> {reporte.tema || '—'}
            </div>
            <div>
              <strong>Asistencia:</strong> {reporte.asistencia || 0} personas
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
};
