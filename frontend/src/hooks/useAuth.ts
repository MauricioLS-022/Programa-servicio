/**
 * Hook de Autenticación con TanStack Query.
 * Libre de acoplamiento al DOM para futura exportación a React Native.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { AuthMeResponse, AuthResponse, LoginCredentials, User } from '../types/auth';

export const AUTH_QUERY_KEY = ['auth', 'me'];

export function useAuth() {
  const queryClient = useQueryClient();

  const meQuery = useQuery<AuthMeResponse>({
    queryKey: AUTH_QUERY_KEY,
    queryFn: () => api.get<AuthMeResponse>('/auth/me'),
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutos de validez en caché de memoria
  });

  const loginMutation = useMutation<AuthResponse, Error, LoginCredentials>({
    mutationFn: (credentials) => api.post<AuthResponse>('/auth/login', credentials),
    onSuccess: (data) => {
      if (data.success && data.user) {
        queryClient.setQueryData(AUTH_QUERY_KEY, {
          authenticated: true,
          user: data.user,
        });
        queryClient.invalidateQueries({ queryKey: ['reportes'] });
        queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      }
    },
  });

  const logoutMutation = useMutation<AuthResponse, Error, void>({
    mutationFn: () => api.post<AuthResponse>('/auth/logout'),
    onSuccess: () => {
      queryClient.setQueryData(AUTH_QUERY_KEY, {
        authenticated: false,
        user: undefined,
      });
      queryClient.clear();
    },
  });

  const user: User | undefined = meQuery.data?.authenticated ? meQuery.data.user : undefined;
  const isAuthenticated = Boolean(meQuery.data?.authenticated);
  const isLoading = meQuery.isLoading;

  return {
    user,
    isAuthenticated,
    isLoading,
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    logout: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,
    refetchUser: meQuery.refetch,
  };
}

