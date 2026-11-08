import React, { useState, useMemo, useEffect } from 'react';
import { usePerfil } from '../hooks/usePerfil';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../context/ToastContext';
import { api, ApiError } from '../api/client';
import { Icon } from '../components/ui/Icon';
import '../styles/perfil.css';

export const PerfilPage: React.FC = () => {
  const { perfil, usuario, rol, isLoading, isError, refetch } = usePerfil();
  const { user, refetchUser } = useAuth();
  const { success, error: toastError } = useToast();

  // Estados Formulario Cambiar Usuario
  const [nuevoUsername, setNuevoUsername] = useState('');
  const [isUpdatingUsername, setIsUpdatingUsername] = useState(false);

  // Estados Formulario Cambiar Contraseña
  const [passwordActual, setPasswordActual] = useState('');
  const [passwordNueva, setPasswordNueva] = useState('');
  const [passwordConfirmar, setPasswordConfirmar] = useState('');
  const [showPassActual, setShowPassActual] = useState(false);
  const [showPassNueva, setShowPassNueva] = useState(false);
  const [showPassConfirmar, setShowPassConfirmar] = useState(false);
  const [isUpdatingPassword, setIsUpdatingPassword] = useState(false);

  // Sincronizar input de usuario cuando se cargan los datos
  useEffect(() => {
    if (perfil?.username || usuario || user?.username) {
      setNuevoUsername(perfil?.username || usuario || user?.username || '');
    }
  }, [perfil, usuario, user]);

  // Cálculo de fortaleza de contraseña
  const strength = useMemo(() => {
    if (!passwordNueva) return null;
    let score = 0;
    if (passwordNueva.length >= 6) score++;
    if (passwordNueva.length >= 10) score++;
    if (/[A-Z]/.test(passwordNueva)) score++;
    if (/[0-9]/.test(passwordNueva)) score++;
    if (/[^A-Za-z0-9]/.test(passwordNueva)) score++;

    const levels = [
      { label: 'Muy débil', color: '#ef4444', width: '20%' },
      { label: 'Débil', color: '#f97316', width: '40%' },
      { label: 'Regular', color: '#eab308', width: '60%' },
      { label: 'Buena', color: '#22c55e', width: '80%' },
      { label: 'Excelente', color: '#16a34a', width: '100%' },
    ];
    return levels[Math.min(score, 4)];
  }, [passwordNueva]);

  // Validación de coincidencia de contraseñas
  const passwordsMatch = useMemo(() => {
    if (!passwordConfirmar) return null;
    return passwordNueva === passwordConfirmar;
  }, [passwordNueva, passwordConfirmar]);

  const canSubmitPassword =
    passwordActual.length > 0 &&
    passwordNueva.length >= 6 &&
    passwordConfirmar.length >= 6 &&
    passwordsMatch === true &&
    !isUpdatingPassword;

  // Detección de dispositivo y navegador
  const deviceInfo = useMemo(() => {
    const ua = typeof navigator !== 'undefined' ? navigator.userAgent : '';
    let browser = 'Navegador Web';
    if (ua.includes('Firefox')) browser = 'Mozilla Firefox';
    else if (ua.includes('Edg')) browser = 'Microsoft Edge';
    else if (ua.includes('Chrome')) browser = 'Google Chrome';
    else if (ua.includes('Safari')) browser = 'Apple Safari';

    let os = 'Sistema';
    if (ua.includes('Win')) os = 'Windows';
    else if (ua.includes('Mac')) os = 'macOS';
    else if (ua.includes('Linux')) os = 'Linux';
    else if (ua.includes('Android')) os = 'Android';
    else if (ua.includes('iPhone') || ua.includes('iPad')) os = 'iOS';

    return {
      dispositivo: `${browser} en ${os}`,
    };
  }, []);

  // Formato del último inicio de sesión
  const ultimoAcceso = useMemo(() => {
    try {
      const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('ultimo_acceso_login') : null;
      const date = stored ? new Date(stored) : new Date();
      const now = new Date();
      const isToday =
        date.getDate() === now.getDate() &&
        date.getMonth() === now.getMonth() &&
        date.getFullYear() === now.getFullYear();

      const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      if (isToday) {
        return `Hoy, ${timeStr}`;
      }
      const day = date.getDate();
      const month = date.toLocaleDateString('es-ES', { month: 'short' });
      return `${day} ${month}, ${timeStr}`;
    } catch {
      return 'Sesión activa';
    }
  }, []);

  // Manejar actualización de nombre de usuario
  const handleSubmitUsername = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanUser = nuevoUsername.trim();
    if (cleanUser.length < 3 || cleanUser.length > 30) {
      toastError('El usuario debe tener entre 3 y 30 caracteres.');
      return;
    }

    try {
      setIsUpdatingUsername(true);
      const res = await api.post<{ success: boolean; message: string; username: string }>(
        '/perfil/username',
        { nuevo_username: cleanUser }
      );
      if (res.success) {
        success(res.message || 'Nombre de usuario actualizado con éxito.');
        await refetch();
        if (refetchUser) await refetchUser();
      }
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Error al actualizar nombre de usuario.';
      toastError(msg);
    } finally {
      setIsUpdatingUsername(false);
    }
  };

  // Manejar actualización de contraseña
  const handleSubmitPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmitPassword) return;

    try {
      setIsUpdatingPassword(true);
      const res = await api.post<{ success: boolean; message: string }>('/perfil/password', {
        password_actual: passwordActual,
        password_nueva: passwordNueva,
        password_confirmar: passwordConfirmar,
      });

      if (res.success) {
        success(res.message || 'Contraseña actualizada correctamente.');
        setPasswordActual('');
        setPasswordNueva('');
        setPasswordConfirmar('');
      }
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Error al cambiar la contraseña.';
      toastError(msg);
    } finally {
      setIsUpdatingPassword(false);
    }
  };

  if (isLoading) {
    return (
      <div className="perfil-page flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <Icon name="progress_activity" size={40} className="text-vino icon-spin" />
        <p className="text-sm font-medium text-text-muted">Cargando perfil ministerial...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="perfil-page">
        <div className="perfil-card text-center p-8">
          <p className="text-red-600 font-semibold mb-4">
            No se pudo cargar la información del perfil ministerial.
          </p>
          <button
            onClick={() => refetch()}
            className="btn-perfil-primary inline-flex items-center gap-2"
          >
            <Icon name="refresh" size={16} />
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  const effectiveRol = rol || perfil?.tipo_usuario || user?.rol || 'lider_cdp';
  const nombreCompleto =
    `${perfil?.nombre || user?.nombre || ''} ${perfil?.apellido || user?.apellido || ''}`.trim() ||
    usuario ||
    'Usuario';
  const displayUsername = perfil?.username || usuario || user?.username || '';
  const iniciales = (
    (perfil?.nombre || user?.nombre || usuario || 'U')[0] +
    (perfil?.apellido || user?.apellido || '')[0]
  ).toUpperCase();

  const rolLabelMap: Record<string, string> = {
    admin: 'Administrador',
    supervisor: 'Supervisor',
    lider_cdp: 'Líder Casa de Paz',
    cdp: 'Líder Casa de Paz',
  };

  const roleIconSrc =
    effectiveRol === 'admin'
      ? '/iconos/administrador.webp'
      : effectiveRol === 'supervisor'
      ? '/iconos/supervisor.webp'
      : '/iconos/casa_de_paz.webp';

  const roleBadgeClass =
    effectiveRol === 'admin'
      ? 'role-admin'
      : effectiveRol === 'supervisor'
      ? 'role-supervisor'
      : 'role-cdp';

  return (
    <div className="perfil-page">
      {/* Cabecera */}
      <div className="perfil-page-header">
        <div className="perfil-page-header-info">
          <h1 className="perfil-page-title">Mi Perfil</h1>
          <p className="perfil-page-subtitle">
            Gestiona tu información personal, credenciales y seguridad de acceso
          </p>
        </div>
      </div>

      <div className="perfil-layout">
        {/* Columna Izquierda: Ficha de Identidad Ministerial */}
        <div className="perfil-column-left">
          <section className="perfil-card perfil-identity-card" aria-label="Información personal">
            {/* Visual del Avatar con Gradiente Vinotinto Canónico */}
            <div className="identity-visual">
              <div className="avatar-large" aria-hidden="true">
                <span className="avatar-initials">{iniciales}</span>
              </div>
              <div className="avatar-role-icon" title={rolLabelMap[effectiveRol] || effectiveRol}>
                <img
                  src={roleIconSrc}
                  alt={rolLabelMap[effectiveRol] || effectiveRol}
                  className="role-icon-img"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            </div>

            {/* Nombre completo */}
            <h2 className="identity-name">{nombreCompleto}</h2>

            {/* Badge de Rol oficial */}
            <span className={`identity-role-badge ${roleBadgeClass}`}>
              {effectiveRol === 'admin' ? (
                <Icon name="shield_person" size={14} />
              ) : effectiveRol === 'supervisor' ? (
                <Icon name="verified_user" size={14} />
              ) : (
                <Icon name="home" size={14} />
              )}
              {rolLabelMap[effectiveRol] || effectiveRol}
            </span>

            {/* Campos de Identidad Ministerial estructurados y limpios */}
            <div className="identity-fields">
              {/* 1. Nombre de usuario */}
              <div className="identity-field">
                <Icon name="person" size={16} className="field-icon" />
                <div className="field-content">
                  <span className="field-label">Nombre de usuario</span>
                  <span className="field-value">{displayUsername}</span>
                </div>
              </div>

              {/* 2. Asignación Territorial según Rol */}
              {effectiveRol === 'admin' && (
                <div className="identity-field">
                  <Icon name="public" size={16} className="field-icon" />
                  <div className="field-content">
                    <span className="field-label">Alcance Administrativo</span>
                    <span className="field-value">
                      <span className="assignment-badge badge-admin">
                        <Icon name="public" size={14} />
                        Acceso Global
                      </span>
                    </span>
                  </div>
                </div>
              )}

              {effectiveRol === 'supervisor' && (
                <div className="identity-field">
                  <Icon name="hub" size={16} className="field-icon" />
                  <div className="field-content">
                    <span className="field-label">Red Asignada</span>
                    <span className="field-value">
                      {perfil?.red_nombre || perfil?.red_asignada ? (
                        <span className="assignment-badge badge-red">
                          <Icon name="hub" size={14} />
                          {perfil.red_nombre || perfil.red_asignada}
                        </span>
                      ) : (
                        <span className="text-unassigned">Sin red asignada</span>
                      )}
                    </span>
                  </div>
                </div>
              )}

              {effectiveRol !== 'admin' && effectiveRol !== 'supervisor' && (
                <>
                  <div className="identity-field">
                    <Icon name="home" size={16} className="field-icon" />
                    <div className="field-content">
                      <span className="field-label">Casa de Paz Asignada</span>
                      <span className="field-value">
                        {perfil?.cdp_codigo || perfil?.cdp_asignada ? (
                          <span className="assignment-badge badge-cdp">
                            <Icon name="home" size={14} />
                            {perfil.cdp_asignada || `Casa "${perfil.cdp_codigo}"`}
                          </span>
                        ) : (
                          <span className="text-unassigned">Sin Casa de Paz asignada</span>
                        )}
                      </span>
                    </div>
                  </div>

                  {(perfil?.red_nombre || perfil?.red_asignada) && (
                    <div className="identity-field">
                      <Icon name="hub" size={16} className="field-icon" />
                      <div className="field-content">
                        <span className="field-label">Red Ministerial</span>
                        <span className="field-value">
                          <span className="assignment-badge badge-red">
                            <Icon name="hub" size={14} />
                            {perfil.red_nombre || perfil.red_asignada}
                          </span>
                        </span>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* 3. Dispositivo de acceso */}
              <div className="identity-field">
                <Icon name="laptop" size={16} className="field-icon" />
                <div className="field-content">
                  <span className="field-label">Dispositivo</span>
                  <span className="field-value">{deviceInfo.dispositivo}</span>
                </div>
              </div>

              {/* 4. Último inicio de sesión */}
              <div className="identity-field">
                <Icon name="schedule" size={16} className="field-icon" />
                <div className="field-content">
                  <span className="field-label">Último inicio de sesión</span>
                  <span className="field-value">{ultimoAcceso}</span>
                </div>
              </div>

              {/* 5. Estado de la cuenta */}
              <div className="identity-field">
                <Icon name="check_circle" size={16} className="field-icon" />
                <div className="field-content">
                  <span className="field-label">Estado</span>
                  <span className="field-value status-active-text">
                    <span className="status-dot active" /> Activo
                  </span>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* Columna Derecha: Tarjetas de Acción de Seguridad */}
        <div className="perfil-column-right">
          {/* Tarjeta: Cambiar Usuario */}
          <section className="perfil-card" aria-label="Cambiar usuario">
            <div className="perfil-card-header">
              <div className="perfil-card-header-icon">
                <Icon name="person" size={20} />
              </div>
              <div>
                <h3 className="perfil-card-title">Cambiar Usuario</h3>
                <p className="perfil-card-subtitle">Actualiza tu nombre de acceso al sistema</p>
              </div>
            </div>
            <form onSubmit={handleSubmitUsername} className="perfil-form">
              <div className="perfil-input-group">
                <label htmlFor="nuevo_username">Nuevo nombre de usuario</label>
                <div className="input-with-icon">
                  <Icon name="person" size={16} className="input-icon" />
                  <input
                    type="text"
                    id="nuevo_username"
                    name="nuevo_username"
                    value={nuevoUsername}
                    onChange={(e) => setNuevoUsername(e.target.value)}
                    minLength={3}
                    maxLength={30}
                    required
                    placeholder="Escribe tu nuevo usuario..."
                  />
                </div>
                <span className="input-hint">Mínimo 3 caracteres, máximo 30. Debe ser único.</span>
              </div>
              <div className="perfil-form-actions">
                <button
                  type="submit"
                  disabled={isUpdatingUsername || !nuevoUsername.trim()}
                  className="btn-perfil-primary"
                >
                  {isUpdatingUsername ? (
                    <Icon name="progress_activity" size={16} className="icon-spin" />
                  ) : (
                    <Icon name="save" size={16} />
                  )}
                  Actualizar Usuario
                </button>
              </div>
            </form>
          </section>

          {/* Tarjeta: Cambiar Contraseña */}
          <section className="perfil-card" aria-label="Cambiar contraseña">
            <div className="perfil-card-header">
              <div className="perfil-card-header-icon danger">
                <Icon name="lock" size={20} />
              </div>
              <div>
                <h3 className="perfil-card-title">Cambiar Contraseña</h3>
                <p className="perfil-card-subtitle">Asegura tu cuenta con una nueva contraseña</p>
              </div>
            </div>
            <form onSubmit={handleSubmitPassword} className="perfil-form">
              <div className="perfil-input-group">
                <label htmlFor="password_actual">Contraseña actual</label>
                <div className="input-with-icon">
                  <Icon name="lock" size={16} className="input-icon" />
                  <input
                    type={showPassActual ? 'text' : 'password'}
                    id="password_actual"
                    name="password_actual"
                    value={passwordActual}
                    onChange={(e) => setPasswordActual(e.target.value)}
                    required
                    placeholder="Tu contraseña actual"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassActual(!showPassActual)}
                    className="btn-toggle-password"
                    aria-label={showPassActual ? 'Ocultar contraseña' : 'Ver contraseña'}
                  >
                    {showPassActual ? <Icon name="visibility_off" size={16} /> : <Icon name="visibility" size={16} />}
                  </button>
                </div>
              </div>

              <div className="perfil-input-group">
                <label htmlFor="password_nueva">Nueva contraseña</label>
                <div className="input-with-icon">
                  <Icon name="key" size={16} className="input-icon" />
                  <input
                    type={showPassNueva ? 'text' : 'password'}
                    id="password_nueva"
                    name="password_nueva"
                    value={passwordNueva}
                    onChange={(e) => setPasswordNueva(e.target.value)}
                    required
                    minLength={6}
                    placeholder="Mínimo 6 caracteres"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassNueva(!showPassNueva)}
                    className="btn-toggle-password"
                    aria-label={showPassNueva ? 'Ocultar contraseña' : 'Ver contraseña'}
                  >
                    {showPassNueva ? <Icon name="visibility_off" size={16} /> : <Icon name="visibility" size={16} />}
                  </button>
                </div>

                {/* Barra de fortaleza interactiva */}
                {strength && (
                  <div className="strength-bar-container">
                    <div className="strength-bar">
                      <div
                        className="strength-fill"
                        style={{
                          width: strength.width,
                          backgroundColor: strength.color,
                        }}
                      />
                    </div>
                    <span className="strength-text" style={{ color: strength.color }}>
                      Fortaleza: {strength.label}
                    </span>
                  </div>
                )}
              </div>

              <div className="perfil-input-group">
                <label htmlFor="password_confirmar">Confirmar nueva contraseña</label>
                <div className="input-with-icon">
                  <Icon name="key" size={16} className="input-icon" />
                  <input
                    type={showPassConfirmar ? 'text' : 'password'}
                    id="password_confirmar"
                    name="password_confirmar"
                    value={passwordConfirmar}
                    onChange={(e) => setPasswordConfirmar(e.target.value)}
                    required
                    minLength={6}
                    placeholder="Repite la nueva contraseña"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassConfirmar(!showPassConfirmar)}
                    className="btn-toggle-password"
                    aria-label={showPassConfirmar ? 'Ocultar contraseña' : 'Ver contraseña'}
                  >
                    {showPassConfirmar ? <Icon name="visibility_off" size={16} /> : <Icon name="visibility" size={16} />}
                  </button>
                </div>

                {passwordsMatch !== null && (
                  <span
                    className={`match-indicator ${
                      passwordsMatch ? 'match-success' : 'match-error'
                    }`}
                  >
                    {passwordsMatch
                      ? '✓ Las contraseñas coinciden'
                      : '✗ Las contraseñas no coinciden'}
                  </span>
                )}
              </div>

              <div className="perfil-form-actions">
                <button
                  type="submit"
                  disabled={!canSubmitPassword}
                  className="btn-perfil-danger"
                >
                  {isUpdatingPassword ? (
                    <Icon name="progress_activity" size={16} className="icon-spin" />
                  ) : (
                    <Icon name="lock" size={16} />
                  )}
                  Cambiar Contraseña
                </button>
              </div>
            </form>
          </section>
        </div>
      </div>
    </div>
  );
};
