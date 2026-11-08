import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { DashboardPage } from '../DashboardPage';

// Mocks
let mockUser: any = {
  id: 'lider-uuid-1',
  username: 'lider1',
  rol: 'lider_cdp',
  nombre: 'Hermano Pedro',
};

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: true,
  }),
}));

const mockLiderDashboardData: any = {
  cdp: {
    id: 1,
    codigo: 'CDP-01',
    anfitrion: 'Familia Pérez',
  },
  lideres: [
    { id: 1, nombre: 'Pedro', apellido: 'Pérez', rol: 'Lider' },
    { id: 2, nombre: 'María', apellido: 'Gómez', rol: 'Sublider' },
  ],
  metricas: {
    total_reportes: 3,
    asistencia_promedio: 15.0,
    ofrendas_usd_totales: 75.5,
    ofrendas_bs_totales: 3100.0,
    visitas_totales: 6,
    conversiones_totales: 2,
    reconciliaciones_totales: 1,
    reporte_esta_semana: true,
    dias_cierre_texto: 'Próximo cierre: Domingo 6:00 PM',
  },
  reportes: [
    {
      id: 'rep-1',
      fecha: '2026-11-01',
      fecha_formateada: '01 Nov 2026',
      hr_inicio: '18:00',
      hr_fin: '19:30',
      lider_nombre: 'Pedro Pérez',
      enviado_por_lider_id: 1,
      iniciales: 'PP',
      tema: 'Caminando sobre las Aguas',
      asistencia: 15,
      nro_regulares: 10,
      nro_niños: 2,
      nro_visitas: 2,
      nro_comprometidos: 1,
      reconciliaciones: 1,
      confesiones: 2,
      ofrendas_usd: 25.5,
      ofrendas_bs: 1000.0,
      cesta_amor: 'Sí',
      observaciones: 'Gran reunión con visitas nuevas',
    },
  ],
  total_reportes: 3,
  currentPage: 1,
  totalPages: 1,
  tieneCdp: true,
  isLoading: false,
  isError: false,
  error: null,
  refetch: vi.fn(),
};

let currentHookData = { ...mockLiderDashboardData };

vi.mock('../../hooks/useLiderDashboard', () => ({
  useLiderDashboard: () => currentHookData,
}));

vi.mock('../../api/client', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn().mockResolvedValue({ success: true }),
    delete: vi.fn().mockResolvedValue({ success: true }),
  },
}));

