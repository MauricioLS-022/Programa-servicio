/**
 * Hook de datos para el Dashboard de Líder de Casa de Paz.
 * Conectado con GET /api/lider/dashboard?page=N.
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { LiderDashboardData } from '../types/liderDashboard';

export interface UseLiderDashboardParams {
  page?: number;
  per_page?: number;
}

export function useLiderDashboard(params: UseLiderDashboardParams = {}) {
  const page = params.page || 1;
  const per_page = params.per_page || 5;

  const query = useQuery<LiderDashboardData>({
    queryKey: ['lider-dashboard', { page, per_page }],
    queryFn: () =>
      api.get<LiderDashboardData>('/lider/dashboard', {
        params: {
          page,
          per_page,
        },
      }),
    staleTime: 1000 * 60 * 2, // 2 minutos
  });

  return {
    data: query.data,
    cdp: query.data?.cdp || null,
    lideres: query.data?.lideres || [],
    metricas: query.data?.metricas || null,
    reportes: query.data?.reportes || [],
    total_reportes: query.data?.total_reportes || 0,
    currentPage: query.data?.page || page,
    totalPages: query.data?.pages || 1,
    tieneCdp: query.data?.tiene_cdp ?? true,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
