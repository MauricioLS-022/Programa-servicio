import React from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../context/ThemeContext';
import { Icon } from '../ui/Icon';

export const DesktopHeader: React.FC = () => {
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

  const rol = user?.rol;

  // Enlaces adaptados estrictamente según el rol en header_admin.html
  const getNavLinks = () => {
    if (rol === 'supervisor') {
      return [
        { to: '/dashboard', label: 'Dashboard' },
        { to: '/estructura', label: 'Estructura' },
        { to: '/reportes', label: 'Reportes' },
        { to: '/lideres', label: 'Líderes' },
        { to: '/perfil', label: 'Perfil' },
      ];
    }
    if (rol === 'lider_cdp') {
      return [
        { to: '/dashboard', label: 'Inicio' },
        { to: '/generar-reporte', label: 'Generar Reporte' },
        { to: '/perfil', label: 'Perfil' },
      ];
    }
    // Rol admin por defecto
    return [
      { to: '/dashboard', label: 'Dashboard' },
      { to: '/estructura', label: 'Estructura' },
      { to: '/usuarios', label: 'Usuarios' },
      { to: '/lideres', label: 'Líderes' },
      { to: '/reportes', label: 'Reportes' },
      { to: '/perfil', label: 'Perfil' },
    ];
  };

  const navLinks = getNavLinks();

  return (
    <header id="admin-desktop-header" className="header-nav" aria-label="Navegación principal de escritorio">
      {/* Logotipo oficial */}
      <div className="logo-container">
        <Link to="/dashboard" className="logo-link" aria-label="Ir al inicio del ministerio">
          <img src="/logo.webp" alt="Vino Nuevo" className="logo-img" />
        </Link>
      </div>

      {/* Navegación central con tipografía serif original */}
      <nav className="link-container" aria-label="Enlaces de navegación ministerial">
        {navLinks.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}
          >
            <span className="nav-text">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Sección derecha: Selector de tema y Cierre de Sesión con logout.webp */}
      <div className="header-right-actions">
        <button
          type="button"
          onClick={toggleTheme}
          className="theme-toggle-header"
          aria-label={`Cambiar a modo ${theme === 'dark' ? 'claro' : 'oscuro'}`}
          title={`Cambiar a modo ${theme === 'dark' ? 'claro' : 'oscuro'}`}
        >
          <Icon name={theme === 'dark' ? 'light_mode' : 'dark_mode'} size={20} />
        </button>

        <button
          type="button"
          onClick={handleLogout}
          className="logout-btn"
          aria-label="Cerrar Sesión"
          title="Cerrar Sesión"
        >
          <img src="/iconos/logout.webp" alt="Cerrar Sesión" className="logout-icon" />
          <span className="logout-text">Cerrar Sesión</span>
        </button>
      </div>
    </header>
  );
};

export default DesktopHeader;

