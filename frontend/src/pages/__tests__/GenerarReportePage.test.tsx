import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { GenerarReportePage } from '../GenerarReportePage';

// Mocks
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useSearchParams: () => [new URLSearchParams()],
  };
});

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

const mockUser = {
  id: '1',
  username: 'lider_betel',
  rol: 'lider_cdp',
  nombre: 'Carlos',
  apellido: 'Mendoza',
};

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: true,
  }),
}));

let mockPerfilData: any = {
  id: 1,
  username: 'lider_betel',
  nombre: 'Carlos',
  apellido: 'Mendoza',
  tipo_usuario: 'lider_cdp',
  cdp_id: 10,
  cdp_codigo: 'HEB-001',
  cdp_nombre: 'Betel',
};

vi.mock('../../hooks/usePerfil', () => ({
  usePerfil: () => ({
    perfil: mockPerfilData,
    usuario: 'lider_betel',
    rol: 'lider_cdp',
    isLoading: false,
    isError: false,
    refetch: vi.fn(),
  }),
}));

const mockLideres = [
  { id: 101, nombre: 'Carlos', apellido: 'Mendoza', rol: 'Líder', is_active: 1 },
  { id: 102, nombre: 'Ana', apellido: 'Gómez', rol: 'Sublíder', is_active: 1 },
];

vi.mock('../../hooks/useDashboard', () => ({
  useCasasDePaz: () => ({
    casas: [{ id: 10, codigo: 'HEB-001', nombre: 'Betel', red_id: 1, is_active: 1 }],
    isLoading: false,
  }),
  useLideres: () => ({
    lideres: mockLideres,
    isLoading: false,
  }),
}));

let mockCrearReporte = vi.fn();
let mockIsCreando = false;

vi.mock('../../hooks/useReportes', () => ({
  useReportes: () => ({
    crearReporte: mockCrearReporte,
    isCreando: mockIsCreando,
  }),
}));

