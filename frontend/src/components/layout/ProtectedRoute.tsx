import React from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import type { UserRole } from '../../types/auth';
import { Icon } from '../ui/Icon';
import '../../styles/errors.css';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-surface dark:bg-[#120e0f] gap-3">
        <Icon name="progress_activity" size={32} className="text-vino dark:text-[#ffdad6] icon-spin" />
        <p className="text-sm font-medium text-text-muted dark:text-[#d4c2bf]">
          Verificando sesión...
        </p>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.rol)) {
    return (
      <main className="error-page-wrapper">
        <div className="error-card-canon">
          <div className="error-code-canon code-403" aria-hidden="true">
            403
          </div>

          <div className="error-content-canon">
            <h1 className="error-title-canon">Acceso denegado</h1>
            <p className="error-message-canon">
              No tienes permiso para acceder a esta página. Si crees que esto es un error, contacta al administrador.
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
  }

  return <>{children}</>;
};
