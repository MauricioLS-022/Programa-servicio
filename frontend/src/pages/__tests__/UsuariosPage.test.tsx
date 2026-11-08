import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { UsuariosPage } from '../UsuariosPage';
import { ProtectedRoute } from '../../components/layout/ProtectedRoute';
import type { Usuario } from '../../types/usuario';

const mockSuccess = vi.fn();
const mockError = vi.fn();
const mockInfo = vi.fn();
vi.mock('../../context/ToastContext', () => ({
  useToast: () => ({
    success: mockSuccess,
    error: mockError,
    info: mockInfo,
    showToast: vi.fn(),
  }),
}));

let mockCurrentUser: {
  id: string;
  username: string;
  rol: 'admin' | 'supervisor' | 'lider_cdp';
  nombre: string;
  apellido: string;
} = {
  id: 'usr-admin-1',
  username: 'admin',
  rol: 'admin',
  nombre: 'Admin',
  apellido: 'Principal',
};

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockCurrentUser,
    isAuthenticated: true,
    isLoading: false,
  }),
}));

const mockUsuariosList: Usuario[] = [
  {
    id: 'usr-admin-1',
    username: 'admin',
    nombre: 'Admin',
    apellido: 'Principal',
    tipo_usuario: 'admin',
    is_active: 1,
  },
  {
    id: 'usr-sup-2',
    username: 'sup_norte',
    nombre: 'Marcos',
    apellido: 'Pérez',
    tipo_usuario: 'supervisor',
    red_nombre: 'Red Norte',
    red_id: 1,
    is_active: 1,
  },
  {
    id: 'usr-lider-3',
    username: 'lider_cdp1',
    nombre: 'Elena',
    apellido: 'Gómez',
    tipo_usuario: 'lider_cdp',
    cdp_codigo: 'CDP-001',
    cdp_id: 10,
    is_active: 1,
  },
  {
    id: 'usr-libre-4',
    username: 'usuario_libre',
    nombre: 'Roberto',
    apellido: 'Díaz',
    tipo_usuario: 'lider_cdp',
    is_active: 0,
  },
];

const mockCrearUsuario = vi.fn();
const mockEditarUsuario = vi.fn();
const mockToggleUsuario = vi.fn().mockResolvedValue({ success: true, message: 'Estado alternado' });
const mockEliminarUsuario = vi.fn().mockResolvedValue({ success: true, message: 'Usuario eliminado' });

vi.mock('../../hooks/useUsuarios', () => ({
  useUsuarios: () => ({
    usuarios: mockUsuariosList,
    total: mockUsuariosList.length,
    totalActivos: 3,
    page: 1,
    pages: 1,
    isLoading: false,
    isError: false,
    error: null,
    refetch: vi.fn(),
  }),
  useUsuarioOpcionesAsignacion: () => ({
    redes: [{ id: 1, nombre: 'Red Norte' }],
    casasDePaz: [{ id: 10, codigo: 'CDP-001' }],
    isLoading: false,
    isError: false,
  }),
  useUsuarioMutations: () => ({
    crearUsuario: mockCrearUsuario,
    isCreando: false,
    editarUsuario: mockEditarUsuario,
    isEditando: false,
    toggleUsuario: mockToggleUsuario,
    isToggling: false,
    eliminarUsuario: mockEliminarUsuario,
    isEliminando: false,
  }),
}));

