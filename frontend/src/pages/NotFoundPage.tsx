import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '../components/ui/Icon';
import '../styles/errors.css';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <main className="error-page-wrapper">
      <div className="error-card-canon">
        {/* Código 404 Gigante con gradiente institucional y animación */}
        <div className="error-code-canon" aria-hidden="true">
          404
        </div>

        <div className="error-content-canon">
          <h1 className="error-title-canon">Página no encontrada</h1>
          <p className="error-message-canon">
            Lo sentimos, la página que buscas no existe o ha sido movida.
          </p>

          <div className="error-actions-canon">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn-error-canon btn-error-primary"
            >
              <Icon name="home" size={20} aria-hidden="true" />
              Ir al inicio
            </button>
            <button
              type="button"
              onClick={() => window.history.back()}
              className="btn-error-canon btn-error-secondary"
            >
              <Icon name="arrow_back" size={20} aria-hidden="true" />
              Volver atrás
            </button>
          </div>
        </div>

        {/* Orbes circulares animados de fondo */}
        <div className="error-decorations" aria-hidden="true">
          <div className="decoration-circle" />
          <div className="decoration-circle" />
          <div className="decoration-circle" />
        </div>
      </div>

      <p className="error-footer-canon">
        Vino Nuevo — Servicio Comunitario
      </p>
    </main>
  );
};
