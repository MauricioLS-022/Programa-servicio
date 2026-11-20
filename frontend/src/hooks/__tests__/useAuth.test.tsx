import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuth, AUTH_QUERY_KEY } from '../useAuth';
import { api } from '../../api/client';

vi.mock('../../api/client', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
  resetCsrfToken: vi.fn(),
}));

function createWrapper(queryClient: QueryClient) {
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('useAuth Hook', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  it('no consulta /auth/me cuando checkSession es false', () => {
    const { result } = renderHook(() => useAuth({ checkSession: false }), {
      wrapper: createWrapper(queryClient),
    });

    expect(api.get).not.toHaveBeenCalled();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeUndefined();
  });

  it('carga la sesión activa desde /auth/me por defecto', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({
      authenticated: true,
      user: { id: 'adm-1', username: 'admin', nombre: 'Admin', rol: 'admin' },
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(queryClient),
    });

    await waitFor(() => expect(result.current.isAuthenticated).toBe(true));
    expect(api.get).toHaveBeenCalledWith('/auth/me');
    expect(result.current.user?.username).toBe('admin');
  });

  it('actualiza la caché AUTH_QUERY_KEY, guarda timestamp y revalida dashboard/reportes en login', async () => {
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
    vi.mocked(api.post).mockResolvedValueOnce({
      success: true,
      user: { id: 'sup-1', username: 'supervisor', nombre: 'Pedro', rol: 'supervisor', supervisor_red_id: 1 },
    });

    const { result } = renderHook(() => useAuth({ checkSession: false }), {
      wrapper: createWrapper(queryClient),
    });

    await act(async () => {
      await result.current.login({ usuario: 'supervisor', contrasena: 'secret' });
    });

    expect(api.post).toHaveBeenCalledWith('/auth/login', { usuario: 'supervisor', contrasena: 'secret' });
    const cached = queryClient.getQueryData<{ authenticated: boolean; user?: { username: string } }>(AUTH_QUERY_KEY);
    expect(cached?.authenticated).toBe(true);
    expect(cached?.user?.username).toBe('supervisor');
    expect(localStorage.getItem('ultimo_acceso_login')).toBeTruthy();
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['reportes'] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['dashboard'] });
  });

  it('revoca la autenticación y purga completamente el QueryClient en logout', async () => {
    queryClient.setQueryData(AUTH_QUERY_KEY, {
      authenticated: true,
      user: { id: 'adm-1', username: 'admin', nombre: 'Admin', rol: 'admin' },
    });
    queryClient.setQueryData(['dashboard', 'datos'], { asistencia_total: 99 });

    const clearSpy = vi.spyOn(queryClient, 'clear');
    vi.mocked(api.post).mockResolvedValueOnce({ success: true });

    const { result } = renderHook(() => useAuth({ checkSession: false }), {
      wrapper: createWrapper(queryClient),
    });

    expect(result.current.isAuthenticated).toBe(true);

    await act(async () => {
      await result.current.logout();
    });

    expect(api.post).toHaveBeenCalledWith('/auth/logout');
    expect(clearSpy).toHaveBeenCalledTimes(1);
    expect(queryClient.getQueryData(['dashboard', 'datos'])).toBeUndefined();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
