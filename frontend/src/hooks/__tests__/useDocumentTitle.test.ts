import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useDocumentTitle, getRoleTitlePrefix } from '../useDocumentTitle';
import * as useAuthModule from '../useAuth';

vi.mock('../useAuth', () => ({
  useAuth: vi.fn(),
}));

describe('useDocumentTitle and getRoleTitlePrefix', () => {
  const originalTitle = 'Vino Nuevo';

  beforeEach(() => {
    document.title = originalTitle;
    vi.clearAllMocks();
  });

  afterEach(() => {
    document.title = originalTitle;
  });

  describe('getRoleTitlePrefix', () => {
    it('debe devolver "Panel Administrativo" para rol admin', () => {
      expect(getRoleTitlePrefix('admin')).toBe('Panel Administrativo');
    });

    it('debe devolver "Supervisión Regional" para rol supervisor', () => {
      expect(getRoleTitlePrefix('supervisor')).toBe('Supervisión Regional');
    });

    it('debe devolver "Casa de Paz" para rol lider_cdp o indefinido', () => {
      expect(getRoleTitlePrefix('lider_cdp')).toBe('Casa de Paz');
      expect(getRoleTitlePrefix(undefined)).toBe('Casa de Paz');
    });
  });

  describe('useDocumentTitle Hook', () => {
    it('debe establecer el título ministerial para administrador', () => {
      vi.mocked(useAuthModule.useAuth).mockReturnValue({
        user: { id: '1', username: 'admin', rol: 'admin', nombre: 'Admin', apellido: 'User' },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        isLoggingIn: false,
        loginError: null,
        logout: vi.fn(),
        isLoggingOut: false,
        refetchUser: vi.fn(),
      });

      renderHook(() => useDocumentTitle('Dashboard'));

      expect(document.title).toBe('Vino Nuevo - Panel Administrativo - Dashboard');
    });

    it('debe establecer el título ministerial para supervisor', () => {
      vi.mocked(useAuthModule.useAuth).mockReturnValue({
        user: { id: '2', username: 'sup', rol: 'supervisor', nombre: 'Super', apellido: 'Visor' },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        isLoggingIn: false,
        loginError: null,
        logout: vi.fn(),
        isLoggingOut: false,
        refetchUser: vi.fn(),
      });

      renderHook(() => useDocumentTitle('Reportes'));

      expect(document.title).toBe('Vino Nuevo - Supervisión Regional - Reportes');
    });

    it('debe establecer el título ministerial para líder de Casa de Paz', () => {
      vi.mocked(useAuthModule.useAuth).mockReturnValue({
        user: { id: '3', username: 'lider', rol: 'lider_cdp', nombre: 'Lider', apellido: 'CDP' },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        isLoggingIn: false,
        loginError: null,
        logout: vi.fn(),
        isLoggingOut: false,
        refetchUser: vi.fn(),
      });

      renderHook(() => useDocumentTitle('Generar Reporte'));

      expect(document.title).toBe('Vino Nuevo - Casa de Paz - Generar Reporte');
    });

    it('debe soportar modo override para pantallas independientes como Login', () => {
      vi.mocked(useAuthModule.useAuth).mockReturnValue({
        user: undefined,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        isLoggingIn: false,
        loginError: null,
        logout: vi.fn(),
        isLoggingOut: false,
        refetchUser: vi.fn(),
      });

      renderHook(() => useDocumentTitle('Iniciar Sesión — Vino Nuevo', { override: true }));

      expect(document.title).toBe('Iniciar Sesión — Vino Nuevo');
    });

    it('debe restaurar el título previo al desmontar', () => {
      vi.mocked(useAuthModule.useAuth).mockReturnValue({
        user: { id: '1', username: 'admin', rol: 'admin', nombre: 'Admin', apellido: 'User' },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        isLoggingIn: false,
        loginError: null,
        logout: vi.fn(),
        isLoggingOut: false,
        refetchUser: vi.fn(),
      });

      const { unmount } = renderHook(() => useDocumentTitle('Estructura'));
      expect(document.title).toBe('Vino Nuevo - Panel Administrativo - Estructura');

      unmount();
      expect(document.title).toBe(originalTitle);
    });
  });
});
