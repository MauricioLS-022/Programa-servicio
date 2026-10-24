import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { UserPlus, UserCheck, AlertTriangle } from 'lucide-react';
import type { LiderInput } from '../../types/estructura';

export interface LiderModalProps {
  isOpen: boolean;
  onClose: () => void;
  lider?: {
    id: number;
    nombre_completo?: string;
    nombre?: string;
    apellido?: string;
    rol?: string;
    telefono?: string;
    is_active?: number | boolean;
  } | null;
  cdpId: number | string;
  cdpCodigo?: string;
  onSave: (data: LiderInput) => Promise<void>;
  isSaving?: boolean;
}

export const LiderModal: React.FC<LiderModalProps> = ({
  isOpen,
  onClose,
  lider,
  cdpId,
  cdpCodigo,
  onSave,
  isSaving = false,
}) => {
  const isEdit = Boolean(lider);

  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [telefono, setTelefono] = useState('');
  const [rol, setRol] = useState<'Lider' | 'Sublider'>('Lider');
  const [isActive, setIsActive] = useState('1');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  useEffect(() => {
    if (lider) {
      // Si tenemos nombre separado o nombre_completo
      if (lider.nombre) {
        setNombre(lider.nombre);
        setApellido(lider.apellido || '');
      } else if (lider.nombre_completo) {
        const parts = lider.nombre_completo.trim().split(' ');
        setNombre(parts[0] || '');
        setApellido(parts.slice(1).join(' ') || '');
      }
      setTelefono(lider.telefono || '');
      const rolRaw = lider.rol?.toLowerCase() || '';
      setRol(rolRaw.includes('sub') ? 'Sublider' : 'Lider');
      setIsActive(lider.is_active !== undefined ? (lider.is_active ? '1' : '0') : '1');
    } else {
      setNombre('');
      setApellido('');
      setTelefono('');
      setRol('Lider');
      setIsActive('1');
    }
    setErrorLocal(null);
  }, [lider, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!nombre.trim() || nombre.trim().length < 2) {
      setErrorLocal('El nombre debe contener al menos 2 caracteres.');
      return;
    }

    if (!apellido.trim() || apellido.trim().length < 2) {
      setErrorLocal('El apellido debe contener al menos 2 caracteres.');
      return;
    }

    const cleanPhone = telefono.replace(/[^0-9]/g, '');
    if (!telefono.trim() || cleanPhone.length < 8) {
      setErrorLocal('Ingresa un teléfono válido de al menos 8 dígitos (ej: +58 412 1234567).');
      return;
    }

    setErrorLocal(null);

    try {
      await onSave({
        nombre: nombre.trim(),
        apellido: apellido.trim(),
        telefono: telefono.trim(),
        rol,
        cdp_id: cdpId,
        is_active: isActive === '1',
      });
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorLocal(err.message);
      } else {
        setErrorLocal('Error al registrar o actualizar el líder.');
      }
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? `Editar Líder: ${lider?.nombre_completo || nombre}` : 'Añadir Líder a Casa de Paz'}
      description={cdpCodigo ? `Asignación a Casa de Paz ${cdpCodigo}` : undefined}
      headerIcon={
        isEdit ? (
          <UserCheck className="w-5 h-5 text-vino dark:text-vino-light" />
        ) : (
          <UserPlus className="w-5 h-5 text-vino dark:text-vino-light" />
        )
      }
      maxWidth="md"
      footer={
        <div className="flex items-center justify-end gap-3 w-full">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isSaving}>
            Cancelar
          </Button>
          <Button type="submit" form="lider-modal-form" variant="primary" disabled={isSaving}>
            {isSaving ? 'Guardando...' : isEdit ? 'Guardar Cambios' : 'Registrar Líder'}
          </Button>
        </div>
      }
    >
      <form id="lider-modal-form" onSubmit={handleSubmit} className="space-y-4">
        {errorLocal && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 text-xs text-red-700 dark:text-red-300 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-red-600 dark:text-red-400" />
            <span>{errorLocal}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Nombre"
            id="lider-nombre"
            placeholder="Ej: Carlos"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            autoFocus
          />
          <Input
            label="Apellido"
            id="lider-apellido"
            placeholder="Ej: Mendoza"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Teléfono Móvil / WhatsApp"
            id="lider-telefono"
            placeholder="Ej: +58 412 1234567"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            required
          />
          <Select
            label="Rol Ministerial"
            id="lider-rol"
            value={rol}
            onChange={(e) => setRol(e.target.value as 'Lider' | 'Sublider')}
            options={[
              { value: 'Lider', label: 'Líder Principal' },
              { value: 'Sublider', label: 'Sublíder' },
            ]}
            required
          />
        </div>

        {isEdit && (
          <Select
            label="Estado del Líder"
            id="lider-status"
            value={isActive}
            onChange={(e) => setIsActive(e.target.value)}
            options={[
              { value: '1', label: 'Activo / Asignado' },
              { value: '0', label: 'Inactivo / Pausado' },
            ]}
          />
        )}
      </form>
    </Modal>
  );
};
