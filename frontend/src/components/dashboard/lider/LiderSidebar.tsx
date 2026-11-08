import React from 'react';
import { Icon } from '../../ui/Icon';
import type { LiderMiembro } from '../../../types/liderDashboard';

export interface LiderSidebarProps {
  diasCierreTexto?: string;
  lideres: LiderMiembro[];
}

export const LiderSidebar: React.FC<LiderSidebarProps> = ({
  diasCierreTexto = 'Próximo cierre: Domingo 6:00 PM',
  lideres,
}) => {
  return (
    <div className="right-sidebar-column" data-testid="lider-sidebar">
      {/* Tarjeta de Recordatorio */}
      <aside className="reminder-card" data-testid="reminder-card">
        <span className="watermark-warning" aria-hidden="true">
          <Icon name="error" size={120} />
        </span>
        <h3 className="reminder-title">Recordatorio</h3>
        <p className="reminder-text">
          Recuerda subir tus reportes antes del domingo a las 6:00 PM para la revisión semanal.
        </p>
        <div className="reminder-footer">
          <Icon name="schedule" size={16} />
          <span>{diasCierreTexto}</span>
        </div>
      </aside>

      {/* Tarjeta Mi Equipo */}
      <aside className="team-card" data-testid="team-card">
        <div className="team-header">
          <span className="team-icon">
            <Icon name="badge" size={24} />
          </span>
          <h3 className="team-title">Mi Equipo</h3>
        </div>

        <ul className="team-list">
          {lideres && lideres.length > 0 ? (
            lideres.map((lider, index) => {
              const isPrincipal =
                lider.rol?.toLowerCase().includes('lider') &&
                !lider.rol?.toLowerCase().includes('sub');
              return (
                <li key={lider.id || index} className="team-member" data-testid={`team-member-${index}`}>
                  <div className={`member-avatar ${isPrincipal ? 'principal' : 'sublider'}`}>
                    <Icon name="person" size={20} />
                  </div>
                  <div className="member-info">
                    <p className="member-name">
                      {lider.nombre} {lider.apellido || ''}
                    </p>
                    <p className="member-role">{lider.rol}</p>
                  </div>
                </li>
              );
            })
          ) : (
            <li className="team-member" style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No hay líderes registrados en esta Casa de Paz.
            </li>
          )}
        </ul>
      </aside>
    </div>
  );
};
