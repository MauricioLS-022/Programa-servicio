import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import React from 'react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { useUrlFilters } from '../useUrlFilters';

interface TestFilters {
  nivel: 'general' | 'red' | 'cdp';
  red_id: string;
  periodo: 'semana' | 'mes' | 'historico';
  q: string;
  page: number;
}

const defaultFilters: TestFilters = {
  nivel: 'general',
  red_id: '',
  periodo: 'semana',
  q: '',
  page: 1,
};

describe('useUrlFilters Hook', () => {
  it('debe inicializarse con los valores por defecto cuando la URL está limpia', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <MemoryRouter initialEntries={['/dashboard']}>{children}</MemoryRouter>
    );

    const { result } = renderHook(() => useUrlFilters(defaultFilters), { wrapper });

    expect(result.current.filters).toEqual(defaultFilters);
    expect(result.current.isDefault).toBe(true);
    expect(result.current.searchParams.toString()).toBe('');
  });

  it('debe inicializarse a partir de los query params en la URL (Deep Linking)', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <MemoryRouter initialEntries={['/dashboard?nivel=red&red_id=3&periodo=mes&page=2&q=hebron']}>
        {children}
      </MemoryRouter>
    );

    const { result } = renderHook(() => useUrlFilters(defaultFilters), { wrapper });

    expect(result.current.filters).toEqual({
      nivel: 'red',
      red_id: '3',
      periodo: 'mes',
      page: 2,
      q: 'hebron',
    });
    expect(result.current.isDefault).toBe(false);
  });

  it('debe actualizar la URL al modificar un filtro no por defecto', () => {
    let currentLocation: any;
    const LocationWatcher = () => {
      currentLocation = useLocation();
      return null;
    };

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <MemoryRouter initialEntries={['/dashboard']}>
        <LocationWatcher />
        {children}
      </MemoryRouter>
    );

    const { result } = renderHook(() => useUrlFilters(defaultFilters), { wrapper });

    act(() => {
      result.current.setFilter('nivel', 'red');
    });

    expect(result.current.filters.nivel).toBe('red');
    expect(result.current.isDefault).toBe(false);
    expect(currentLocation.search).toBe('?nivel=red');
  });

  it('debe ELIMINAR el parámetro de la URL si se restablece al valor por defecto (URL Limpia)', () => {
    let currentLocation: any;
    const LocationWatcher = () => {
      currentLocation = useLocation();
      return null;
    };

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <MemoryRouter initialEntries={['/dashboard?nivel=red']}>
        <LocationWatcher />
        {children}
      </MemoryRouter>
    );

    const { result } = renderHook(() => useUrlFilters(defaultFilters), { wrapper });

    expect(result.current.filters.nivel).toBe('red');

    // Cambiar de vuelta al valor por defecto ('general')
    act(() => {
      result.current.setFilter('nivel', 'general');
    });

    expect(result.current.filters.nivel).toBe('general');
    expect(result.current.isDefault).toBe(true);
    // La URL debe quedar totalmente limpia sin query params
    expect(currentLocation.search).toBe('');
  });

  it('debe ELIMINAR parámetros vacíos o nulos en lugar de dejar cadenas vacías (?q=)', () => {
    let currentLocation: any;
    const LocationWatcher = () => {
      currentLocation = useLocation();
      return null;
    };

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <MemoryRouter initialEntries={['/dashboard?q=busqueda']}>
        <LocationWatcher />
        {children}
      </MemoryRouter>
    );

    const { result } = renderHook(() => useUrlFilters(defaultFilters), { wrapper });

    act(() => {
      result.current.setFilter('q', '');
    });

    expect(result.current.filters.q).toBe('');
    expect(currentLocation.search).toBe('');
  });

  it('debe soportar actualización atómica de múltiples filtros con setFilters', () => {
    let currentLocation: any;
    const LocationWatcher = () => {
      currentLocation = useLocation();
      return null;
    };

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <MemoryRouter initialEntries={['/dashboard']}>
        <LocationWatcher />
        {children}
      </MemoryRouter>
    );

    const { result } = renderHook(() => useUrlFilters(defaultFilters), { wrapper });

    act(() => {
      result.current.setFilters({
        nivel: 'cdp',
        red_id: '12',
        periodo: 'historico',
      });
    });

    expect(result.current.filters.nivel).toBe('cdp');
    expect(result.current.filters.red_id).toBe('12');
    expect(result.current.filters.periodo).toBe('historico');
    expect(currentLocation.search).toContain('nivel=cdp');
    expect(currentLocation.search).toContain('red_id=12');
    expect(currentLocation.search).toContain('periodo=historico');
  });

  it('debe limpiar todos los parámetros con resetFilters', () => {
    let currentLocation: any;
    const LocationWatcher = () => {
      currentLocation = useLocation();
      return null;
    };

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <MemoryRouter
        initialEntries={['/dashboard?nivel=red&red_id=5&cdp_id=99']}
      >
        <LocationWatcher />
        {children}
      </MemoryRouter>
    );

    const { result } = renderHook(
      () =>
        useUrlFilters(defaultFilters, {
          cleanupKeys: ['cdp_id'],
        }),
      { wrapper }
    );

    act(() => {
      result.current.resetFilters();
    });

    expect(result.current.filters).toEqual(defaultFilters);
    expect(result.current.isDefault).toBe(true);
    expect(currentLocation.search).toBe('');
  });
});
