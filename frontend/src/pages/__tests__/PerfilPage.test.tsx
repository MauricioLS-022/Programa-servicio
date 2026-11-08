import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { PerfilPage } from '../PerfilPage';
import { api } from '../../api/client';

// Mock Toasts
const mockSuccess = vi.fn();
const mockError = vi.fn();
vi.mock('../../context/ToastContext', () => ({
  useToast: () => ({
    success: mockSuccess,
    error: mockError,
    showToast: vi.fn(),
  }),
}));

// Mock Theme
const mockToggleTheme = vi.fn();
vi.mock('../../context/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'light',
    toggleTheme: mockToggleTheme,
    setTheme: vi.fn(),
  }),
}));

// Mock Auth
let mockUser: {
  id: string;
  username: string;
  rol: 'admin' | 'supervisor' | 'lider_cdp';
  nombre: string;
  apellido: string;
} = {
  id: 'usr-1',
  username: 'pastor_juan',
  rol: 'admin',
  nombre: 'Juan',
  apellido: 'Pérez',
};

const mockRefetchUser = vi.fn();
vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockUser,
    refetchUser: mockRefetchUser,
    isAuthenticated: true,
  }),
}));

// Mock Perfil
let mockPerfilData: any = {
  id: 'usr-1',
  username: 'pastor_juan',
  nombre: 'Juan',
  apellido: 'Pérez',
  tipo_usuario: 'admin',
};

const mockRefetch = vi.fn();
vi.mock('../../hooks/usePerfil', () => ({
  usePerfil: () => ({
    perfil: mockPerfilData,
    usuario: mockPerfilData?.username,
    rol: mockPerfilData?.tipo_usuario,
    isLoading: false,
    isError: false,
    refetch: mockRefetch,
  }),
}));

// Mock API Client
vi.mock('../../api/client', () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    status: number;
    constructor(status: number, message: string) {
      super(message);
      this.status = status;
    }
  },
}));

describe('PerfilPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUser = {
      id: 'usr-1',
      username: 'pastor_juan',
      rol: 'admin',
      nombre: 'Juan',
      apellido: 'Pérez',
    };
    mockPerfilData = {
      id: 'usr-1',
      username: 'pastor_juan',
      nombre: 'Juan',
      apellido: 'Pérez',
      tipo_usuario: 'admin',
    };
  });

  it('renderiza la identidad ministerial del administrador con Acceso Global', () => {
    render(
      <MemoryRouter>
        <PerfilPage />
      </MemoryRouter>
    );

    expect(screen.getByText('Mi Perfil')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Juan Pérez' })).toBeInTheDocument();
    expect(screen.getAllByText('Administrador').length).toBeGreaterThan(0);
    expect(screen.getByText('Acceso Global')).toBeInTheDocument();
  });

  it('renderiza la identidad del supervisor con su Red Ministerial Asignada', () => {
    mockPerfilData = {
      id: 'usr-sup-1',
      username: 'sup_maria',
      nombre: 'María',
      apellido: 'Gómez',
      tipo_usuario: 'supervisor',
      red_id: 1,
      red_nombre: 'Red Juvenil Norte',
    };

    render(
      <MemoryRouter>
        <PerfilPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: 'María Gómez' })).toBeInTheDocument();
    expect(screen.getAllByText('Supervisor').length).toBeGreaterThan(0);
    expect(screen.getByText('Red Juvenil Norte')).toBeInTheDocument();
  });

  it('renderiza la identidad del líder CDP con su Casa de Paz y Red', () => {
    mockPerfilData = {
      id: 'usr-lider-1',
      username: 'lider_carlos',
      nombre: 'Carlos',
      apellido: 'Mendoza',
      tipo_usuario: 'lider_cdp',
      cdp_codigo: 'CDP-005',
      cdp_asignada: 'Betel Victoria',
      red_nombre: 'Red Familia',
    };

    render(
      <MemoryRouter>
        <PerfilPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: 'Carlos Mendoza' })).toBeInTheDocument();
    expect(screen.getAllByText('Líder Casa de Paz').length).toBeGreaterThan(0);
    expect(screen.getByText('Betel Victoria')).toBeInTheDocument();
    expect(screen.getByText('Red Familia')).toBeInTheDocument();
  });

  it('permite cambiar el nombre de usuario y notifica éxito', async () => {
    (api.post as any).mockResolvedValueOnce({
      success: true,
      message: 'Nombre de usuario actualizado con éxito',
      username: 'pastor_juan_nuevo',
    });

    render(
      <MemoryRouter>
        <PerfilPage />
      </MemoryRouter>
    );

    const userInput = screen.getByLabelText('Nuevo nombre de usuario');
    fireEvent.change(userInput, { target: { value: 'pastor_juan_nuevo' } });

    const btnSubmit = screen.getByRole('button', { name: /Actualizar Usuario/i });
    fireEvent.click(btnSubmit);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/perfil/username', {
        nuevo_username: 'pastor_juan_nuevo',
      });
      expect(mockSuccess).toHaveBeenCalledWith('Nombre de usuario actualizado con éxito');
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  it('calcula la fortaleza de la nueva contraseña y valida la coincidencia', async () => {
    (api.post as any).mockResolvedValueOnce({
      success: true,
      message: 'Contraseña actualizada correctamente',
    });

    render(
      <MemoryRouter>
        <PerfilPage />
      </MemoryRouter>
    );

    const passActual = screen.getByLabelText('Contraseña actual');
    const passNueva = screen.getByLabelText('Nueva contraseña');
    const passConfirmar = screen.getByLabelText('Confirmar nueva contraseña');
    const btnSubmit = screen.getByRole('button', { name: /Cambiar Contraseña/i });

    // Botón deshabilitado inicialmente
    expect(btnSubmit).toBeDisabled();

    // Contraseña débil
    fireEvent.change(passNueva, { target: { value: 'abc' } });
    expect(screen.getByText(/Fortaleza: Muy débil/i)).toBeInTheDocument();

    // Contraseña fuerte con números y mayúsculas
    fireEvent.change(passNueva, { target: { value: 'Bendicion#2026' } });
    expect(screen.getByText(/Fortaleza: Excelente/i)).toBeInTheDocument();

    // No coinciden
    fireEvent.change(passConfirmar, { target: { value: 'Bendicion#2025' } });
    expect(screen.getByText(/Las contraseñas no coinciden/i)).toBeInTheDocument();
    expect(btnSubmit).toBeDisabled();

    // Coinciden y contraseña actual completada
    fireEvent.change(passActual, { target: { value: 'AntiguaClave123' } });
    fireEvent.change(passConfirmar, { target: { value: 'Bendicion#2026' } });
    expect(screen.getByText(/Las contraseñas coinciden/i)).toBeInTheDocument();
    expect(btnSubmit).not.toBeDisabled();

    fireEvent.click(btnSubmit);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/perfil/password', {
        password_actual: 'AntiguaClave123',
        password_nueva: 'Bendicion#2026',
        password_confirmar: 'Bendicion#2026',
      });
      expect(mockSuccess).toHaveBeenCalledWith('Contraseña actualizada correctamente');
    });
  });

  it('muestra el dispositivo y el último inicio de sesión en tiempo real', () => {
    render(
      <MemoryRouter>
        <PerfilPage />
      </MemoryRouter>
    );

    expect(screen.getByText('Dispositivo')).toBeInTheDocument();
    expect(screen.getByText('Último inicio de sesión')).toBeInTheDocument();
    expect(screen.getByText('Estado')).toBeInTheDocument();
    expect(screen.getByText('Activo')).toBeInTheDocument();
  });
});

