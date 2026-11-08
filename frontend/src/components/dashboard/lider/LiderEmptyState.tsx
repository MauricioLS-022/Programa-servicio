import React from 'react';
import { Link } from 'react-router-dom';
import { Icon } from '../../ui/Icon';

export interface LiderEmptyStateProps {
  mensaje?: string;
}

export const LiderEmptyState: React.FC<LiderEmptyStateProps> = ({
  mensaje = 'Parece que aún no has comenzado. Tus reportes semanales aparecerán aquí una vez que los registres.',
}) => {
  return (
    <div className="empty-state" data-testid="lider-empty-state">
      <div className="empty-icon-wrapper">
        <Icon name="inventory_2" size={40} />
      </div>
      <p className="empty-text">{mensaje}</p>
      <Link to="/generar-reporte" className="btn-new" data-testid="btn-primer-reporte">
        <Icon name="add_circle" size={18} />
        <span>Crear mi primer reporte</span>
      </Link>
    </div>
  );
};