describe('GenerarReportePage (Paridad 1 a 1 Jinja2)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockIsCreando = false;
    mockPerfilData = {
      id: 1,
      username: 'lider_betel',
      nombre: 'Carlos',
      apellido: 'Mendoza',
      tipo_usuario: 'lider_cdp',
      cdp_id: 10,
      cdp_codigo: 'HEB-001',
      cdp_nombre: 'Betel',
    };
    mockCrearReporte = vi.fn().mockResolvedValue({ success: true, message: 'OK' });
  });

  it('renderiza la estructura canónica con badge de Casa de Paz y 4 secciones', () => {
    render(
      <MemoryRouter>
        <GenerarReportePage />
      </MemoryRouter>
    );

    // Título y Descripción
    expect(screen.getByRole('heading', { name: /generar reporte/i })).toBeInTheDocument();
    expect(
      screen.getByText(/registra los datos y estadísticas de la reunión semanal/i)
    ).toBeInTheDocument();

    // Context Badge con Código y Nombre
    expect(screen.getByText('HEB-001')).toBeInTheDocument();
    expect(screen.getByText(/Betel/)).toBeInTheDocument();

    // Sección 1: Datos de la Reunión
    expect(screen.getByText(/datos de la reunión/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/líder que reporta/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/fecha \(hoy\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/hora de inicio/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/hora de finalización/i)).toBeInTheDocument();

    // Sección 2: Asistencia
    expect(screen.getByText('Asistencia')).toBeInTheDocument();
    expect(screen.getByLabelText(/regulares/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/niños/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/visitas/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/comprometidos/i)).toBeInTheDocument();

    // Sección 3: Frutos y Ofrendas
    expect(screen.getByText('Ministerio')).toBeInTheDocument();
    expect(screen.getByLabelText(/reconciliaciones/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confesiones de fe/i)).toBeInTheDocument();
    expect(screen.getByText('Ofrendas y Recursos')).toBeInTheDocument();
    expect(screen.getByLabelText(/bs\./i)).toBeInTheDocument();
    expect(screen.getByLabelText(/usd \(\$\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/¿cesta\?/i)).toBeInTheDocument();

    // Sección 4: Tema y Observaciones
    expect(screen.getByText('Tema y Observaciones')).toBeInTheDocument();
    expect(screen.getByLabelText(/tema de la clase/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/observaciones/i)).toBeInTheDocument();

    // Botones de acción
    expect(screen.getByRole('button', { name: /enviar reporte/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
  });

  it('calcula la Asistencia Total de forma reactiva en tiempo real', () => {
    render(
      <MemoryRouter>
        <GenerarReportePage />
      </MemoryRouter>
    );

    const badgeTotal = document.getElementById('badge-total-asistencia');
    expect(badgeTotal?.textContent).toBe('0');

    const inputRegulares = screen.getByLabelText(/regulares/i);
    const inputNinos = screen.getByLabelText(/niños/i);
    const inputVisitas = screen.getByLabelText(/visitas/i);
    const inputComprometidos = screen.getByLabelText(/comprometidos/i);

    fireEvent.change(inputRegulares, { target: { value: '12' } });
    expect(badgeTotal?.textContent).toBe('12');

    fireEvent.change(inputNinos, { target: { value: '4' } });
    expect(badgeTotal?.textContent).toBe('16');

    fireEvent.change(inputVisitas, { target: { value: '3' } });
    expect(badgeTotal?.textContent).toBe('19');

    fireEvent.change(inputComprometidos, { target: { value: '5' } });
    expect(badgeTotal?.textContent).toBe('24');
  });

  it('valida que la hora de fin sea estrictamente posterior a la hora de inicio', async () => {
    render(
      <MemoryRouter>
        <GenerarReportePage />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/hora de inicio/i), { target: { value: '18:00' } });
    fireEvent.change(screen.getByLabelText(/hora de finalización/i), { target: { value: '17:30' } });
    fireEvent.change(screen.getByLabelText(/regulares/i), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText(/tema de la clase/i), { target: { value: 'Poder de Dios' } });
    fireEvent.change(screen.getByLabelText(/bs\./i), { target: { value: '50' } });
    fireEvent.change(screen.getByLabelText(/usd \(\$\)/i), { target: { value: '5' } });

    fireEvent.click(screen.getByRole('button', { name: /enviar reporte/i }));

    expect(mockError).toHaveBeenCalledWith(
      'La hora de finalización debe ser posterior a la hora de inicio.'
    );
    expect(mockCrearReporte).not.toHaveBeenCalled();
  });

  it('rechaza el envío si el total de asistencia es 0', async () => {
    render(
      <MemoryRouter>
        <GenerarReportePage />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/hora de inicio/i), { target: { value: '17:00' } });
    fireEvent.change(screen.getByLabelText(/hora de finalización/i), { target: { value: '18:30' } });
    fireEvent.change(screen.getByLabelText(/tema de la clase/i), { target: { value: 'Gracia y Verdad' } });
    fireEvent.change(screen.getByLabelText(/bs\./i), { target: { value: '100' } });
    fireEvent.change(screen.getByLabelText(/usd \(\$\)/i), { target: { value: '10' } });

    fireEvent.click(screen.getByRole('button', { name: /enviar reporte/i }));

    expect(mockError).toHaveBeenCalledWith(
      'Debes registrar al menos un asistente en la reunión.'
    );
    expect(mockCrearReporte).not.toHaveBeenCalled();
  });

  it('envía el payload ministerial canónico y redirige al dashboard del líder', async () => {
    render(
      <MemoryRouter>
        <GenerarReportePage />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/hora de inicio/i), { target: { value: '17:00' } });
    fireEvent.change(screen.getByLabelText(/hora de finalización/i), { target: { value: '18:30' } });
    fireEvent.change(screen.getByLabelText(/líder que reporta/i), { target: { value: '101' } });

    // Asistencia
    fireEvent.change(screen.getByLabelText(/regulares/i), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText(/niños/i), { target: { value: '3' } });
    fireEvent.change(screen.getByLabelText(/visitas/i), { target: { value: '2' } });
    fireEvent.change(screen.getByLabelText(/comprometidos/i), { target: { value: '5' } });

    // Frutos
    fireEvent.change(screen.getByLabelText(/reconciliaciones/i), { target: { value: '1' } });
    fireEvent.change(screen.getByLabelText(/confesiones de fe/i), { target: { value: '2' } });

    // Finanzas
    fireEvent.change(screen.getByLabelText(/bs\./i), { target: { value: '120.50' } });
    fireEvent.change(screen.getByLabelText(/usd \(\$\)/i), { target: { value: '15.00' } });
    fireEvent.change(screen.getByLabelText(/¿cesta\?/i), { target: { value: '1' } });

    // Tema y Observaciones
    fireEvent.change(screen.getByLabelText(/tema de la clase/i), { target: { value: 'El poder del perdón' } });
    fireEvent.change(screen.getByLabelText(/observaciones/i), {
      target: { value: 'Hermoso tiempo de compañerismo.' },
    });

    fireEvent.click(screen.getByRole('button', { name: /enviar reporte/i }));

    await waitFor(() => {
      expect(mockCrearReporte).toHaveBeenCalledWith(
        expect.objectContaining({
          cdp_id: 10,
          lider_id: 101,
          hr_inicio: '17:00',
          hr_fin: '18:30',
          tema: 'El poder del perdón',
          nro_regulares: 10,
          nro_ninos: 3,
          nro_visitas: 2,
          nro_comprometidos: 5,
          reconciliaciones: 1,
          confesiones: 2,
          cesta_amor: 1,
          ofrendas_bs: 120.5,
          ofrendas_usd: 15,
          observaciones: 'Hermoso tiempo de compañerismo.',
        })
      );
    });

    expect(mockSuccess).toHaveBeenCalledWith('¡Reporte ministerial registrado exitosamente!');
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('el botón Cancelar redirige al dashboard ministerial', () => {
    render(
      <MemoryRouter>
        <GenerarReportePage />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /cancelar/i }));
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('muestra estado institucional bloqueado cuando el líder no tiene Casa de Paz asignada', () => {
    mockPerfilData = {
      id: 1,
      username: 'lider_sin_cdp',
      tipo_usuario: 'lider_cdp',
      cdp_id: undefined,
    };

    render(
      <MemoryRouter>
        <GenerarReportePage />
      </MemoryRouter>
    );

    expect(screen.getByText('Sin Casa de Paz Asignada')).toBeInTheDocument();
    expect(
      screen.getByText(/tu cuenta de líder ministerial aún no tiene una casa de paz vinculada/i)
    ).toBeInTheDocument();

    const btnVolver = screen.getByRole('button', { name: /volver al dashboard/i });
    expect(btnVolver).toBeInTheDocument();

    fireEvent.click(btnVolver);
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });
});
