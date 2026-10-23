/**
 * Hook de Reportes con TanStack Query.
 * Maneja listados paginados, filtros e invalidación automática tras mutaciones.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type {
  ReporteFiltros,
  ReportesResponse,
  ReporteFormPayload,
  ProcesarReporteResponse,
} from '../types/reporte';

export const REPORTES_QUERY_KEY = ['reportes'];

export function useReportes(filtros: ReporteFiltros = {}) {
  const queryClient = useQueryClient();

  const reportesQuery = useQuery<ReportesResponse>({
    queryKey: [...REPORTES_QUERY_KEY, filtros],
    queryFn: () =>
      api.get<ReportesResponse>('/reportes', {
        params: {
          q: filtros.q,
          red_id: filtros.red_id,
          cdp_id: filtros.cdp_id,
          fecha_desde: filtros.fecha_desde,
          fecha_hasta: filtros.fecha_hasta,
          page: filtros.page || 1,
          per_page: filtros.per_page || 10,
        },
      }),
  });

  const crearReporteMutation = useMutation<ProcesarReporteResponse, Error, ReporteFormPayload>({
    mutationFn: (payload) => api.post<ProcesarReporteResponse>('/reportes', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORTES_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['casas'] });
    },
  });

  const actualizarReporteMutation = useMutation<
    ProcesarReporteResponse,
    Error,
    { id: string | number; data: Partial<ReporteFormPayload> }
  >({
    mutationFn: ({ id, data }) => api.put<ProcesarReporteResponse>(`/reportes/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORTES_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const eliminarReporteMutation = useMutation<
    ProcesarReporteResponse,
    Error,
    { id: string | number; cdp_id?: number }
  >({
    mutationFn: ({ id, cdp_id }) =>
      api.delete<ProcesarReporteResponse>(`/reportes/${id}`, {
        params: cdp_id ? { cdp_id } : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORTES_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  return {
    reportes: reportesQuery.data?.reportes || [],
    total: reportesQuery.data?.total || 0,
    page: reportesQuery.data?.page || 1,
    pages: reportesQuery.data?.pages || 1,
    perPage: reportesQuery.data?.per_page || 10,
    isLoading: reportesQuery.isLoading,
    isError: reportesQuery.isError,
    error: reportesQuery.error,
    refetch: reportesQuery.refetch,

    crearReporte: crearReporteMutation.mutateAsync,
    isCreando: crearReporteMutation.isPending,

    actualizarReporte: actualizarReporteMutation.mutateAsync,
    isActualizando: actualizarReporteMutation.isPending,

    eliminarReporte: eliminarReporteMutation.mutateAsync,
    isEliminando: eliminarReporteMutation.isPending,
  };
}

