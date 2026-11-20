import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { useEstructuraController, cleanRedName } from '../useEstructuraController';
import type { Red, CasaDePaz } from '../../types/estructura';

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

let mockUser: { id: string; username: string; rol: 'admin' | 'supervisor' | 'lider_cdp'; nombre: string } = {
  id: '1',
  username: 'admin',
  rol: 'admin',
  nombre: 'Admin',
};
vi.mock('../useAuth', () => ({
  useAuth: () => ({ user: mockUser, isAuthenticated: true }),
}));

const mockRefetchRedes = vi.fn();
const mockRefetchCasas = vi.fn();

const mockRedes: Red[] = [
  { id: 1, nombre: 'Red Hebrón', is_active: 1, supervisor_id: 'sup-1', supervisor_nombre: 'Pedro' },
  { id: 2, nombre: 'Sur', is_active: 1, supervisor_id: 'sup-2', supervisor_nombre: 'María' },
];

const mockCasas: CasaDePaz[] = [
  {
    id: 10,
    codigo: 'HEB-001',
    anfitrion: 'Familia Mendoza',
    direccion: 'Av Norte',
    red_id: 1,
    red_nombre: 'Red Hebrón',
    is_active: 1,
    sin_reporte_7d: false,
    lider: 'Carlos',
  },
  {
    id: 11,
    codigo: 'HEB-002',
    anfitrion: 'Familia Rojas',
    direccion: 'Calle 3',
    red_id: 1,
    red_nombre: 'Red Hebrón',
    is_active: 1,
    sin_reporte_7d: true,
    lider: 'Ana',
  },
  {
    id: 20,
    codigo: 'SUR-001',
    anfitrion: 'Familia Díaz',
    direccion: 'Av Sur',
    red_id: 2,
    red_nombre: 'Red Sur',
    is_active: 1,
    sin_reporte_7d: true,
    lider: 'Luis',
  },
  {
    id: 21,
    codigo: 'SUR-002',
    anfitrion: 'Familia Pausada',
    direccion: 'Calle 9',
    red_id: 2,
    red_nombre: 'Red Sur',
    is_active: 0,
    sin_reporte_7d: true,
    lider: 'Inactivo',
  },
];

vi.mock('../useDashboard', () => ({
  useRedes: () => ({ redes: mockRedes, isLoading: false, refetch: mockRefetchRedes }),
  useCasasDePaz: () => ({ casas: mockCasas, isLoading: false, refetch: mockRefetchCasas }),
}));

const mockCrearRed = vi.fn();
const mockEditarRed = vi.fn();
const mockToggleRed = vi.fn();
const mockEliminarRed = vi.fn();
const mockCrearCdp = vi.fn();
const mockEditarCdp = vi.fn();
const mockEliminarCdp = vi.fn();

vi.mock('../useEstructura', () => ({
  useEstructuraSelectores: () => ({ selectores: { supervisores: [], lideres_cdp: [], casas_de_paz: [], redes: mockRedes } }),
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
    eliminarCdp: mockEliminarCdp,
    isEliminandoCdp: false,
  }),
}));

function makeWrapper(initialEntries: string[] = ['/estructura']) {
  return ({ children }: { children: React.ReactNode }) => (
    <MemoryRouter initialEntries={initialEntries}>{children}</MemoryRouter>
  );
}

