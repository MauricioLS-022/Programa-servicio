import React from 'react';

export interface DashboardFrutoCardProps {
  conversiones?: number;
  reconciliaciones?: number;
  cestasAmor?: number;
  totalVisitas?: number;
}

export const DashboardFrutoCard: React.FC<DashboardFrutoCardProps> = ({
  conversiones = 0,
  reconciliaciones = 0,
  cestasAmor = 0,
  totalVisitas = 0,
}) => {
  return (
    <article className="participation-card">
      <div className="status-card-header">
        <h2 className="section-title">Fruto y Transformación</h2>
        <p className="section-subtitle">Impacto espiritual consolidado</p>
      </div>

      <div className="fruto-grid">
        <div className="fruto-item">
          <div className="fruto-icon bg-success-light">
            <span className="material-symbols-outlined text-success">person_add</span>
          </div>
          <div className="fruto-info">
            <span className="fruto-number">{conversiones}</span>
            <span className="fruto-label">Confesiones de Fe</span>
          </div>
        </div>

        <div className="fruto-item">
          <div className="fruto-icon bg-primary-light">
            <span className="material-symbols-outlined text-primary">handshake</span>
          </div>
          <div className="fruto-info">
            <span className="fruto-number">{reconciliaciones}</span>
            <span className="fruto-label">Reconciliaciones</span>
          </div>
        </div>

        <div className="fruto-item">
          <div className="fruto-icon bg-accent-light">
            <span className="material-symbols-outlined text-primary-container">favorite</span>
          </div>
          <div className="fruto-info">
            <span className="fruto-number">{cestasAmor}</span>
            <span className="fruto-label">Cestas de Amor</span>
          </div>
        </div>

        <div className="fruto-item">
          <div className="fruto-icon bg-info-light">
            <span className="material-symbols-outlined text-info">how_to_reg</span>
          </div>
          <div className="fruto-info">
            <span className="fruto-number">{totalVisitas}</span>
            <span className="fruto-label">Visitas</span>
          </div>
        </div>
      </div>
    </article>
  );
};