describe('UsuariosPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockCurrentUser = {
      id: 'usr-admin-1',
      username: 'admin',
      rol: 'admin',
      nombre: 'Admin',
      apellido: 'Principal',
    };
  });

  it('renderiza el Bento Grid con métricas y el directorio de usuarios', () => {
    render(
      <MemoryRouter>
        <UsuariosPage />
      </MemoryRouter>
    );

    expect(screen.getByText('Usuarios del Sistema')).toBeInTheDocument();
    expect(screen.getByText('Usuarios Activos')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Seguridad de Roles')).toBeInTheDocument();
    expect(screen.getByText('@admin')).toBeInTheDocument();
    expect(screen.getByText('@sup_norte')).toBeInTheDocument();
    expect(screen.getByText('@lider_cdp1')).toBeInTheDocument();
    expect(screen.getByText('@usuario_libre')).toBeInTheDocument();
  });

  it('filtra usuarios instantáneamente con Live Search por nombre o username', () => {
    render(
      <MemoryRouter>
        <UsuariosPage />
      </MemoryRouter>
    );

    const searchInput = screen.getByPlaceholderText('Buscar por nombre o usuario...');
    fireEvent.change(searchInput, { target: { value: 'Elena' } });

    expect(screen.getByText('@lider_cdp1')).toBeInTheDocument();
    expect(screen.queryByText('@admin')).not.toBeInTheDocument();
    expect(screen.queryByText('@sup_norte')).not.toBeInTheDocument();
  });

  it('bloquea la eliminación de la propia cuenta en sesión (Candado 1)', async () => {
    render(
      <MemoryRouter>
        <UsuariosPage />
      </MemoryRouter>
    );

    // Botón eliminar para el primer usuario (usr-admin-1)
    const deleteButtons = screen.getAllByTitle('Eliminar Usuario');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('No es posible eliminar el usuario')).toBeInTheDocument();
      expect(screen.getByText(/No puedes eliminar tu propia cuenta de usuario en esta sesión/i)).toBeInTheDocument();
    });
  });

  it('bloquea la eliminación de un usuario con responsabilidades activas (Candado 2)', async () => {
    render(
      <MemoryRouter>
        <UsuariosPage />
      </MemoryRouter>
    );

    // Botón eliminar para sup_norte (tiene Red Norte)
    const deleteButtons = screen.getAllByTitle('Eliminar Usuario');
    fireEvent.click(deleteButtons[1]);

    await waitFor(() => {
      expect(screen.getByText('No es posible eliminar el usuario')).toBeInTheDocument();
      expect(screen.getByText(/supervisor de la red "Red Norte"/i)).toBeInTheDocument();
    });
  });

  it('permite la eliminación escribiendo estrictamente ELIMINAR para un usuario sin dependencias (Candado 3)', async () => {
    render(
      <MemoryRouter>
        <UsuariosPage />
      </MemoryRouter>
    );

    // Botón eliminar para usuario_libre (sin dependencias)
    const deleteButtons = screen.getAllByTitle('Eliminar Usuario');
    fireEvent.click(deleteButtons[3]);

    await waitFor(() => {
      expect(screen.getByText('Confirmar Eliminación')).toBeInTheDocument();
    });

    const confirmBtn = screen.getByRole('button', { name: /^Eliminar$/i });
    expect(confirmBtn).toBeDisabled();

    // Escribir ELIMINAR en el input
    const inputConfirm = screen.getByPlaceholderText('ELIMINAR');
    fireEvent.change(inputConfirm, { target: { value: 'ELIMINAR' } });

    expect(confirmBtn).not.toBeDisabled();
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(mockEliminarUsuario).toHaveBeenCalledWith('usr-libre-4');
    });
  });

  it('bloquea el acceso a usuarios con rol supervisor mostrando Acceso Restringido', () => {
    mockCurrentUser = {
      id: 'usr-sup-2',
      username: 'sup_norte',
      rol: 'supervisor',
      nombre: 'Marcos',
      apellido: 'Pérez',
    };

    render(
      <MemoryRouter initialEntries={['/usuarios']}>
        <Routes>
          <Route
            path="/usuarios"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <UsuariosPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Acceso denegado')).toBeInTheDocument();
    expect(screen.getByText(/no tienes permiso para acceder a esta página/i)).toBeInTheDocument();
    expect(screen.queryByText('Usuarios del Sistema')).not.toBeInTheDocument();
  });
});


