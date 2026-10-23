import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { DashboardPage } from '../DashboardPage';

// Mocks de hooks
const mockUser = {
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
  { id: 1, nombre: 'Red Hebrón', is_active: 1 },
  { id: 2, nombre: 'Red Sur', is_active: 1 },
];

let mockCasasData: any[] = [
  { id: 10, codigo: 'HEB-001', red_id: 1, anfitrion: 'Familia Gómez', is_active: 1 },
];

let mockMetricasData: any = {};
let mockIsLoading = false;
let mockIsError = false;

vi.mock('../../hooks/useDashboard', () => ({
  useDashboard: () => ({
    metricas: mockMetricasData,
    isLoading: mockIsLoading,
    isError: mockIsError,
    error: null,
    refetch: vi.fn(),
  }),
  useRedes: () => ({
    redes: mockRedes,
    isLoading: false,
  }),
  useCasasDePaz: () => ({
    casas: mockCasasData,
    isLoading: false,
  }),
}));

describe('DashboardPage Component (Paridad Estructural Jinja)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockIsLoading = false;
    mockIsError = false;
    mockCasasData = [
      { id: 10, codigo: 'HEB-001', red_id: 1, anfitrion: 'Familia Gómez', is_active: 1 },
    ];
    mockMetricasData = {
      total_asistencia: 150,
      total_casas: 10,
      casas_con_reporte: 8,
      cumplimiento: 80,
      ofrendas_usd: 300,
      ofrendas_bs: 10000,
      conversiones: 12,
      reconciliaciones: 5,
      cestas_amor: 3,
      total_visitas: 18,
      distribucion: { regulares: 80, ninos: 30, visitas: 25, comprometidos: 15 },
      ranking_redes: [
        { nombre: 'Red Hebrón', supervisor: 'Pedro G', cumplimiento: 90, asistencia: 70 }
      ],
      alertas: [
        { nombre: 'Casa Betel', codigo: 'HEB-001', red: 'Red Hebrón', dias_sin_reporte: 18, motivo: 'Sin reporte >2 semanas', lider: 'Juan Pérez' }
      ],
      tendencia_semanas: [
        { semana: 'Sem 1', asistencia: 120, porcentaje: 80 }
      ],
    };
  });

  it('renderiza la estructura de dos columnas en Vista General con Donut completo y Fruto en sidebar', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    // Encabezado
    expect(screen.getByText('Panel Administrativo')).toBeInTheDocument();

    // 4 KPIs principales
    expect(screen.getByText('Total Asistencia')).toBeInTheDocument();
    expect(screen.getByText('Cumplimiento Semanal')).toBeInTheDocument();
    expect(screen.getByText('Ofrendas Acumuladas')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Confesiones de Fe' })).toBeInTheDocument();

    // Gráficas y tarjetas de soporte
    expect(screen.getByText('Distribución por Categoría')).toBeInTheDocument();
    expect(screen.getByText('Alertas de Seguimiento')).toBeInTheDocument();
    expect(screen.getByText('Ranking de Redes')).toBeInTheDocument();
    expect(screen.getByText('Fruto y Transformación')).toBeInTheDocument();
  });

  it('renderiza la estructura de Vista Por Red con actividad reciente y sidebar zonal', () => {
    mockMetricasData = {
      ...mockMetricasData,
      nombre_red: 'Red Hebrón',
      supervisor: 'Pedro González',
      casas_activas: 4,
      asistencia_total: 60,
      promedio_casa: 15,
      actividad_reciente: [
        { cdp_codigo: 'HEB-001', lider: 'Juan Pérez', cdp_nombre: 'Betel', asistencia: 18, tema: 'Fe viva' }
      ],
      top_crecimiento: { nombre: 'Casa Betel', codigo: 'HEB-001', tasa: '+15%', visitas: 6, lider: 'Juan Pérez' },
      lideres_red: [{ nombre: 'Juan Pérez', rol: 'Líder', cdp_codigo: 'HEB-001' }]
    };

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    // Cambiar a nivel Red en el filtro
    const nivelSelect = screen.getByLabelText('Seleccionar nivel de vista del panel');
    fireEvent.change(nivelSelect, { target: { value: 'red' } });

    expect(screen.getByText('Actividad Reciente')).toBeInTheDocument();
    expect(screen.getByText('Top Crecimiento')).toBeInTheDocument();
    expect(screen.getByText('Líderes de la Red')).toBeInTheDocument();
    expect(screen.getByText('Alertas Zonal')).toBeInTheDocument();
  });

  it('muestra el estado vacío "Sin Casas de Paz Asignadas" cuando se selecciona nivel cdp sin casas', () => {
    mockCasasData = [];
    mockMetricasData = {
      nombre_red: 'Red Sur',
      casas: [],
      historial: [],
    };

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    const nivelSelect = screen.getByLabelText('Seleccionar nivel de vista del panel');
    fireEvent.change(nivelSelect, { target: { value: 'cdp' } });

    // Cuando cdpId está vacío
    expect(screen.getByText('Sin Casas de Paz Asignadas')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Ver Vista Zonal/i })).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /Estructura y Redes/i }).length).toBeGreaterThanOrEqual(2);
  });
});
