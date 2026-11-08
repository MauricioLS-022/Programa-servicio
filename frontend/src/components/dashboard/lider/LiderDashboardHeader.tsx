import React from 'react';
import { Icon } from '../../ui/Icon';
import type { LiderCdpInfo } from '../../../types/liderDashboard';

export interface LiderDashboardHeaderProps {
  usuario: string;
  cdp: LiderCdpInfo | null;
}

export const LiderDashboardHeader: React.FC<LiderDashboardHeaderProps> = ({ usuario, cdp }) => {
  return (
    <header className="lider-page-header" data-testid="lider-page-header">
      <div>
        <h1 className="title">Panel de Casa de Paz</h1>
        <p className="subtitle">
          Bienvenido, <strong>{usuario}</strong>. Aquí puedes gestionar y registrar las reuniones semanales.
        </p>
      </div>
      {cdp && (
        <div className="cdp-tag" data-testid="cdp-tag">
          <span className="tag-icon">
            <Icon name="home" size={18} />
          </span>
          <span>
            {cdp.codigo}
            {cdp.anfitrion ? ` · ${cdp.anfitrion}` : ''}
          </span>
        </div>
      )}
    </header>
  );
};
