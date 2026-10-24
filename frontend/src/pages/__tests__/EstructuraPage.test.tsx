import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { EstructuraPage } from '../EstructuraPage';

// Mocks
const mockSuccess = vi.fn();
const mockError = vi.fn();
vi.mock('../../context/ToastContext', () => ({
  useToast: () => ({
    success: mockSuccess,
    error: mockError,
    warning: vi.fn(),
    info: vi.fn(),
  }),
}));

let mockUser: any = {
  id: '1',
  username: 'admin',
  rol: 'admin',
  nombre: 'Administrador',
};

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: true,
  }),
}));

const mockRedes = [
  { id: 1, nombre: 'Hebrón', is_active: 1, supervisor_id: 2, supervisor_nombre: 'Pedro Pérez' },
  { id: 2, nombre: 'Sur', is_active: 1, supervisor_id: 3, supervisor_nombre: 'María Gómez' },
];

const mockCasas = [
  {
    id: 10,
    codigo: 'HEB-001',
    anfitrion: 'Familia Mendoza',
    direccion: 'Calle Principal 10',
    telefono: '+584121111111',
    red_id: 1,
    red_nombre: 'Red Hebrón',
    is_active: 1,
    sin_reporte_7d: false,
    total_lideres: 2,
    asistencia: 15,
  },
  {
    id: 20,
    codigo: 'SUR-001',
    anfitrion: 'Familia Díaz',
    direccion: 'Avenida Bolívar 20',
    telefono: '+584142222222',
    red_id: 2,
    red_nombre: 'Red Sur',
    is_active: 1,
    sin_reporte_7d: true,
    total_lideres: 1,
    asistencia: 10,
  },
];

vi.mock('../../hooks/useDashboard', () => ({
  useRedes: () => ({
    redes: mockRedes,
    isLoading: false,
    refetch: vi.fn(),
  }),
  useCasasDePaz: () => ({
    casas: mockCasas,
    total: mockCasas.length,
    isLoading: false,
    refetch: vi.fn(),
  }),
}));

const mockCrearRed = vi.fn().mockResolvedValue({ success: true, message: 'Red creada' });
const mockEditarRed = vi.fn().mockResolvedValue({ success: true, message: 'Red actualizada' });
const mockToggleRed = vi.fn().mockResolvedValue({ success: true, message: 'Estado red cambiado' });
const mockEliminarRed = vi.fn().mockResolvedValue({ success: true, message: 'Red eliminada' });

const mockCrearCdp = vi.fn().mockResolvedValue({ success: true, message: 'CDP creada' });
const mockEditarCdp = vi.fn().mockResolvedValue({ success: true, message: 'CDP actualizada' });
const mockToggleCdp = vi.fn().mockResolvedValue({ success: true, message: 'Estado CDP cambiado' });
const mockEliminarCdp = vi.fn().mockResolvedValue({ success: true, message: 'CDP eliminada' });

vi.mock('../../hooks/useEstructura', () => ({
  useCdpDetalle: vi.fn(),
  useEstructuraSelectores: () => ({
    selectores: {
      supervisores: [{ id: 2, nombre: 'Pedro', apellido: 'Pérez', username: 'pperez' }],
      lideres_cdp: [{ id: 5, nombre: 'Juan', apellido: 'López', username: 'jlopez' }],
      casas_de_paz: [{ id: 10, codigo: 'HEB-001', anfitrion: 'Familia Mendoza' }],
      redes: mockRedes,
    },
    supervisores: [{ id: 2, nombre: 'Pedro', apellido: 'Pérez', username: 'pperez' }],
    lideresCdp: [{ id: 5, nombre: 'Juan', apellido: 'López', username: 'jlopez' }],
    redes: mockRedes,
  }),
  useEstructuraMutations: () => ({
    crearRed: mockCrearRed,
    isCreandoRed: false,
    editarRed: mockEditarRed,
    isEditandoRed: false,
    toggleRed: mockToggleRed,
    eliminarRed: mockEliminarRed,
    isEliminandoRed: false,
    crearCdp: mockCrearCdp,
    isCreandoCdp: false,
    editarCdp: mockEditarCdp,
    isEditandoCdp: false,
    toggleCdp: mockToggleCdp,
    eliminarCdp: mockEliminarCdp,
    isEliminandoCdp: false,
  }),
}));

