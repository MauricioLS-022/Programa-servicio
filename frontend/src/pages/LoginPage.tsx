import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Church, Lock, User as UserIcon, Moon, Sun, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
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
    <div className="min-h-screen flex flex-col justify-center items-center bg-surface dark:bg-neutral-900 p-4 relative transition-colors duration-200">
      {/* Theme Switcher Button */}
      <button
        type="button"
        onClick={toggleTheme}
        className="absolute top-6 right-6 p-2.5 rounded-full bg-white dark:bg-neutral-800 border border-border-subtle dark:border-neutral-700 shadow-sm text-text-muted hover:text-text-main dark:text-neutral-400 dark:hover:text-neutral-200 transition-colors cursor-pointer"
        aria-label="Alternar tema"
      >
        {theme === 'dark' ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5" />}
      </button>

      {/* Main Card */}
      <div className="w-full max-w-md bg-white dark:bg-neutral-800/90 rounded-2xl border border-border-subtle dark:border-neutral-700/80 shadow-elevated p-8 sm:p-10 transition-all duration-200">
        {/* Header Branding */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-vino text-white flex items-center justify-center shadow-lg shadow-vino/20 mb-4">
            <Church className="w-9 h-9" />
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-text-main dark:text-neutral-100 tracking-tight">
            Vino Nuevo
          </h1>
          <p className="text-xs font-semibold uppercase tracking-wider text-vino dark:text-vino-light mt-1">
            Gestión y Reportes de Casas de Paz
          </p>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="mb-6 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 flex items-start gap-3 text-red-800 dark:text-red-300 text-xs font-medium">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600 dark:text-red-400 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <Input
            label="Usuario"
            placeholder="Ingresa tu nombre de usuario"
            icon={<UserIcon className="w-4 h-4" />}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoggingIn}
            autoComplete="username"
            autoFocus
          />

          <Input
            label="Contraseña"
            type="password"
            placeholder="••••••••"
            icon={<Lock className="w-4 h-4" />}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoggingIn}
            autoComplete="current-password"
          />

          <Button
            type="submit"
            size="lg"
            variant="primary"
            isLoading={isLoggingIn}
            className="w-full mt-2 font-semibold shadow-md"
          >
            Iniciar Sesión
          </Button>
        </form>

        {/* Footer info / Demo hint */}
        <div className="mt-8 pt-6 border-t border-border-subtle/80 dark:border-neutral-700/80 text-center">
          <p className="text-xs text-text-muted dark:text-neutral-400">
            ¿Problemas con tus credenciales? Contacta a tu supervisor de red.
          </p>
        </div>
      </div>
    </div>
  );
};

