import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Icon, type IconName } from '../ui/Icon';

interface BottomNavItem {
  to: string;
  label: string;
  icon: IconName;
}

export const MobileBottomNav: React.FC = () => {
  const { user } = useAuth();
  const rol = user?.rol;

  const getNavItems = (): BottomNavItem[] => {
    if (rol === 'supervisor') {
      return [
        { to: '/dashboard', label: 'Dash', icon: 'dashboard' },
        { to: '/estructura', label: 'Estructura', icon: 'account_tree' },
        { to: '/reportes', label: 'Reportes', icon: 'analytics' },
        { to: '/lideres', label: 'Líderes', icon: 'leaderboard' },
        { to: '/perfil', label: 'Mí', icon: 'person' },
      ];
    }
    if (rol === 'lider_cdp') {
      return [
        { to: '/dashboard', label: 'Inicio', icon: 'home' },
        { to: '/generar-reporte', label: 'Reporte', icon: 'description' },
        { to: '/perfil', label: 'Perfil', icon: 'person' },
      ];
    }
    // Admin por defecto
    return [
      { to: '/dashboard', label: 'Dash', icon: 'dashboard' },
      { to: '/estructura', label: 'Estructura', icon: 'account_tree' },
      { to: '/usuarios', label: 'Usuarios', icon: 'group' },
      { to: '/lideres', label: 'Líderes', icon: 'leaderboard' },
      { to: '/reportes', label: 'Reportes', icon: 'analytics' },
      { to: '/perfil', label: 'Mí', icon: 'person' },
    ];
  };

  const navItems = getNavItems();

  return (
    <nav className="mobile-bottom-nav" aria-label="Navegación inferior móvil">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) => `mobile-nav-item ${isActive ? 'active' : ''}`}
        >
          <Icon name={item.icon} size={22} />
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
};

export default MobileBottomNav;

