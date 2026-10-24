import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { ReportesPage } from '../ReportesPage';
import type { Reporte } from '../../types/reporte';

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
  { id: 1, nombre: 'Red Hebrón', is_active: 1 },
  { id: 2, nombre: 'Red Sur', is_active: 1 },
];

const mockCasas = [
  { id: 10, codigo: 'HEB-001', nombre: 'Betel', red_id: 1, is_active: 1 },
  { id: 20, codigo: 'SUR-001', nombre: 'Antioquía', red_id: 2, is_active: 1 },
];

vi.mock('../../hooks/useDashboard', () => ({
  useRedes: () => ({
    redes: mockRedes,
    isLoading: false,
  }),
  useCasasDePaz: () => ({
    casas: mockCasas,
    isLoading: false,
  }),
}));

const mockReporteItem: Reporte = {
  id: 'rep-uuid-1',
  cdp_id: 10,
  cdp_codigo: 'HEB-001',
  cdp_nombre: 'Betel',
  red_id: 1,
  red_nombre: 'Red Hebrón',
  fecha: '2026-10-23',
  fecha_formateada: '23/10/2026',
  lider_nombre: 'Carlos Mendoza',
  iniciales: 'CM',
  hr_inicio: '18:00',
  hr_fin: '19:30',
  tema: 'La fe victoriosa',
  nro_regulares: 12,
  nro_ninos: 4,
  nro_visitas: 3,
  nro_comprometidos: 5,
  asistencia: 24,
  reconciliaciones: 1,
  confesiones: 2,
  ofrendas_usd: 25.5,
  ofrendas_bs: 1500.0,
  cesta_amor: 1,
  observaciones: 'Excelente tiempo en la reunión.',
};

let mockReportesList: Reporte[] = [mockReporteItem];
let mockActualizarReporte = vi.fn();
let mockEliminarReporte = vi.fn();
let mockIsLoading = false;
let mockIsActualizando = false;
let mockIsEliminando = false;
let lastReportesArgs: any = null;

vi.mock('../../hooks/useReportes', () => ({
  useReportes: (args: any) => {
    lastReportesArgs = args;
    return {
      reportes: mockReportesList,
      total: mockReportesList.length,
      pages: 1,
      page: 1,
      isLoading: mockIsLoading,
      actualizarReporte: mockActualizarReporte,
      isActualizando: mockIsActualizando,
      eliminarReporte: mockEliminarReporte,
      isEliminando: mockIsEliminando,
      refetch: vi.fn(),
    };
  },
}));

