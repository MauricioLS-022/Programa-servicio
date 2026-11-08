import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { LideresPage } from '../LideresPage';
import type { Lider } from '../../types/estructura';

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
  }),
}));

let mockPerfil = {
  id: 'usr-sup-1',
  username: 'sup1',
  nombre: 'Supervisor',
  apellido: 'Regional',
  tipo_usuario: 'supervisor',
  red_id: 1,
  red_nombre: 'Red Este',
};

vi.mock('../../hooks/usePerfil', () => ({
  usePerfil: () => ({
    perfil: mockPerfil,
    usuario: mockPerfil.username,
    rol: mockCurrentUser.rol,
    isLoading: false,
    isError: false,
  }),
}));

const mockLideresList: Lider[] = [
  {
    id: 101,
    nombre: 'Carlos',
    apellido: 'Mendoza',
    rol: 'Lider',
    red_id: 1,
    red_nombre: 'Red Este',
    cdp_id: 10,
    cdp_codigo: 'EST-01',
    telefono: '+58 412 1234567',
    is_active: 1,
  },
  {
    id: 102,
    nombre: 'Ana',
    apellido: 'Salazar',
    rol: 'Sublider',
    red_id: 1,
    red_nombre: 'Red Este',
    cdp_id: 10,
    cdp_codigo: 'EST-01',
    telefono: '+58 414 9876543',
    is_active: 1,
  },
  {
    id: 103,
    nombre: 'Pedro',
    apellido: 'Gómez',
    rol: 'Lider',
    red_id: 2,
    red_nombre: 'Red Oeste',
    cdp_id: 20,
    cdp_codigo: 'OES-01',
    telefono: '+58 416 1112233',
    is_active: 0,
  },
];

const mockCrearLider = vi.fn();
const mockEditarLider = vi.fn();
const mockToggleLider = vi.fn().mockResolvedValue({ success: true, message: 'Estado alternado' });
const mockEliminarLider = vi.fn().mockResolvedValue({ success: true, message: 'Líder eliminado' });

vi.mock('../../hooks/useLideres', () => ({
  useLideres: () => ({
    lideres: mockLideresList,
    total: mockLideresList.length,
    page: 1,
    pages: 1,
    isLoading: false,
    isError: false,
    error: null,
    refetch: vi.fn(),
  }),
  useLiderMutations: () => ({
    crearLider: mockCrearLider,
    isCreando: false,
    editarLider: mockEditarLider,
    isEditando: false,
    toggleLider: mockToggleLider,
    isToggling: false,
    eliminarLider: mockEliminarLider,
    isEliminando: false,
  }),
}));

vi.mock('../../hooks/useEstructura', () => ({
  useEstructuraSelectores: () => ({
    redes: [
      { id: 1, nombre: 'Red Este' },
      { id: 2, nombre: 'Red Oeste' },
    ],
    casasDePaz: [
      { id: 10, codigo: 'EST-01', anfitrion: 'Familia Mendoza', red_id: 1 },
      { id: 20, codigo: 'OES-01', anfitrion: 'Familia Gómez', red_id: 2 },
    ],
    isLoading: false,
    isError: false,
  }),
}));

describe('LideresPage Component', () => {
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

  it('renderiza la cabecera, la cita bíblica y la lista de líderes', () => {
    render(
      <MemoryRouter>
        <LideresPage />
      </MemoryRouter>
    );

    expect(screen.getByText('Directorio de Liderazgo')).toBeInTheDocument();
    expect(screen.getByText(/Porque donde están dos o tres congregados en mi nombre/i)).toBeInTheDocument();
    expect(screen.getByText('Mateo 18:20')).toBeInTheDocument();

    expect(screen.getByText('Carlos Mendoza')).toBeInTheDocument();
    expect(screen.getByText('Ana Salazar')).toBeInTheDocument();
    expect(screen.getByText('Pedro Gómez')).toBeInTheDocument();
  });

  it('renderiza enlaces normalizados a WhatsApp (wa.me) con el número telefónico', () => {
    render(
      <MemoryRouter>
        <LideresPage />
      </MemoryRouter>
    );

    const waLinks = screen.getAllByRole('link', { name: /WhatsApp/i });
    expect(waLinks.length).toBeGreaterThan(0);
    expect(waLinks[0]).toHaveAttribute('href', 'https://wa.me/584121234567');
  });

  it('filtra líderes en tiempo real con Live Search instantáneo client-side', () => {
    render(
      <MemoryRouter>
        <LideresPage />
      </MemoryRouter>
    );

    const searchInput = screen.getByPlaceholderText('Buscar por nombre o teléfono...');
    fireEvent.change(searchInput, { target: { value: 'Salazar' } });

    expect(screen.getByText('Ana Salazar')).toBeInTheDocument();
    expect(screen.queryByText('Carlos Mendoza')).not.toBeInTheDocument();
    expect(screen.queryByText('Pedro Gómez')).not.toBeInTheDocument();
  });

  it('aplica aislamiento territorial cuando el usuario es supervisor', () => {
    mockCurrentUser = {
      id: 'usr-sup-1',
      username: 'sup1',
      rol: 'supervisor',
      nombre: 'Supervisor',
      apellido: 'Regional',
    };

    render(
      <MemoryRouter>
        <LideresPage />
      </MemoryRouter>
    );

    // Debe mostrar la red asignada del supervisor como badge/fijada sin selector de otras redes
    expect(screen.getAllByText('Red Este').length).toBeGreaterThan(0);
    expect(screen.getByText('Supervisión')).toBeInTheDocument();

    // Solo líderes de Red Este visibles por aislamiento
    expect(screen.getByText('Carlos Mendoza')).toBeInTheDocument();
    expect(screen.getByText('Ana Salazar')).toBeInTheDocument();
    expect(screen.queryByText('Pedro Gómez')).not.toBeInTheDocument();
  });

  it('solicita confirmación estricta escribiendo ELIMINAR para dar de baja a un líder', async () => {
    render(
      <MemoryRouter>
        <LideresPage />
      </MemoryRouter>
    );

    const deleteButtons = screen.getAllByTitle('Eliminar Líder');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Confirmar Eliminación')).toBeInTheDocument();
    });

    const confirmBtn = screen.getByRole('button', { name: /^Eliminar$/i });
    expect(confirmBtn).toBeDisabled();

    const inputConfirm = screen.getByPlaceholderText('ELIMINAR');
    fireEvent.change(inputConfirm, { target: { value: 'ELIMINAR' } });

    expect(confirmBtn).not.toBeDisabled();
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(mockEliminarLider).toHaveBeenCalledWith(101);
    });
  });
});


