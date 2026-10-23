import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../context/ThemeContext';
import { Moon, Sun, LogOut, User as UserIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (e) {
      console.error('Error al cerrar sesión:', e);
    }
  };

  const rolLabel = {
    admin: 'Administrador',
    supervisor: 'Supervisor de Red',
    lider_cdp: 'Líder Casa de Paz',
  }[user?.rol || 'admin'];

  return (
    <header className="hidden md:flex items-center justify-between px-8 py-3.5 bg-white dark:bg-neutral-800/80 border-b border-border-subtle/80 dark:border-neutral-700/80 sticky top-0 z-30 backdrop-blur-xs">
      <div>
        <h2 className="text-sm font-bold text-text-main dark:text-neutral-100 tracking-tight">
          Ministerio Vino Nuevo
        </h2>
        <p className="text-xs text-text-muted dark:text-neutral-400">
          Sistema Integral de Gestión y Reportes
        </p>
      </div>

      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-text-muted hover:text-text-main hover:bg-surface-low dark:text-neutral-400 dark:hover:text-neutral-200 dark:hover:bg-neutral-700/60 cursor-pointer transition-colors"
          title={`Cambiar a modo ${theme === 'dark' ? 'claro' : 'oscuro'}`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* User Badge */}
        <div className="flex items-center gap-3 pl-3 border-l border-border-subtle/80 dark:border-neutral-700/80">
          <div className="w-8 h-8 rounded-full bg-vino/10 dark:bg-vino-light/20 text-vino dark:text-vino-light flex items-center justify-center font-bold text-xs">
            {user?.nombre?.[0] || user?.username?.[0]?.toUpperCase() || <UserIcon className="w-4 h-4" />}
          </div>
          <div className="text-left">
            <p className="text-xs font-bold text-text-main dark:text-neutral-100 leading-tight">
              {user?.nombre ? `${user.nombre} ${user.apellido || ''}` : user?.username}
            </p>
            <p className="text-[11px] text-text-muted dark:text-neutral-400 font-medium">
              {rolLabel}
            </p>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="p-2 rounded-lg text-text-muted hover:text-red-700 hover:bg-red-50 dark:text-neutral-400 dark:hover:text-red-400 dark:hover:bg-red-950/40 cursor-pointer transition-colors"
          title="Cerrar Sesión"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

