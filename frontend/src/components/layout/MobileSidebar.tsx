import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Icon, type IconName } from '../ui/Icon';

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItemConfig {
  to: string;
  label: string;
  icon: IconName;
}

export const MobileSidebar: React.FC<MobileSidebarProps> = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    onClose();
    try {
      await logout();
      navigate('/login');
    } catch (e) {
      console.error('Error al cerrar sesión:', e);
    }
  };

  const rol = user?.rol;

  const getSubtitulo = () => {
    if (rol === 'supervisor') return 'Supervisión Regional';
    if (rol === 'admin') return 'Administración';
    return 'Casa de Paz';
  };

  const getNavItems = (): NavItemConfig[] => {
    if (rol === 'supervisor') {
      return [
        { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
        { to: '/estructura', label: 'Estructura', icon: 'account_tree' },
        { to: '/reportes', label: 'Reportes', icon: 'analytics' },
        { to: '/lideres', label: 'Líderes', icon: 'leaderboard' },
        { to: '/perfil', label: 'Perfil', icon: 'person' },
      ];
    }
    if (rol === 'lider_cdp') {
      return [
        { to: '/dashboard', label: 'Inicio', icon: 'home' },
        { to: '/generar-reporte', label: 'Generar Reporte', icon: 'description' },
        { to: '/perfil', label: 'Perfil', icon: 'person' },
      ];
    }
    // Admin por defecto
    return [
      { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
      { to: '/estructura', label: 'Estructura', icon: 'account_tree' },
      { to: '/usuarios', label: 'Usuarios', icon: 'group' },
      { to: '/lideres', label: 'Líderes', icon: 'leaderboard' },
      { to: '/reportes', label: 'Reportes', icon: 'analytics' },
      { to: '/perfil', label: 'Perfil', icon: 'person' },
    ];
  };

  const navItems = getNavItems();

  return (
    <>
      {/* Overlay translúcido de fondo */}
      <div
        id="sidebar-overlay"
        className={`sidebar-overlay ${isOpen ? 'active' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer lateral deslizable */}
      <aside
        className={`sidebar ${isOpen ? 'active' : ''}`}
        aria-label="Menú lateral de navegación móvil"
      >
        <div className="sidebar-header">
          <div className="logo-box">
            <img src="/logo3.webp" alt="Vino Nuevo" className="logo" />
          </div>
          <div className="brand-text">
            <h2 className="brand-title">Vino Nuevo</h2>
            <p className="brand-subtitle">{getSubtitulo()}</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon name={item.icon} size={22} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button
            type="button"
            onClick={handleLogout}
            className="nav-item"
            aria-label="Cerrar Sesión"
          >
            <Icon name="logout" size={22} className="logout-icon" />
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default MobileSidebar;