describe('EstructuraPage Component (Paridad Jinja2 estructura_admin.html)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renderiza la estructura ministerial con aside de redes, tarjeta de impacto, banner semanal y tarjetas de casas', () => {
    render(
      <MemoryRouter initialEntries={['/estructura']}>
        <EstructuraPage />
      </MemoryRouter>
    );

    expect(screen.getByText('Estructura Organizacional')).toBeInTheDocument();
    expect(screen.getByText('Todas las redes')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Red Hebrón/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Red Sur/i })).toBeInTheDocument();

    // Tarjeta de Impacto
    expect(screen.getByText('Resumen de Impacto')).toBeInTheDocument();
    expect(screen.getByText('Casas de Paz registradas')).toBeInTheDocument();

    // Banner de pendientes
    expect(screen.getByText(/Reportes de la Semana Pendientes/i)).toBeInTheDocument();
    expect(screen.getByText(/1 pendiente/i)).toBeInTheDocument();

    // Tarjetas de Casas
    expect(screen.getByText('Casa "HEB-001"')).toBeInTheDocument();
    expect(screen.getByText('Casa "SUR-001"')).toBeInTheDocument();
    expect(screen.getByText('15 Asistentes promedio')).toBeInTheDocument();
  });

  it('soporta deep linking con parámetros de URL e interactúa con el buscador client-side', async () => {
    render(
      <MemoryRouter initialEntries={['/estructura?q=Mendoza&filtro=todas']}>
        <EstructuraPage />
      </MemoryRouter>
    );

    const input = screen.getByPlaceholderText(/Buscar por código, líder, anfitrión o zona/i) as HTMLInputElement;
    expect(input.value).toBe('Mendoza');

    // Debe mostrar la casa de los Mendoza y ocultar la de Díaz
    expect(screen.getByText('Casa "HEB-001"')).toBeInTheDocument();
    expect(screen.queryByText('Casa "SUR-001"')).not.toBeInTheDocument();

    // Si cambiamos la búsqueda
    fireEvent.change(input, { target: { value: 'Díaz' } });
    await waitFor(() => {
      expect(screen.getByText('Casa "SUR-001"')).toBeInTheDocument();
      expect(screen.queryByText('Casa "HEB-001"')).not.toBeInTheDocument();
    });
  });

  it('permite abrir el modal de Nueva Red y enviar el formulario de creación', async () => {
    render(
      <MemoryRouter initialEntries={['/estructura']}>
        <EstructuraPage />
      </MemoryRouter>
    );

    const btnNuevaRed = screen.getByRole('button', { name: /Nueva Red/i });
    fireEvent.click(btnNuevaRed);

    // Modal abierto
    expect(screen.getByText('Nueva Red Ministerial')).toBeInTheDocument();

    const inputNombre = screen.getByPlaceholderText(/Ej. Red de Crecimiento Norte/i);
    fireEvent.change(inputNombre, { target: { value: 'Red Betel' } });

    const btnGuardar = screen.getByRole('button', { name: 'Guardar Red' });
    fireEvent.click(btnGuardar);

    await waitFor(() => {
      expect(mockCrearRed).toHaveBeenCalledWith(
        expect.objectContaining({
          nombre: 'Red Betel',
        })
      );
    });
  });

  it('permite abrir el modal de Nueva Casa de Paz y registrar una casa con datos completos', async () => {
    render(
      <MemoryRouter initialEntries={['/estructura']}>
        <EstructuraPage />
      </MemoryRouter>
    );

    const btnNuevaCasa = screen.getByRole('button', { name: /Nueva Casa de Paz/i });
    fireEvent.click(btnNuevaCasa);

    expect(screen.getByText('Registrar Nueva Casa de Paz')).toBeInTheDocument();

    // Llenar campos
    fireEvent.change(screen.getByPlaceholderText(/Ej. SUR-001/i), { target: { value: 'SUR-002' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej. Familia Gómez Ríos/i), { target: { value: 'Familia Silva' } });
    fireEvent.change(screen.getByPlaceholderText(/0414-1234567/i), { target: { value: '+58 412 9999999' } });
    fireEvent.change(screen.getByPlaceholderText(/Calle, sector, punto de referencia/i), { target: { value: 'Calle 5 con Av 2' } });

    const btnSubmit = screen.getByRole('button', { name: 'Registrar Casa' });
    fireEvent.click(btnSubmit);

    await waitFor(() => {
      expect(mockCrearCdp).toHaveBeenCalledWith(
        expect.objectContaining({
          codigo: 'SUR-002',
          anfitrion: 'Familia Silva',
          telefono: '+58 412 9999999',
          direccion: 'Calle 5 con Av 2',
        })
      );
    });
  });

  it('el enlace Gestionar apunta a /casa-de-paz/:id', () => {
    render(
      <MemoryRouter initialEntries={['/estructura']}>
        <EstructuraPage />
      </MemoryRouter>
    );

    const linksGestionar = screen.getAllByRole('link', { name: /Gestionar/i });
    expect(linksGestionar[0]).toHaveAttribute('href', '/casa-de-paz/10');
    expect(linksGestionar[1]).toHaveAttribute('href', '/casa-de-paz/20');
  });

  it('no muestra la tarjeta Registrar Nueva Casa en Todas las redes pero si al seleccionar una red especifica', async () => {
    render(
      <MemoryRouter initialEntries={['/estructura']}>
        <EstructuraPage />
      </MemoryRouter>
    );

    // En "Todas las redes" la tarjeta no debe estar presente en la cuadrícula
    expect(screen.queryByRole('heading', { name: /Registrar Nueva Casa/i })).not.toBeInTheDocument();

    // Seleccionar Red Hebrón
    const btnRedHebron = screen.getByRole('button', { name: /Red Hebrón/i });
    fireEvent.click(btnRedHebron);

    // Ahora sí debe mostrarse la tarjeta Registrar Nueva Casa
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Registrar Nueva Casa/i })).toBeInTheDocument();
    });

    // Y las demás redes deben seguir mostrando su conteo de casas en el sidebar
    expect(screen.getByRole('button', { name: /Red Sur/i })).toHaveTextContent(/1 Casa Vinculada/i);
  });

  it('aplica la clase menu-open a la tarjeta de red cuando se abre su menu de opciones', async () => {
    render(
      <MemoryRouter initialEntries={['/estructura']}>
        <EstructuraPage />
      </MemoryRouter>
    );

    const btnOpciones = screen.getByRole('button', { name: /Opciones de Hebrón/i });
    fireEvent.click(btnOpciones);

    // El menú debe desplegarse
    expect(screen.getByText('Editar red')).toBeInTheDocument();
    expect(screen.getByText('Poner en pausa')).toBeInTheDocument();
    expect(screen.getByText('Eliminar red')).toBeInTheDocument();

    // La tarjeta contenedora debe tener la clase menu-open para elevarse en el stacking context
    const cardHebron = btnOpciones.closest('.red-card');
    expect(cardHebron).toHaveClass('menu-open');
  });

  it('permite abrir el menu de opciones por portal en desktop y el bottom sheet contextual en móvil', async () => {
    render(
      <MemoryRouter initialEntries={['/estructura?red_id=1']}>
        <EstructuraPage />
      </MemoryRouter>
    );

    // En vista con red_id=1 seleccionada, debe estar el botón contextual móvil
    const btnMobileOpciones = screen.getByRole('button', { name: /Gestionar Hebrón/i });
    expect(btnMobileOpciones).toBeInTheDocument();

    // Al pulsar el botón contextual se abre el Bottom Sheet
    fireEvent.click(btnMobileOpciones);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Red Hebrón' })).toBeInTheDocument();
    expect(screen.getByText('Editar red')).toBeInTheDocument();

    // Cerrar bottom sheet
    const btnCancelar = screen.getByRole('button', { name: /Cancelar/i });
    fireEvent.click(btnCancelar);
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });
});
