import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { useGenerarReporteForm } from '../useGenerarReporteForm';
import { buildCdpFichaHtml } from '../../utils/exportCdpPdf';
import type { CdpDetalle } from '../../types/estructura';

const mockCrearReporte = vi.fn();
const mockSuccess = vi.fn();
const mockError = vi.fn();
const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../useAuth', () => ({
  useAuth: () => ({ user: { id: 'l1', rol: 'lider_cdp', nombre: 'Líder' } }),
}));

vi.mock('../usePerfil', () => ({
  usePerfil: () => ({
    perfil: { cdp_id: 5, cdp_codigo: 'HEB-05', cdp_nombre: 'Casa Hebrón 5' },
    isLoading: false,
  }),
}));

vi.mock('../useReportes', () => ({
  useReportes: () => ({ crearReporte: mockCrearReporte, isCreando: false }),
}));

vi.mock('../useDashboard', () => ({
  useCasasDePaz: () => ({ casas: [] }),
  useLideres: () => ({ lideres: [] }),
}));

vi.mock('../../context/ToastContext', () => ({
  useToast: () => ({ success: mockSuccess, error: mockError }),
}));

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MemoryRouter initialEntries={['/generar-reporte']}>{children}</MemoryRouter>
);

describe('useGenerarReporteForm y exportCdpPdf', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calcula totalAsistencia reactivamente y valida horario antes de enviar', async () => {
    const { result } = renderHook(() => useGenerarReporteForm(), { wrapper });

    act(() => {
      result.current.setNroRegulares(10);
      result.current.setNroNinos(4);
      result.current.setNroVisitas(3);
      result.current.setNroComprometidos(2);
      result.current.setHrInicio('19:00');
      result.current.setHrFin('18:00');
      result.current.setTema('Fe y Esperanza');
    });

    expect(result.current.totalAsistencia).toBe(19);

    await act(async () => {
      await result.current.handleSubmit({ preventDefault: vi.fn() } as unknown as React.FormEvent);
    });

    expect(mockError).toHaveBeenCalledWith(
      'La hora de finalización debe ser posterior a la hora de inicio.'
    );
    expect(mockCrearReporte).not.toHaveBeenCalled();
  });

  it('envía payload válido y navega al dashboard tras éxito', async () => {
    mockCrearReporte.mockResolvedValue({ success: true });
    const { result } = renderHook(() => useGenerarReporteForm(), { wrapper });

    act(() => {
      result.current.setNroRegulares(8);
      result.current.setHrInicio('19:00');
      result.current.setHrFin('20:30');
      result.current.setTema('El Amor de Dios');
      result.current.setOfrendasUsd('15.5');
      result.current.setOfrendasBs('600');
    });

    await act(async () => {
      await result.current.handleSubmit({ preventDefault: vi.fn() } as unknown as React.FormEvent);
    });

    expect(mockCrearReporte).toHaveBeenCalledWith(
      expect.objectContaining({
        cdp_id: 5,
        tema: 'El Amor de Dios',
        nro_regulares: 8,
        ofrendas_usd: 15.5,
        ofrendas_bs: 600,
      })
    );
    expect(mockSuccess).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('buildCdpFichaHtml genera ficha imprimible con código, KPIs y tabla de líderes', () => {
    const mockCdp = {
      id: 5,
      codigo: 'HEB-05',
      red_nombre: 'Red Hebrón',
      supervisor_nombre: 'Pedro Gómez',
      asistencia_promedio: 18,
      total_reportes: 12,
      ofrendas_usd_totales: 120.5,
      ofrendas_bs_totales: 4500,
      visitas_totales: 9,
      conversiones_totales: 4,
      direccion: 'Calle Principal',
      anfitrion: 'Ana Ruiz',
      telefono: '+584121234567',
      horario: 'Miércoles · 7:00 PM',
      lideres: [{ nombre_completo: 'Juan Pérez', rol: 'Líder', telefono: '04120001122' }],
      reportes: [],
    } as unknown as CdpDetalle;

    const html = buildCdpFichaHtml(mockCdp, '18 de noviembre de 2026');
    expect(html).toContain('Casa "HEB-05"');
    expect(html).toContain('Red Hebrón');
    expect(html).toContain('$120.50');
    expect(html).toContain('Juan Pérez');
    expect(html).toContain('18 de noviembre de 2026');
  });
});