describe('useEstructuraController Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
    mockUser = { id: '1', username: 'admin', rol: 'admin', nombre: 'Admin' };
  });

  it('cleanRedName elimina el prefijo duplicado "Red "', () => {
    expect(cleanRedName('Red Hebrón')).toBe('Hebrón');
    expect(cleanRedName('red   Betel')).toBe('Betel');
    expect(cleanRedName('Sur')).toBe('Sur');
    expect(cleanRedName(undefined)).toBe('');
  });

  it('calcula pendingInScope, totalPendientesCongregacion y aplica filtros combinados de red, estado y búsqueda', () => {
    const { result } = renderHook(() => useEstructuraController(), {
      wrapper: makeWrapper(['/estructura']),
    });

    // Solo cuentan casas activas con sin_reporte_7d=true (HEB-002 y SUR-001; SUR-002 está inactiva)
    expect(result.current.totalCasasCongregacion).toBe(4);
    expect(result.current.totalPendientesCongregacion).toBe(2);
    expect(result.current.pendingInScope).toBe(2);
    expect(result.current.filteredCasas).toHaveLength(4);

    // Seleccionar Red 1
    act(() => {
      result.current.handleSelectRed(1);
    });
    expect(result.current.effectiveRedId).toBe('1');
    expect(result.current.selectedRedName).toBe('Red Hebrón');
    expect(result.current.pendingInScope).toBe(1);
    expect(result.current.filteredCasas.map((c) => c.codigo)).toEqual(['HEB-001', 'HEB-002']);

    // Filtrar por pendientes_7d dentro de Red 1
    act(() => {
      result.current.handleFiltroEstadoChange('pendientes_7d');
    });
    expect(result.current.filteredCasas.map((c) => c.codigo)).toEqual(['HEB-002']);

    // Búsqueda que no coincide con HEB-002
    act(() => {
      result.current.handleSearchChange('Mendoza');
    });
    expect(result.current.filteredCasas).toHaveLength(0);
  });

  it('aplica aislamiento territorial automático a la primera red para supervisores', () => {
    mockUser = { id: 'sup-1', username: 'sup1', rol: 'supervisor', nombre: 'Pedro' };

    const { result } = renderHook(() => useEstructuraController(), {
      wrapper: makeWrapper(['/estructura']),
    });

    expect(result.current.isSupervisor).toBe(true);
    expect(result.current.isAdmin).toBe(false);
    expect(result.current.effectiveRedId).toBe('1');
    expect(result.current.selectedRedName).toBe('Red Hebrón');
    expect(result.current.filteredCasas.every((c) => c.red_id === 1)).toBe(true);
    expect(result.current.pendingInScope).toBe(1);
  });

  it('inicializa highlightedCdpId con deep linking de cdp_id en URL', () => {
    const { result } = renderHook(() => useEstructuraController(), {
      wrapper: makeWrapper(['/estructura?red_id=1&cdp_id=10']),
    });

    expect(result.current.highlightedCdpId).toBe('10');
    expect(result.current.effectiveRedId).toBe('1');
  });

  it('ejecuta handlers CRUD de Red y CDP mostrando toasts de éxito y error', async () => {
    mockCrearRed.mockResolvedValueOnce({ success: true, message: 'Red creada' });
    mockToggleRed.mockResolvedValueOnce({ success: false, message: 'No se pudo pausar' });
    mockEliminarRed.mockResolvedValueOnce({ success: true, message: 'Red borrada' });
    mockCrearCdp.mockRejectedValueOnce(new Error('Fallo de red 503'));
    mockEliminarCdp.mockResolvedValueOnce({ success: true, message: 'CDP borrada' });

    const { result } = renderHook(() => useEstructuraController(), {
      wrapper: makeWrapper(['/estructura?red_id=1']),
    });

    await act(async () => {
      await result.current.handleGuardarRed({ nombre: 'Nueva Red' });
    });
    expect(mockSuccess).toHaveBeenCalledWith('Red creada');
    expect(mockRefetchRedes).toHaveBeenCalled();

    await act(async () => {
      await result.current.handleToggleRed(1);
    });
    expect(mockError).toHaveBeenCalledWith('No se pudo pausar');

    await act(async () => {
      await result.current.handleEliminarRed(1);
    });
    expect(mockSuccess).toHaveBeenCalledWith('Red borrada');
    expect(result.current.selectedRedId).toBe('');

    await act(async () => {
      await result.current.handleGuardarCdp({
        codigo: 'NEW-1',
        anfitrion: 'A',
        telefono: '',
        direccion: 'B',
        red_id: 1,
      });
    });
    expect(mockError).toHaveBeenCalledWith('Fallo de red 503');

    await act(async () => {
      await result.current.handleEliminarCdp(10);
    });
    expect(mockSuccess).toHaveBeenCalledWith('CDP borrada');
    expect(mockRefetchCasas).toHaveBeenCalled();
  });
});
