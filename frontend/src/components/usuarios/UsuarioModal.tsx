import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Icon } from '../ui/Icon';
import { useUsuarioOpcionesAsignacion } from '../../hooks/useUsuarios';
import type { Usuario, UsuarioInput } from '../../types/usuario';

export interface UsuarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  usuario?: Usuario | null;
  onSave: (data: UsuarioInput) => Promise<void>;
  isSaving?: boolean;
}

export const UsuarioModal: React.FC<UsuarioModalProps> = ({
  isOpen,
  onClose,
  usuario,
  onSave,
  isSaving = false,
}) => {
  const isEdit = Boolean(usuario);
  const { redes, casasDePaz, isLoading: isLoadingOpciones } = useUsuarioOpcionesAsignacion(usuario?.id);

  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rol, setRol] = useState<'admin' | 'supervisor' | 'lider_cdp'>('lider_cdp');
  const [redId, setRedId] = useState<string>('');
  const [cdpId, setCdpId] = useState<string>('');
  const [isActive, setIsActive] = useState<string>('1');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  useEffect(() => {
    if (usuario) {
      setNombre(usuario.nombre || '');
      setApellido(usuario.apellido || '');
      setUsername(usuario.username || '');
      setPassword(''); // Dejar en blanco en edición
      const rawRol = (usuario.tipo_usuario || usuario.rol || 'lider_cdp') as string;
      setRol(rawRol === 'cdp' ? 'lider_cdp' : (rawRol as 'admin' | 'supervisor' | 'lider_cdp'));
      setRedId(usuario.red_id ? String(usuario.red_id) : '');
      setCdpId(usuario.cdp_id ? String(usuario.cdp_id) : '');
      setIsActive(usuario.is_active ? '1' : '0');
    } else {
      setNombre('');
      setApellido('');
      setUsername('');
      setPassword('');
      setRol('lider_cdp');
      setRedId('');
      setCdpId('');
      setIsActive('1');
    }
    setErrorLocal(null);
  }, [usuario, isOpen]);

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
    if (!username.trim() || username.trim().length < 3) {
      setErrorLocal('El nombre de usuario debe tener al menos 3 caracteres.');
      return;
    }

    // Validación de contraseña en creación
    if (!isEdit) {
      if (!password || password.length < 8) {
        setErrorLocal('La contraseña debe tener al menos 8 caracteres.');
        return;
      }
      if (!/[A-Z]/.test(password) || !/[0-9]/.test(password)) {
        setErrorLocal('La contraseña debe contener al menos una mayúscula y un número.');
        return;
      }
    } else if (password) {
      // Si se está cambiando en edición
      if (password.length < 8 || !/[A-Z]/.test(password) || !/[0-9]/.test(password)) {
        setErrorLocal('La nueva contraseña debe tener al menos 8 caracteres, una mayúscula y un número.');
        return;
      }
    }

    setErrorLocal(null);

    try {
      const payload: UsuarioInput = {
        nombre: nombre.trim(),
        apellido: apellido.trim(),
        username: username.trim(),
        tipo_usuario: rol,
        red_id: rol === 'supervisor' && redId ? Number(redId) : null,
        cdp_id: rol === 'lider_cdp' && cdpId ? Number(cdpId) : null,
        is_active: isActive === '1',
      };

      if (password) {
        payload.password = password;
      }

      await onSave(payload);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorLocal(err.message);
      } else {
        setErrorLocal('Error al registrar o actualizar el usuario.');
      }
    }
  };

  const redOptions = [
    { value: '', label: '-- Sin asignar por ahora --' },
    ...redes.map((r) => ({ value: String(r.id), label: r.nombre })),
  ];

  const cdpOptions = [
    { value: '', label: '-- Sin asignar por ahora --' },
    ...casasDePaz.map((c) => ({
      value: String(c.id),
      label: `${c.codigo}${c.direccion ? ` · ${c.direccion}` : ''}${c.red_nombre ? ` (${c.red_nombre})` : ''}`,
    })),
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? `Editar Usuario: @${usuario?.username}` : 'Registrar Nuevo Usuario'}
      description="Configura los permisos y la asignación ministerial dentro del sistema Vino Nuevo."
      headerIcon={
        isEdit ? (
          <Icon name="how_to_reg" size={20} className="text-vino dark:text-vino-light" />
        ) : (
          <Icon name="person_add" size={20} className="text-vino dark:text-vino-light" />
        )
      }
      maxWidth="lg"
      footer={
        <div className="flex items-center justify-end gap-3 w-full">
          <button type="button" className="btn-modal btn-modal-cancel" onClick={onClose} disabled={isSaving}>
            Cancelar
          </button>
          <button type="submit" form="usuario-modal-form" className="btn-modal btn-modal-save" disabled={isSaving}>
            <Icon name="save" size={16} />
            <span>{isSaving ? 'Guardando...' : isEdit ? 'Guardar Cambios' : 'Crear Usuario'}</span>
          </button>
        </div>
      }
    >
      <form id="usuario-modal-form" onSubmit={handleSubmit} className="space-y-4">
        {errorLocal && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 text-xs text-red-700 dark:text-red-300 flex items-center gap-2">
            <Icon name="warning" size={16} className="shrink-0 text-red-600 dark:text-red-400" />
            <span>{errorLocal}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Nombre"
            id="usr-nombre"
            placeholder="Ej: Carlos"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            autoFocus
          />
          <Input
            label="Apellido"
            id="usr-apellido"
            placeholder="Ej: Mendoza"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Nombre de Usuario"
            id="usr-username"
            placeholder="Ej: cmendoza"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <Select
            label="Rol del Usuario"
            id="usr-rol"
            value={rol}
            onChange={(e) => setRol(e.target.value as 'admin' | 'supervisor' | 'lider_cdp')}
            options={[
              { value: 'admin', label: 'Administrador' },
              { value: 'supervisor', label: 'Supervisor' },
              { value: 'lider_cdp', label: 'Líder de Casa de Paz' },
            ]}
            required
          />
        </div>

        {/* Asignación condicional según rol */}
        {rol === 'supervisor' && (
          <div>
            <Select
              label="Asignar Red Ministerial"
              id="usr-red"
              value={redId}
              onChange={(e) => setRedId(e.target.value)}
              options={redOptions}
              disabled={isLoadingOpciones}
            />
            <p className="text-[11px] text-text-muted dark:text-neutral-400 mt-1">
              Redes que actualmente no tienen supervisor asignado.{' '}
              {usuario?.red_nombre && (
                <>
                  (Actualmente asignado a: <strong>{usuario.red_nombre}</strong>)
                </>
              )}
            </p>
          </div>
        )}

        {rol === 'lider_cdp' && (
          <div>
            <Select
              label="Asignar Casa de Paz"
              id="usr-cdp"
              value={cdpId}
              onChange={(e) => setCdpId(e.target.value)}
              options={cdpOptions}
              disabled={isLoadingOpciones}
            />
            <p className="text-[11px] text-text-muted dark:text-neutral-400 mt-1">
              Casas de Paz sin usuario asignado.{' '}
              {usuario?.cdp_codigo && (
                <>
                  (Actualmente asignado a: <strong>{usuario.cdp_codigo}</strong>)
                </>
              )}
            </p>
          </div>
        )}

        <div className={`grid grid-cols-1 ${isEdit ? 'sm:grid-cols-2' : ''} gap-4`}>
          <div>
            <Input
              label={isEdit ? 'Contraseña (opcional)' : 'Contraseña'}
              id="usr-password"
              type="password"
              placeholder={isEdit ? 'Dejar en blanco para conservar actual' : 'Mínimo 8 caracteres'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required={!isEdit}
            />
            <p className="text-[11px] text-text-muted dark:text-neutral-400 mt-1">
              Mínimo 8 caracteres, al menos una mayúscula y un número.
            </p>
          </div>

          {isEdit && (
            <Select
              label="Estado de la Cuenta"
              id="usr-active"
              value={isActive}
              onChange={(e) => setIsActive(e.target.value)}
              options={[
                { value: '1', label: 'Activo' },
                { value: '0', label: 'En pausa / Inactivo' },
              ]}
              required
            />
          )}
        </div>
      </form>
    </Modal>
  );
};


