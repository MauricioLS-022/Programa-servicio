import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Icon } from '../ui/Icon';
import type { Lider, LiderInput } from '../../types/estructura';

export interface LiderFormCasaOpcion {
  id: number;
  codigo: string;
  anfitrion?: string;
  direccion?: string;
  red_id?: number;
  red_nombre?: string;
}

export interface LiderFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  lider?: Lider | null;
  casasDePaz: LiderFormCasaOpcion[];
  supervisorRedId?: number | string | null;
  onSave: (data: LiderInput) => Promise<void>;
  isSaving?: boolean;
}

export const LiderFormModal: React.FC<LiderFormModalProps> = ({
  isOpen,
  onClose,
  lider,
  casasDePaz,
  supervisorRedId,
  onSave,
  isSaving = false,
}) => {
  const isEdit = Boolean(lider);

  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [telefono, setTelefono] = useState('');
  const [rol, setRol] = useState<'Lider' | 'Sublider'>('Lider');
  const [cdpId, setCdpId] = useState<string>('');
  const [isActive, setIsActive] = useState('1');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  // Aislamiento territorial de supervisor: sólo Casas de Paz de su red
  const casasDisponibles = casasDePaz.filter((c) => {
    if (!supervisorRedId) return true;
    return String(c.red_id) === String(supervisorRedId);
  });

  useEffect(() => {
    if (lider) {
      setNombre(lider.nombre || '');
      setApellido(lider.apellido || '');
      setTelefono(lider.telefono || '');
      const rolRaw = lider.rol?.toLowerCase() || '';
      setRol(rolRaw.includes('sub') ? 'Sublider' : 'Lider');
      setCdpId(lider.cdp_id ? String(lider.cdp_id) : '');
      setIsActive(lider.is_active ? '1' : '0');
    } else {
      setNombre('');
      setApellido('');
      setTelefono('');
      setRol('Lider');
      setCdpId(casasDisponibles.length > 0 ? String(casasDisponibles[0].id) : '');
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
    if (!cdpId) {
      setErrorLocal('Debes seleccionar una Casa de Paz para vincular al líder.');
      return;
    }

    setErrorLocal(null);

    try {
      await onSave({
        nombre: nombre.trim(),
        apellido: apellido.trim(),
        telefono: telefono.trim(),
        rol,
        cdp_id: Number(cdpId),
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

  const cdpOptions = [
    { value: '', label: '-- Selecciona una Casa de Paz --' },
    ...casasDisponibles.map((c) => ({
      value: String(c.id),
      label: `${c.codigo}${c.direccion ? ` - ${c.direccion}` : ''}${c.red_nombre ? ` (${c.red_nombre})` : ''}`,
    })),
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? `Editar Líder: ${lider?.nombre} ${lider?.apellido}` : 'Registrar Nuevo Líder'}
      description="Registra o actualiza los datos del equipo de liderazgo ministerial y vincúlalo a su Casa de Paz."
      headerIcon={
        isEdit ? (
          <Icon name="how_to_reg" size={20} className="text-vino dark:text-vino-light" />
        ) : (
          <Icon name="person_add" size={20} className="text-vino dark:text-vino-light" />
        )
      }
      maxWidth="md"
      footer={
        <div className="flex items-center justify-end gap-3 w-full">
          <button type="button" className="btn-modal btn-modal-cancel" onClick={onClose} disabled={isSaving}>
            Cancelar
          </button>
          <button type="submit" form="lider-form-modal" className="btn-modal btn-modal-save" disabled={isSaving}>
            <Icon name="save" size={16} />
            <span>{isSaving ? 'Guardando...' : isEdit ? 'Guardar Cambios' : 'Registrar Líder'}</span>
          </button>
        </div>
      }
    >
      <form id="lider-form-modal" onSubmit={handleSubmit} className="space-y-4">
        {errorLocal && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 text-xs text-red-700 dark:text-red-300 flex items-center gap-2">
            <Icon name="warning" size={16} className="shrink-0 text-red-600 dark:text-red-400" />
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
            placeholder="Ej: Méndez"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Teléfono / WhatsApp"
            id="lider-telefono"
            placeholder="Ej: +58 412 1234567"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            required
          />
          <Select
            label="Rol Asignado"
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

        <div>
          <Select
            label="Casa de Paz a la que pertenece"
            id="lider-cdp"
            value={cdpId}
            onChange={(e) => setCdpId(e.target.value)}
            options={cdpOptions}
            required
          />
          {supervisorRedId && (
            <p className="text-[11px] text-text-muted dark:text-neutral-400 mt-1">
              Restringido a Casas de Paz de tu Red asignada.
            </p>
          )}
        </div>

        {isEdit && (
          <Select
            label="Estado del Líder"
            id="lider-active"
            value={isActive}
            onChange={(e) => setIsActive(e.target.value)}
            options={[
              { value: '1', label: 'Activo' },
              { value: '0', label: 'En pausa / Inactivo' },
            ]}
            required
          />
        )}
      </form>
    </Modal>
  );
};