describe('LiderDashboardView Integration and Parity Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUser = {
      id: 'lider-uuid-1',
      username: 'lider1',
      rol: 'lider_cdp',
      nombre: 'Hermano Pedro',
    };
    currentHookData = { ...mockLiderDashboardData, refetch: vi.fn() };
  });

  const renderDashboard = () => {
    return render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );
  };

  it('renderiza la cabecera del líder con saludo y tag de Casa de Paz', () => {
    renderDashboard();

    expect(screen.getByRole('heading', { name: 'Panel de Casa de Paz' })).toBeInTheDocument();
    expect(screen.getByText(/Bienvenido,/i)).toBeInTheDocument();
    expect(screen.getByText(/Hermano Pedro/i)).toBeInTheDocument();
    expect(screen.getByTestId('cdp-tag')).toHaveTextContent('CDP-01 · Familia Pérez');
  });

  it('renderiza las 4 tarjetas KPI con datos consolidados y marcas de agua', () => {
    renderDashboard();

    const actionCard = screen.getByTestId('action-nuevo-reporte');
    expect(actionCard).toBeInTheDocument();
    expect(actionCard).toHaveTextContent('Nuevo Reporte');

    const misReportesCard = screen.getByTestId('card-mis-reportes');
    expect(misReportesCard).toHaveTextContent('3');

    const asistenciaCard = screen.getByTestId('card-asistencia-promedio');
    expect(asistenciaCard).toHaveTextContent('15.0');

    const ofrendasCard = screen.getByTestId('card-ofrendas-totales');
    expect(ofrendasCard).toHaveTextContent('$75.50');
    expect(ofrendasCard).toHaveTextContent('Bs. 3,100.00');
  });

  it('renderiza la tabla de historial con columnas, badges y botones de acción', () => {
    renderDashboard();

    expect(screen.getByText('Últimos Reportes')).toBeInTheDocument();
    expect(screen.getByText('Caminando sobre las Aguas')).toBeInTheDocument();
    
    const row = screen.getByTestId('reporte-row-rep-1');
    expect(row).toHaveTextContent('Pedro Pérez');
    expect(row).toHaveTextContent('01 Nov 2026');
    expect(row).toHaveTextContent('$25.50');

    expect(screen.getByTestId('btn-view-rep-1')).toBeInTheDocument();
    expect(screen.getByTestId('btn-edit-rep-1')).toBeInTheDocument();
    expect(screen.getByTestId('btn-delete-rep-1')).toBeInTheDocument();
  });

  it('renderiza la barra lateral con recordatorio de domingo y el equipo de líderes', () => {
    renderDashboard();

    expect(screen.getByTestId('reminder-card')).toHaveTextContent(
      'Recuerda subir tus reportes antes del domingo a las 6:00 PM'
    );
    expect(screen.getByTestId('reminder-card')).toHaveTextContent(
      'Próximo cierre: Domingo 6:00 PM'
    );

    const teamCard = screen.getByTestId('team-card');
    expect(teamCard).toHaveTextContent('Mi Equipo');
    expect(teamCard).toHaveTextContent('Pedro Pérez');
    expect(teamCard).toHaveTextContent('Lider');
    expect(teamCard).toHaveTextContent('María Gómez');
    expect(teamCard).toHaveTextContent('Sublider');
  });

  it('renderiza estado vacío cuando no existen reportes registrados', () => {
    currentHookData = {
      ...mockLiderDashboardData,
      reportes: [],
      total_reportes: 0,
    };

    renderDashboard();

    expect(screen.getByTestId('lider-empty-state')).toBeInTheDocument();
    expect(screen.getByText(/Parece que aún no has comenzado/i)).toBeInTheDocument();
    expect(screen.getByTestId('btn-primer-reporte')).toBeInTheDocument();
  });

  it('renderiza mensaje instructivo cuando el líder no tiene Casa de Paz asignada', () => {
    currentHookData = {
      ...mockLiderDashboardData,
      tieneCdp: false,
      cdp: null,
    };

    renderDashboard();

    expect(screen.getByTestId('lider-sin-cdp')).toBeInTheDocument();
    expect(screen.getByText('Sin Casa de Paz Asignada')).toBeInTheDocument();
  });

  it('abre y visualiza el modal de detalle completo del reporte', () => {
    renderDashboard();

    fireEvent.click(screen.getByTestId('btn-view-rep-1'));

    expect(screen.getByRole('heading', { name: 'Detalle de la Reunión' })).toBeInTheDocument();
    expect(screen.getByTestId('lider-modal-detalle-body')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Caminando sobre las Aguas')).toBeInTheDocument();
    expect(screen.getByDisplayValue('$ 25.50')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('btn-cerrar-detalle'));
  });

  it('abre el modal de edición y permite modificar valores', async () => {
    renderDashboard();

    fireEvent.click(screen.getByTestId('btn-edit-rep-1'));

    expect(screen.getByRole('heading', { name: 'Editar Reporte Semanal' })).toBeInTheDocument();
    const temaInput = screen.getByDisplayValue('Caminando sobre las Aguas');
    fireEvent.change(temaInput, { target: { value: 'Tema Actualizado' } });
    expect(screen.getByDisplayValue('Tema Actualizado')).toBeInTheDocument();

    const guardarBtn = screen.getByTestId('btn-guardar-editar');
    fireEvent.click(guardarBtn);

    await waitFor(() => {
      expect(currentHookData.refetch).toHaveBeenCalled();
    });
  });

  it('soporta cesta_amor como valor numerico (1 o 0) de la BD sin fallar con toLowerCase', () => {
    currentHookData = {
      ...mockLiderDashboardData,
      reportes: [
        {
          ...mockLiderDashboardData.reportes[0],
          id: 'rep-num',
          cesta_amor: 1, // Numerico de MySQL
        },
      ],
      refetch: vi.fn(),
    };

    renderDashboard();

    // Abrir detalle
    fireEvent.click(screen.getByTestId('btn-view-rep-num'));
    expect(screen.getByDisplayValue('Sí')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('btn-cerrar-detalle'));

    // Abrir edicion
    fireEvent.click(screen.getByTestId('btn-edit-rep-num'));
    expect(screen.getByRole('heading', { name: 'Editar Reporte Semanal' })).toBeInTheDocument();
    expect(screen.getByLabelText(/¿Cesta de Amor\?/i)).toHaveValue('1');
  });

  it('abre el modal de eliminación y confirma el borrado', async () => {
    renderDashboard();

    fireEvent.click(screen.getByTestId('btn-delete-rep-1'));

    expect(screen.getByRole('heading', { name: 'Eliminar Reporte' })).toBeInTheDocument();
    expect(
      screen.getByText('¿Estás seguro de que deseas eliminar este reporte semanal?')
    ).toBeInTheDocument();

    const confirmarBtn = screen.getByTestId('btn-confirmar-eliminar');
    fireEvent.click(confirmarBtn);

    await waitFor(() => {
      expect(currentHookData.refetch).toHaveBeenCalled();
    });
  });
});
