import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Edit, PauseCircle, PlayCircle, Trash2, X, Network } from 'lucide-react';
import type { Red } from '../../types/estructura';

interface RedBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  red?: Red | null;
  isAdmin?: boolean;
  onEdit: (red: Red) => void;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}

export const RedBottomSheet: React.FC<RedBottomSheetProps> = ({
  isOpen,
  onClose,
  red,
  isAdmin = false,
  onEdit,
  onToggle,
  onDelete,
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen || !red) return null;

  const cleanName = red.nombre.replace(/^Red\s+/i, '').trim();

  return createPortal(
    <div className="bottom-sheet-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div
        className="bottom-sheet-container"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bottom-sheet-handle" />

        <div className="bottom-sheet-header">
          <div className="bottom-sheet-title-row">
            <div className="bottom-sheet-icon">
              <Network className="w-5 h-5" />
            </div>
            <div>
              <h3 className="bottom-sheet-title">Red {cleanName}</h3>
              <p className="bottom-sheet-subtitle">
                Supervisor: {red.supervisor_nombre || red.supervisor || 'Sin asignar'}
              </p>
            </div>
          </div>
          <button
            type="button"
            className="bottom-sheet-close"
            onClick={onClose}
            aria-label="Cerrar opciones"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="bottom-sheet-actions">
          <button
            type="button"
            className="bottom-sheet-action-btn"
            onClick={() => {
              onClose();
              onEdit(red);
            }}
          >
            <Edit className="w-5 h-5" />
            <span>Editar red</span>
          </button>

          <button
            type="button"
            className={`bottom-sheet-action-btn ${red.is_active ? 'action-warning' : 'action-success'}`}
            onClick={() => {
              onClose();
              onToggle(red.id);
            }}
          >
            {red.is_active ? (
              <>
                <PauseCircle className="w-5 h-5" />
                <span>Poner en pausa</span>
              </>
            ) : (
              <>
                <PlayCircle className="w-5 h-5" />
                <span>Reactivar red</span>
              </>
            )}
          </button>

          {isAdmin && (
            <button
              type="button"
              className="bottom-sheet-action-btn action-danger"
              onClick={() => {
                onClose();
                onDelete(red.id);
              }}
            >
              <Trash2 className="w-5 h-5" />
              <span>Eliminar red</span>
            </button>
          )}

          <button
            type="button"
            className="bottom-sheet-cancel-btn"
            onClick={onClose}
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};
