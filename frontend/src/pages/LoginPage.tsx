import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth, useAuthConfig } from '../hooks/useAuth';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { Icon } from '../components/ui/Icon';
import { ApiError } from '../api/client';
import '../styles/login.css';

interface GrecaptchaClient {
  ready: (cb: () => void) => void;
  execute: (siteKey: string, options: { action: string }) => Promise<string>;
  enterprise?: {
    ready: (cb: () => void) => void;
    execute: (siteKey: string, options: { action: string }) => Promise<string>;
  };
}

export const LoginPage: React.FC = () => {
  useDocumentTitle('Iniciar Sesión — Vino Nuevo', { override: true });

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [isCaptchaExecuting, setIsCaptchaExecuting] = useState(false);

  const { login, isLoggingIn } = useAuth();
  const { data: authConfig } = useAuthConfig();
  const { theme, toggleTheme } = useTheme();
  const { success } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as { from?: { pathname?: string } })?.from?.pathname || '/dashboard';

  const siteKey = authConfig?.siteKey || (import.meta.env?.VITE_RECAPTCHA_SITE_KEY as string | undefined) || '';
  const isDev = Boolean(authConfig?.isDev);

  // Inyección dinámica de Google reCAPTCHA v3 y control de visibilidad del badge (solo activo en login)
  useEffect(() => {
    const setBadgeVisibility = (visible: boolean) => {
      const badge = document.querySelector('.grecaptcha-badge') as HTMLElement | null;
      if (badge) {
        badge.style.visibility = visible ? 'visible' : 'hidden';
        badge.style.opacity = visible ? '1' : '0';
        badge.style.pointerEvents = visible ? 'auto' : 'none';
      }
    };

    if (siteKey) {
      const scriptId = 'google-recaptcha-v3-script';
      if (!document.getElementById(scriptId)) {
        const script = document.createElement('script');
        script.id = scriptId;
        script.src = `https://www.google.com/recaptcha/api.js?render=${encodeURIComponent(siteKey)}`;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
      }

      // Google inyecta el badge asíncronamente; nos aseguramos de hacerlo visible en login
      setBadgeVisibility(true);
      const interval = setInterval(() => setBadgeVisibility(true), 300);
      const timeout = setTimeout(() => clearInterval(interval), 4000);

      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
        setBadgeVisibility(false);
      };
    }

    return () => {
      setBadgeVisibility(false);
    };
  }, [siteKey]);

  // Captura de token con temporizador defensivo (4s) y detección de adblockers
  const getRecaptchaToken = async (key: string): Promise<string> => {
    if (!key) return '';

    const grecaptcha = (window as unknown as { grecaptcha?: GrecaptchaClient }).grecaptcha;

    if (!grecaptcha) {
      throw new Error(
        'No se pudo cargar la verificación de seguridad (reCAPTCHA). Si tienes activo un bloqueador de anuncios o extensiones de privacidad, desactívalo temporalmente e inténtalo de nuevo.'
      );
    }

    const client = grecaptcha.enterprise && typeof grecaptcha.enterprise.execute === 'function'
      ? grecaptcha.enterprise
      : grecaptcha;

    return new Promise((resolve, reject) => {
      let hasCompleted = false;

      const timeoutId = setTimeout(() => {
        if (!hasCompleted) {
          hasCompleted = true;
          reject(
            new Error(
              'La verificación de seguridad tardó demasiado. Por favor, verifica tu conexión a internet e inténtalo de nuevo.'
            )
          );
        }
      }, 4000);

      client.ready(() => {
        try {
          client
            .execute(key, { action: 'login' })
            .then((token) => {
              if (hasCompleted) return;
              hasCompleted = true;
              clearTimeout(timeoutId);
              resolve(token);
            })
            .catch((err: unknown) => {
              if (hasCompleted) return;
              hasCompleted = true;
              clearTimeout(timeoutId);
              reject(err instanceof Error ? err : new Error('Error en la verificación de seguridad.'));
            });
        } catch (syncErr: unknown) {
          if (hasCompleted) return;
          hasCompleted = true;
          clearTimeout(timeoutId);
          reject(
            syncErr instanceof Error
              ? syncErr
              : new Error('No fue posible completar la verificación de seguridad.')
          );
        }
      });
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (!username.trim() || !password.trim()) {
      setErrorMsg('Por favor completa todos los campos.');
      return;
    }

    let recaptchaToken = '';
    if (siteKey) {
      setIsCaptchaExecuting(true);
      try {
        recaptchaToken = await getRecaptchaToken(siteKey);
      } catch (captchaErr) {
        setIsCaptchaExecuting(false);
        if (captchaErr instanceof Error) {
          setErrorMsg(captchaErr.message);
        } else {
          setErrorMsg('Error de verificación de seguridad');
        }
        return;
      }
      setIsCaptchaExecuting(false);
    }

    try {
      const res = await login({
        username: username.trim(),
        password: password.trim(),
        recaptcha_token: recaptchaToken,
        'g-recaptcha-response': recaptchaToken,
      });

      if (res.success && res.user) {
        success(`Bienvenido, ${res.user.nombre || res.user.username}`);
        navigate(from, { replace: true });
      } else {
        setErrorMsg(res.error || 'Credenciales incorrectas');
      }
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.status === 429) {
          setErrorMsg('Demasiados intentos. Por favor espera un minuto antes de reintentar.');
        } else {
          setErrorMsg(err.message || 'Error al iniciar sesión');
        }
      } else if (err instanceof Error) {
        setErrorMsg(err.message || 'Error al iniciar sesión');
      } else {
        setErrorMsg('Error de conexión con el servidor');
      }
    }
  };

  const isPending = isLoggingIn || isCaptchaExecuting;

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
          <div className="login-alert" role="alert" data-testid="login-alert">
            <Icon name="error" size={20} className="shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Formulario de Acceso */}
        <form onSubmit={handleSubmit} className="login-form" noValidate>
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
                disabled={isPending}
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
                disabled={isPending}
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
            disabled={isPending}
          >
            <span>{isPending ? 'Accediendo...' : 'Ingresar al Sistema'}</span>
            <Icon
              name={isPending ? 'progress_activity' : 'arrow_forward'}
              size={20}
              className={`btn-icon ${isPending ? 'animate-spin' : ''}`}
            />
          </button>
        </form>

        {/* Indicador de Entorno (ESTRICTAMENTE visible SOLO en desarrollo) */}
        {isDev && (
          <div className="dev-banner" role="note" data-testid="dev-banner">
            <div className="dev-banner-title">
              <Icon name="code" size={16} /> Entorno de Desarrollo
            </div>
            <span>Usuarios de prueba: <code>admin</code> / <code>supervisor</code> / <code>lider</code></span>
          </div>
        )}

        <footer className="login-footer">
          <p>© {new Date().getFullYear()} Vino Nuevo · Sistema de Casas de Paz</p>
        </footer>
      </main>
    </div>
  );
};

export default LoginPage;
