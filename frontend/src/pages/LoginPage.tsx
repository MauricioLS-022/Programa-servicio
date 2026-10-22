import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { Icon } from '../components/ui/Icon';
import '../styles/login.css';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const { login, isLoggingIn } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { success } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as { from?: { pathname?: string } })?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (!username.trim() || !password.trim()) {
      setErrorMsg('Por favor completa todos los campos.');
      return;
    }

    try {
      const res = await login({ username: username.trim(), password: password.trim() });
      if (res.success && res.user) {
        success(`Bienvenido, ${res.user.nombre || res.user.username}`);
        navigate(from, { replace: true });
      } else {
        setErrorMsg(res.error || 'Credenciales incorrectas');
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message || 'Error al iniciar sesión');
      } else {
        setErrorMsg('Error de conexión con el servidor');
      }
    }
  };

  return (
    <div className="login-page-wrapper">
      {/* Botón Flotante para Alternar Modo Oscuro / Claro */}
      <button
        type="button"
        onClick={toggleTheme}
        className="theme-toggle-btn"
        id="themeToggleBtn"
        aria-label="Cambiar tema de color"
        title={`Alternar a modo ${theme === 'dark' ? 'claro' : 'oscuro'}`}
      >
        <Icon
          name={theme === 'dark' ? 'light_mode' : 'dark_mode'}
          size={22}
          className="text-vino dark:text-neutral-100"
        />
      </button>

      {/* Tarjeta Principal de Autenticación */}
      <main className="login-card">
        {/* Cabecera del Login */}
        <div className="brand-header">
          <div className="brand-logo-wrap">
            <img
              src="/logo3.webp"
              alt="Logotipo Vino Nuevo"
              className="brand-logo-img"
            />
          </div>
          <h1 className="brand-title">Vino Nuevo</h1>
          <p className="brand-subtitle">Ministerio Comunitario · Iniciar Sesión</p>
        </div>

        {/* Mensaje de Alerta / Error */}
        {errorMsg && (
          <div className="login-alert" role="alert">
            <Icon name="error" size={20} className="shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Formulario de Acceso */}
        <form onSubmit={handleSubmit} className="login-form" noValidate={false}>
          <div className="form-group">
            <label htmlFor="usuario" className="form-label">
              Usuario
            </label>
            <div className="input-wrapper">
              <Icon name="person" size={20} className="input-icon-left" />
              <input
                type="text"
                name="usuario"
                id="usuario"
                className="form-input"
                placeholder="Ingresa tu usuario"
                required
                autoComplete="username"
                autoFocus
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoggingIn}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="contrasena" className="form-label">
              Contraseña
            </label>
            <div className="input-wrapper">
              <Icon name="lock" size={20} className="input-icon-left" />
              <input
                type={showPassword ? 'text' : 'password'}
                name="contrasena"
                id="contrasena"
                className="form-input form-input-password"
                placeholder="••••••••"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoggingIn}
              />
              <button
                type="button"
                className="btn-toggle-password"
                id="btnTogglePassword"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                title={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                <Icon
                  name={showPassword ? 'visibility_off' : 'visibility'}
                  size={20}
                />
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn-login"
            id="btnSubmit"
            disabled={isLoggingIn}
          >
            <span>{isLoggingIn ? 'Accediendo...' : 'Ingresar al Sistema'}</span>
            <Icon
              name={isLoggingIn ? 'progress_activity' : 'arrow_forward'}
              size={20}
              className={`btn-icon ${isLoggingIn ? 'animate-spin' : ''}`}
            />
          </button>
        </form>

        <footer className="login-footer">
          <p>© {new Date().getFullYear()} Vino Nuevo · Sistema de Casas de Paz</p>
        </footer>
      </main>
    </div>
  );
};

export default LoginPage;
