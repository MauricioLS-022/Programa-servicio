import React from 'react';

export interface DashboardHeaderProps {
  rol?: string;
  userName?: string;
  nivel?: 'general' | 'red' | 'cdp';
  redNombre?: string;
  supervisorNombre?: string;
  casasActivas?: number;
  cdpNombre?: string;
  cdpDireccion?: string;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  rol,
  userName = 'Usuario',
  nivel = 'general',
  redNombre,
  supervisorNombre,
  casasActivas = 0,
  cdpNombre,
  cdpDireccion,
}) => {
  const isSupervisor = rol === 'supervisor';

  if (nivel === 'red' && redNombre) {
    return (
      <div className="section-header-row">
        <div>
          <h2 className="section-title">{redNombre}</h2>
          <p className="section-subtitle">
            {supervisorNombre && (
              <>
                Supervisor: <strong>{supervisorNombre}</strong> ·{' '}
              </>
            )}
            Monitoreo y métricas zonales
          </p>
        </div>
        <div className="header-action-group">
          <span className="badge-status badge-info">
            {casasActivas} Casas Activas
          </span>
        </div>
      </div>
    );
  }

  if (nivel === 'cdp' && cdpNombre) {
    return (
      <div className="section-header-row">
        <div>
          <h2 className="section-title">{cdpNombre}</h2>
          <p className="section-subtitle">
            <span
              className="material-symbols-outlined"
              style={{ fontSize: '0.9rem', verticalAlign: 'middle', marginRight: '0.25rem' }}
            >
              location_on
            </span>
            {cdpDireccion || 'Dirección no registrada'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <header className="page-header">
      <div>
        {isSupervisor ? (
          <>
            <h1 className="title">Panel de Supervisión Regional</h1>
            <p className="subtitle">
              Monitoreo de actividad de tu red ministerial. Bienvenido, {userName}.
            </p>
          </>
        ) : (
          <>
            <h1 className="title">Panel Administrativo</h1>
            <p className="subtitle">
              Bienvenido de vuelta. Resumen ejecutivo de la actividad ministerial y consolidación.
            </p>
          </>
        )}
      </div>
    </header>
  );
};

