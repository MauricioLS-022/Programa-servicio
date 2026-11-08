import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { LideresResponse, LiderInput } from '../types/estructura';

export interface UseLideresParams {
  q?: string;
  rol?: string;
  red_id?: string | number;
  cdp_id?: string | number;
  page?: number;
  per_page?: number;
}

export function useLideres(params: UseLideresParams = {}) {
  const query = useQuery<LideresResponse>({
    queryKey: ['lideres', params],
    queryFn: () =>
      api.get<LideresResponse>('/lideres', {
        params: {
          q: params.q || undefined,
          rol: params.rol || undefined,
          red_id: params.red_id ? String(params.red_id) : undefined,
          cdp_id: params.cdp_id ? String(params.cdp_id) : undefined,
          page: params.page || 1,
          per_page: params.per_page || 100, // Fetch amplio para soportar Live Search client-side
        },
      }),
    staleTime: 1000 * 60 * 2,
  });

  return {
    lideres: query.data?.lideres || [],
    total: query.data?.total || 0,
    page: query.data?.page || 1,
    pages: query.data?.pages || 1,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}

export function useLiderMutations() {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['lideres'] });
    queryClient.invalidateQueries({ queryKey: ['cdp-detalle'] });
    queryClient.invalidateQueries({ queryKey: ['selectores-estructura'] });
    queryClient.invalidateQueries({ queryKey: ['casas'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };

  const crearMutation = useMutation({
    mutationFn: (data: LiderInput) =>
      api.post<{ success: boolean; message: string }>('/lideres', data),
    onSuccess: invalidate,
  });

  const editarMutation = useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: Partial<LiderInput> }) =>
      api.put<{ success: boolean; message: string }>(`/lideres/${id}`, data),
    onSuccess: invalidate,
  });

  const toggleMutation = useMutation({
    mutationFn: (id: number | string) =>
      api.post<{ success: boolean; status?: string; message: string }>(`/lideres/${id}/toggle`),
    onSuccess: invalidate,
  });

  const eliminarMutation = useMutation({
    mutationFn: (id: number | string) =>
      api.delete<{ success: boolean; message: string }>(`/lideres/${id}`),
    onSuccess: invalidate,
  });

  return {
    crearLider: crearMutation.mutateAsync,
    isCreando: crearMutation.isPending,
    editarLider: editarMutation.mutateAsync,
    isEditando: editarMutation.isPending,
    toggleLider: toggleMutation.mutateAsync,
    isToggling: toggleMutation.isPending,
    eliminarLider: eliminarMutation.mutateAsync,
    isEliminando: eliminarMutation.isPending,
  };
}

