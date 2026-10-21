import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
  LayoutDashboard,
  FileText,
  Network,
  PlusCircle,
  Church,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
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
      label: 'Cargar Reporte',
      icon: <PlusCircle className="w-5 h-5" />,
      visible: rol === 'lider_cdp' || rol === 'cdp' || rol === 'admin',
    },
    {
      to: '/estructura',
      label: 'Estructura Ministerial',
      icon: <Network className="w-5 h-5" />,
      visible: rol === 'admin' || rol === 'supervisor',
    },
  ];

  return (
    <aside className="hidden md:flex flex-col w-64 bg-surface-sidebar dark:bg-neutral-900 border-r border-border-subtle/80 dark:border-neutral-800 min-h-screen shrink-0">
      {/* Brand Header */}
      <div className="px-6 py-6 border-b border-border-subtle/80 dark:border-neutral-800 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-vino text-white flex items-center justify-center shadow-md">
          <Church className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-serif text-lg font-bold text-text-main dark:text-neutral-100 leading-tight">
            Vino Nuevo
          </h1>
          <p className="text-[11px] font-semibold uppercase tracking-wider text-vino-light dark:text-neutral-400">
            Casas de Paz
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 flex flex-col gap-1.5 overflow-y-auto custom-scrollbar">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-text-muted dark:text-neutral-500">
          Navegación Principal
        </div>
        {navItems
          .filter((item) => item.visible)
          .map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-vino text-white shadow-sm dark:bg-vino dark:text-white'
                    : 'text-text-muted dark:text-neutral-400 hover:text-text-main dark:hover:text-neutral-100 hover:bg-surface dark:hover:bg-neutral-800/60'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-border-subtle/80 dark:border-neutral-800 text-center">
        <p className="text-[11px] text-text-muted/80 dark:text-neutral-500">
          © {new Date().getFullYear()} Vino Nuevo Community
        </p>
      </div>
    </aside>
  );
};

