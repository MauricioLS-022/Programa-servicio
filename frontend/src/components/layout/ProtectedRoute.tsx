import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import type { UserRole } from '../../types/auth';
import { Loader2, ShieldAlert } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-surface dark:bg-neutral-900 gap-3">
        <Loader2 className="w-8 h-8 text-vino dark:text-vino-light animate-spin" />
        <p className="text-sm font-medium text-text-muted dark:text-neutral-400">
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
      <div className="min-h-screen flex flex-col items-center justify-center bg-surface dark:bg-neutral-900 px-4 text-center">
        <div className="p-4 rounded-full bg-red-100 dark:bg-red-950/50 text-red-700 dark:text-red-400 mb-4">
          <ShieldAlert className="w-10 h-10" />
        </div>
        <h2 className="font-serif text-2xl font-bold text-text-main dark:text-neutral-100 mb-2">
          Acceso Restringido
        </h2>
        <p className="text-sm text-text-muted dark:text-neutral-400 max-w-md mb-6">
          Tu rol actual (<strong className="capitalize">{user.rol}</strong>) no tiene autorización
          para acceder a este módulo ministerial.
        </p>
        <button
          onClick={() => window.history.back()}
          className="px-5 py-2.5 rounded-lg bg-vino text-white text-sm font-semibold hover:bg-vino-hover cursor-pointer transition-colors"
        >
          Volver a la vista anterior
        </button>
      </div>
    );
  }

  return <>{children}</>;
};

