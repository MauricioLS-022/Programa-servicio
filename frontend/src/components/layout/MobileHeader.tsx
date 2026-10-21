import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../context/ThemeContext';
import {
  LayoutDashboard,
  FileText,
  PlusCircle,
  Network,
  Moon,
  Sun,
  LogOut,
  Church,
} from 'lucide-react';

export const MobileHeader: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="flex md:hidden items-center justify-between px-4 py-3 bg-white dark:bg-neutral-900 border-b border-border-subtle dark:border-neutral-800 sticky top-0 z-40">
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-vino text-white flex items-center justify-center">
          <Church className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-serif text-sm font-bold text-text-main dark:text-neutral-100">
            Vino Nuevo
          </h1>
          <span className="text-[10px] text-text-muted dark:text-neutral-400 capitalize">
            {user?.rol || 'Ministerio'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleTheme}
          className="p-2 text-text-muted dark:text-neutral-400"
          aria-label="Alternar tema"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
        </button>
        <button
          onClick={handleLogout}
          className="p-2 text-text-muted hover:text-red-600 dark:text-neutral-400"
          aria-label="Cerrar sesión"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

export const MobileBottomNav: React.FC = () => {
  const { user } = useAuth();
  const rol = user?.rol;

  const navItems = [
    {
      to: '/dashboard',
      label: 'Dashboard',
      icon: <LayoutDashboard className="w-5 h-5" />,
      visible: true,
    },
    {
      to: '/reportes',
      label: 'Reportes',
      icon: <FileText className="w-5 h-5" />,
      visible: true,
    },
    {
      to: '/generar-reporte',
      label: 'Reportar',
      icon: <PlusCircle className="w-5 h-5" />,
      visible: rol === 'lider_cdp' || rol === 'cdp' || rol === 'admin',
    },
    {
      to: '/estructura',
      label: 'Estructura',
      icon: <Network className="w-5 h-5" />,
      visible: rol === 'admin' || rol === 'supervisor',
    },
  ];

  return (
    <nav className="flex md:hidden fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-neutral-900/95 border-t border-border-subtle dark:border-neutral-800 backdrop-blur-md z-40 py-2 px-4 justify-around">
      {navItems
        .filter((i) => i.visible)
        .map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1 text-[11px] font-semibold transition-colors ${
                isActive
                  ? 'text-vino dark:text-vino-light'
                  : 'text-text-muted dark:text-neutral-400'
              }`
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
    </nav>
  );
};

