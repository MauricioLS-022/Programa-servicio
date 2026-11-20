import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route, useLocation } from 'react-router-dom';
import { ProtectedRoute } from '../ProtectedRoute';
import type { User } from '../../../types/auth';

const mockUseAuth = vi.fn();
vi.mock('../../../hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}));

const LoginProbe = () => {
  const location = useLocation();
  const fromPath = (location.state as { from?: { pathname: string; search?: string } } | null)?.from?.pathname;
  return <div data-testid="login-probe">LoginPage from:{fromPath || 'none'}</div>;
};

describe('ProtectedRoute', () => {
  beforeEach(() => {
    mockUseAuth.mockReset();
  });

  it('muestra el indicador de carga mientras verifica la sesión', () => {
    mockUseAuth.mockReturnValue({
      user: undefined,
      isAuthenticated: false,
      isLoading: true,
    });

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <ProtectedRoute>
          <div>Contenido Privado</div>
        </ProtectedRoute>
      </MemoryRouter>
    );

    expect(screen.getByText('Verificando sesión...')).toBeInTheDocument();
    expect(screen.queryByText('Contenido Privado')).not.toBeInTheDocument();
  });

  it('redirige a /login conservando el location solicitado cuando no está autenticado', () => {
    mockUseAuth.mockReturnValue({
      user: undefined,
      isAuthenticated: false,
      isLoading: false,
    });

    render(
      <MemoryRouter initialEntries={['/usuarios']}>
        <Routes>
          <Route path="/login" element={<LoginProbe />} />
          <Route
            path="/usuarios"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <div>Gestión de Usuarios</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByTestId('login-probe')).toHaveTextContent('LoginPage from:/usuarios');
    expect(screen.queryByText('Gestión de Usuarios')).not.toBeInTheDocument();
  });

  it('muestra la pantalla institucional 403 Acceso denegado cuando el rol no está permitido', () => {
    const supervisorUser: User = {
      id: 'sup-1',
      username: 'supervisor1',
      nombre: 'Pedro',
      apellido: 'Pérez',
      rol: 'supervisor',
    };
    mockUseAuth.mockReturnValue({
      user: supervisorUser,
      isAuthenticated: true,
      isLoading: false,
    });

    const historyBackSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {});

    render(
      <MemoryRouter initialEntries={['/usuarios']}>
        <Routes>
          <Route path="/dashboard" element={<div>Dashboard Principal</div>} />
          <Route
            path="/usuarios"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <div>Gestión de Usuarios</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('403')).toBeInTheDocument();
    expect(screen.getByText('Acceso denegado')).toBeInTheDocument();
    expect(screen.queryByText('Gestión de Usuarios')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Volver atrás/i }));
    expect(historyBackSpy).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole('button', { name: /Ir al inicio/i }));
    expect(screen.getByText('Dashboard Principal')).toBeInTheDocument();

    historyBackSpy.mockRestore();
  });

  it('renderiza los hijos cuando el usuario está autenticado y tiene rol autorizado', () => {
    const adminUser: User = {
      id: 'adm-1',
      username: 'admin',
      nombre: 'Pastor',
      apellido: 'Admin',
      rol: 'admin',
    };
    mockUseAuth.mockReturnValue({
      user: adminUser,
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <MemoryRouter initialEntries={['/usuarios']}>
        <ProtectedRoute allowedRoles={['admin']}>
          <div>Gestión de Usuarios</div>
        </ProtectedRoute>
      </MemoryRouter>
    );

    expect(screen.getByText('Gestión de Usuarios')).toBeInTheDocument();
  });
});
