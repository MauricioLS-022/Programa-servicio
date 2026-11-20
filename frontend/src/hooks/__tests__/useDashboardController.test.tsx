import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { useDashboardController } from '../useDashboardController';

const mockUseAuth = vi.fn();
const mockUseRedes = vi.fn();
const mockUseCasasDePaz = vi.fn();
const mockUseDashboard = vi.fn();

vi.mock('../useAuth', () => ({
  useAuth: () => mockUseAuth(),
}));

vi.mock('../useDashboard', () => ({
  useRedes: () => mockUseRedes(),
  useCasasDePaz: () => mockUseCasasDePaz(),
  useDashboard: (params: unknown) => mockUseDashboard(params),
}));

const createWrapper = (initialEntries = ['/dashboard']) => {
  return ({ children }: { children: React.ReactNode }) => (
    <MemoryRouter initialEntries={initialEntries}>{children}</MemoryRouter>
  );
};

describe('useDashboardController', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseRedes.mockReturnValue({
      redes: [
        { id: 1, nombre: 'Red Hebrón' },
        { id: 2, nombre: 'Red Sur' },
      ],
    });
    mockUseCasasDePaz.mockReturnValue({
      casas: [
        { id: 10, codigo: 'HEB-01', anfitrion: 'Carlos', red_id: 1, red_nombre: 'Red Hebrón' },
        { id: 20, codigo: 'SUR-01', anfitrion: 'Marta', red_id: 2, red_nombre: 'Red Sur' },
      ],
    });
    mockUseDashboard.mockReturnValue({
      metricas: { total_casas: 2, casas_activas: 2, historial: [{ id: 'r1' }] },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
  });

  it('inicializa en nivel general para admin y permite cambiar a red y cdp atómicamente', () => {
    mockUseAuth.mockReturnValue({ user: { id: 'a1', rol: 'admin', nombre: 'Admin' } });

    const { result } = renderHook(() => useDashboardController(), {
      wrapper: createWrapper(['/dashboard']),
    });

    expect(result.current.nivel).toBe('general');
    expect(result.current.hasData).toBe(true);

    act(() => {
      result.current.handleNivelChange('cdp');
    });

    expect(result.current.nivel).toBe('cdp');
    expect(result.current.redId).toBe('1');
    expect(result.current.cdpId).toBe('10');

    act(() => {
      result.current.handleRedChange('2');
    });

    expect(result.current.redId).toBe('2');
    expect(result.current.cdpId).toBe('20');
  });

  it('restringe a supervisor a su red asignada y bloquea nivel general', () => {
    mockUseAuth.mockReturnValue({ user: { id: 's1', rol: 'supervisor', nombre: 'Sup' } });
    mockUseRedes.mockReturnValue({ redes: [{ id: 2, nombre: 'Red Sur' }] });

    const { result } = renderHook(() => useDashboardController(), {
      wrapper: createWrapper(['/dashboard?nivel=general']),
    });

    expect(result.current.isSupervisor).toBe(true);
    expect(result.current.nivel).toBe('red');
    expect(result.current.redId).toBe('2');

    act(() => {
      result.current.handleNivelChange('general');
    });
    expect(result.current.nivel).toBe('red');
  });

  it('filtra casas por término de búsqueda rápida', () => {
    mockUseAuth.mockReturnValue({ user: { id: 'a1', rol: 'admin', nombre: 'Admin' } });

    const { result } = renderHook(() => useDashboardController(), {
      wrapper: createWrapper(['/dashboard']),
    });

    act(() => {
      result.current.handleSearchChange('Marta');
    });

    expect(result.current.filteredCasas).toHaveLength(1);
    expect(result.current.filteredCasas[0].codigo).toBe('SUR-01');
  });
});
