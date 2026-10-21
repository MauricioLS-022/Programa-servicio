/**
 * Hook de Métricas de Dashboard y Estructura Ministerial.
 * Conectado con /api/dashboard/datos, /api/redes, /api/casas_de_paz y /api/lideres.
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type {
  DashboardMetricas,
  RedesResponse,
  CasasResponse,
  LideresResponse,
  Red,
  CasaDePaz,
  Lider,
} from '../types/estructura';

export interface DashboardParams {
  nivel?: 'general' | 'red' | 'cdp';
  red_id?: number | string;
  cdp_id?: number | string;
  periodo?: 'semana' | 'mes' | 'anio';
  mes?: number;
  anio?: number;
}

export function useDashboard(params: DashboardParams = {}) {
  const query = useQuery<DashboardMetricas>({
    queryKey: ['dashboard', params],
    queryFn: () =>
      api.get<DashboardMetricas>('/dashboard/datos', {
        params: {
          nivel: params.nivel || 'general',
          red_id: params.red_id,
          cdp_id: params.cdp_id,
          periodo: params.periodo || 'semana',
          mes: params.mes,
          anio: params.anio,
        },
      }),
  });

  return {
    metricas: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}

export function useRedes() {
  const query = useQuery<RedesResponse>({
    queryKey: ['redes'],
    queryFn: () => api.get<RedesResponse>('/redes'),
    staleTime: 1000 * 60 * 10,
  });

  return {
    redes: query.data?.redes || ([] as Red[]),
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}

export function useCasasDePaz(params: { red_id?: number | string; q?: string; filtro?: string } = {}) {
  const query = useQuery<CasasResponse>({
    queryKey: ['casas', params],
    queryFn: () =>
      api.get<CasasResponse>('/casas_de_paz', {
        params: {
          red_id: params.red_id,
          q: params.q,
          filtro: params.filtro,
        },
      }),
  });

  return {
    casas: query.data?.casas || ([] as CasaDePaz[]),
    total: query.data?.total || 0,
    sinReporte7dIds: query.data?.sin_reporte_7d_ids || [],
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}

export function useLideres(params: { red_id?: number | string; cdp_id?: number | string; rol?: string; q?: string; page?: number; per_page?: number } = {}) {
  const query = useQuery<LideresResponse>({
    queryKey: ['lideres', params],
    queryFn: () =>
      api.get<LideresResponse>('/lideres', {
        params: {
          red_id: params.red_id,
          cdp_id: params.cdp_id,
          rol: params.rol,
          q: params.q,
          page: params.page || 1,
          per_page: params.per_page || 10,
        },
      }),
  });

  return {
    lideres: query.data?.lideres || ([] as Lider[]),
    total: query.data?.total || 0,
    page: query.data?.page || 1,
    pages: query.data?.pages || 1,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}

