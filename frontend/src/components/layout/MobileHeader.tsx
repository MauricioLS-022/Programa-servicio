import React from 'react';
import { useTheme } from '../../context/ThemeContext';
import { Icon } from '../ui/Icon';

interface MobileHeaderProps {
  onToggleMenu: () => void;
}

export const MobileHeader: React.FC<MobileHeaderProps> = ({ onToggleMenu }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="mobile-header" aria-label="Cabecera móvil">
      <div className="mobile-header-left">
        <button
          type="button"
          id="menu-toggle"
          className="btn-menu"
          onClick={onToggleMenu}
          aria-label="Abrir menú de navegación"
        >
          <Icon name="menu" size={24} />
        </button>
        <h2 className="mobile-brand">Vino Nuevo</h2>
      </div>

      <div className="mobile-header-right">
        <button
          type="button"
          className="btn-theme-mobile"
          onClick={toggleTheme}
          aria-label={`Cambiar a modo ${theme === 'dark' ? 'claro' : 'oscuro'}`}
          title={`Cambiar a modo ${theme === 'dark' ? 'claro' : 'oscuro'}`}
        >
          <Icon name={theme === 'dark' ? 'light_mode' : 'dark_mode'} size={20} />
        </button>
      </div>
    </header>
  );
};

export default MobileHeader;