describe('ReportesPage (Paridad 1 a 1 reportes_admin.html)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUser = {
      id: '1',
      username: 'admin',
      rol: 'admin',
      nombre: 'Administrador',
    };
    mockReportesList = [mockReporteItem];
    mockIsLoading = false;
    mockIsActualizando = false;
    mockIsEliminando = false;
    mockActualizarReporte = vi.fn().mockResolvedValue({ success: true, message: 'OK' });
    mockEliminarReporte = vi.fn().mockResolvedValue({ success: true, message: 'OK' });
  });

  it('renderiza la vista para Administrador con filtros completos de Red y Casa de Paz y sin botón de agregar reporte (paridad Jinja2)', () => {
    render(
      <MemoryRouter>
        <ReportesPage />
      </MemoryRouter>
    );

    // Hero title
    expect(screen.getByText('Reportes de Administración')).toBeInTheDocument();

    // Filtros
    expect(screen.getByLabelText(/buscar/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/red ministerial/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/casa de paz/i)).toBeInTheDocument();
    expect(screen.getByText('Todas las redes')).toBeInTheDocument();
    expect(screen.getByText('Todas las casas')).toBeInTheDocument();

    // El botón Cargar Nuevo Reporte NO debe existir en el historial según reportes_admin.html
    expect(screen.queryByRole('button', { name: /cargar nuevo reporte/i })).not.toBeInTheDocument();

    // Fila del reporte en tabla
    expect(screen.getByText('23/10/2026')).toBeInTheDocument();
    expect(screen.getByText('Carlos Mendoza')).toBeInTheDocument();
    expect(screen.getAllByText(/HEB-001/)[0]).toBeInTheDocument();
    expect(screen.getByText('24')).toBeInTheDocument(); // Asistencia badge
    expect(screen.getByText('$25.50')).toBeInTheDocument(); // USD
  });

  it('adapta la vista para Supervisor ocultando el selector de Red y los botones de edición/eliminación', () => {
    mockUser = {
      id: '2',
      username: 'supervisor',
      rol: 'supervisor',
      nombre: 'Pedro',
    };

    render(
      <MemoryRouter>
        <ReportesPage />
      </MemoryRouter>
    );

    // Hero title para supervisor
    expect(screen.getByText('Reportes de mi Red')).toBeInTheDocument();

    // Filtro de Red no debe existir para supervisor
    expect(screen.queryByLabelText(/red ministerial/i)).not.toBeInTheDocument();

    // Los botones de Editar y Eliminar tampoco se muestran al supervisor
    expect(screen.queryByTitle(/editar reporte/i)).not.toBeInTheDocument();
    expect(screen.queryByTitle(/eliminar reporte/i)).not.toBeInTheDocument();

    // Solo el botón de Ver Detalle está presente
    expect(screen.getByTitle(/ver detalle del reporte/i)).toBeInTheDocument();
  });

  it('abre el modal "Ver Detalle", permite alternar directamente al modo de edición y cerrar con animación', async () => {
    render(
      <MemoryRouter>
        <ReportesPage />
      </MemoryRouter>
    );

    // Click en botón ver detalle
    const btnVer = screen.getByTitle(/ver detalle del reporte/i);
    fireEvent.click(btnVer);

    // Modal abierto en modo vista
    const modal = screen.getByRole('dialog');
    expect(within(modal).getByText('Detalle del Reporte')).toBeInTheDocument();
    expect(within(modal).getByText('Fecha y Encargado')).toBeInTheDocument();
    expect(within(modal).getByText('Asistencia y Desglose')).toBeInTheDocument();
    expect(within(modal).getByText('Ministerio y Recursos')).toBeInTheDocument();

    // Desglose de valores dentro del modal
    expect(within(modal).getByText('La fe victoriosa')).toBeInTheDocument();
    expect(within(modal).getByText('12')).toBeInTheDocument(); // Regulares
    expect(within(modal).getByText('4')).toBeInTheDocument(); // Niños
    expect(within(modal).getByText('3')).toBeInTheDocument(); // Visitas
    expect(within(modal).getByText('5')).toBeInTheDocument(); // Comprometidos
    expect(within(modal).getByText('Total Calculado:')).toBeInTheDocument();

    // Transición directa al modo edición desde la vista de detalle
    const btnIrAEditar = within(modal).getByRole('button', { name: /editar reporte/i });
    expect(btnIrAEditar).toBeInTheDocument();
    fireEvent.click(btnIrAEditar);

    // Ahora está en modo edición
    expect(within(modal).getByText('Editar Reporte Semanal')).toBeInTheDocument();
    expect(within(modal).getByLabelText(/tema de la clase/i)).toBeInTheDocument();

    // Cancelar para regresar al modo vista
    const btnCancelarEdicion = within(modal).getByRole('button', { name: /cancelar/i });
    fireEvent.click(btnCancelarEdicion);
    expect(within(modal).getByText('Detalle del Reporte')).toBeInTheDocument();

    // Botón cerrar (botón exacto de texto "Cerrar" en el footer del modal)
    const btnCerrar = within(modal).getByRole('button', { name: /^cerrar$/i });
    fireEvent.click(btnCerrar);

    // Esperar a que la animación de salida termine de desmontar el modal
    await waitFor(() => {
      expect(screen.queryByText('Detalle del Reporte')).not.toBeInTheDocument();
    });
  });

  it('permite abrir directamente el modal en modo edición, valida horarios y envía la actualización', async () => {
    render(
      <MemoryRouter>
        <ReportesPage />
      </MemoryRouter>
    );

    // Click en botón editar desde la tabla
    const btnEditar = screen.getByTitle(/editar reporte/i);
    fireEvent.click(btnEditar);

    // Modal de edición abierto
    expect(screen.getByText('Editar Reporte Semanal')).toBeInTheDocument();

    const inputTema = screen.getByLabelText(/tema de la clase/i);
    fireEvent.change(inputTema, { target: { value: 'Tema Actualizado de la Fe' } });

    // Modificar asistencia y comprobar cálculo reactivo
    const inputRegulares = screen.getByLabelText(/regulares/i);
    fireEvent.change(inputRegulares, { target: { value: '15' } });
    expect(screen.getByText('27')).toBeInTheDocument(); // 15 + 4 + 3 + 5

    // Click en Guardar Cambios
    const btnGuardar = screen.getByRole('button', { name: /guardar cambios/i });
    fireEvent.click(btnGuardar);

    await waitFor(() => {
      expect(mockActualizarReporte).toHaveBeenCalledWith({
        id: 'rep-uuid-1',
        data: expect.objectContaining({
          cdp_id: 10,
          tema: 'Tema Actualizado de la Fe',
          nro_regulares: 15,
        }),
      });
    });

    expect(mockSuccess).toHaveBeenCalledWith('¡Reporte ministerial actualizado exitosamente!');
  });

  it('permite abrir el modal de confirmación y eliminar el reporte defensivamente', async () => {
    render(
      <MemoryRouter>
        <ReportesPage />
      </MemoryRouter>
    );

    // Click en botón eliminar
    const btnEliminar = screen.getByTitle(/eliminar reporte/i);
    fireEvent.click(btnEliminar);

    expect(screen.getByText('Confirmar Eliminación')).toBeInTheDocument();
    expect(
      screen.getByText(/¿estás seguro de que deseas eliminar este reporte\?/i)
    ).toBeInTheDocument();

    const btnConfirmar = screen.getByRole('button', { name: /sí, eliminar/i });
    fireEvent.click(btnConfirmar);

    await waitFor(() => {
      expect(mockEliminarReporte).toHaveBeenCalledWith({
        id: 'rep-uuid-1',
        cdp_id: 10,
      });
    });

    expect(mockSuccess).toHaveBeenCalledWith('Reporte ministerial eliminado correctamente');
  });

  it('inicializa los filtros y paginación desde los parámetros de la URL (Deep Linking)', () => {
    render(
      <MemoryRouter initialEntries={['/reportes?q=fe&red_id=1&cdp_id=10&page=2']}>
        <ReportesPage />
      </MemoryRouter>
    );

    expect(lastReportesArgs).toMatchObject({
      q: 'fe',
      red_id: '1',
      cdp_id: '10',
      page: 2,
    });
    expect(document.title).toBe('Vino Nuevo - Panel Administrativo - Reportes');
  });

  it('mantiene la URL limpia y valores por defecto cuando no hay parámetros de búsqueda', () => {
    render(
      <MemoryRouter initialEntries={['/reportes']}>
        <ReportesPage />
      </MemoryRouter>
    );

    expect(lastReportesArgs).toMatchObject({
      q: '',
      red_id: undefined,
      cdp_id: undefined,
      page: 1,
    });
  });
});
