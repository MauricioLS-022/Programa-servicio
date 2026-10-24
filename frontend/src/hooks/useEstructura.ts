import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type {
  CdpDetalleResponse,
  EstructuraSelectoresResponse,
  RedInput,
  CdpInput,
  LiderInput,
} from '../types/estructura';

export function useCdpDetalle(id: number | string | undefined) {
  const query = useQuery<CdpDetalleResponse>({
    queryKey: ['cdp-detalle', id],
    queryFn: () => api.get<CdpDetalleResponse>(`/casas_de_paz/${id}`),
    enabled: Boolean(id),
    staleTime: 1000 * 60 * 2,
  });

  return {
    cdp: query.data?.cdp,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}

export function useEstructuraSelectores(cdpId?: number | string) {
  const query = useQuery<EstructuraSelectoresResponse>({
    queryKey: ['selectores-estructura', cdpId],
    queryFn: () =>
      api.get<EstructuraSelectoresResponse>('/estructura/selectores', {
        params: cdpId ? { cdp_id: cdpId } : undefined,
      }),
    staleTime: 1000 * 60 * 5,
  });

  return {
    selectores: query.data,
    supervisores: query.data?.supervisores || [],
    lideresCdp: query.data?.lideres_cdp || [],
    casasDePaz: query.data?.casas_de_paz || [],
    redes: query.data?.redes || [],
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}

export function useEstructuraMutations() {
  const queryClient = useQueryClient();

  const invalidateEstructura = () => {
    queryClient.invalidateQueries({ queryKey: ['redes'] });
    queryClient.invalidateQueries({ queryKey: ['casas'] });
    queryClient.invalidateQueries({ queryKey: ['cdp-detalle'] });
    queryClient.invalidateQueries({ queryKey: ['lideres'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    queryClient.invalidateQueries({ queryKey: ['selectores-estructura'] });
  };

  // Mutaciones de Red
  const crearRedMutation = useMutation({
    mutationFn: (data: RedInput) => api.post<{ success: boolean; message: string }>('/redes', data),
    onSuccess: invalidateEstructura,
  });

  const editarRedMutation = useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: RedInput }) =>
      api.put<{ success: boolean; message: string }>(`/redes/${id}`, data),
    onSuccess: invalidateEstructura,
  });

  const toggleRedMutation = useMutation({
    mutationFn: (id: number | string) =>
      api.post<{ success: boolean; message: string }>(`/redes/${id}/toggle`),
    onSuccess: invalidateEstructura,
  });

  const eliminarRedMutation = useMutation({
    mutationFn: (id: number | string) =>
      api.delete<{ success: boolean; message: string }>(`/redes/${id}`),
    onSuccess: invalidateEstructura,
  });

  // Mutaciones de Casa de Paz
  const crearCdpMutation = useMutation({
    mutationFn: (data: CdpInput) =>
      api.post<{ success: boolean; message: string }>('/casas_de_paz', data),
    onSuccess: invalidateEstructura,
  });

  const editarCdpMutation = useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: Partial<CdpInput> }) =>
      api.put<{ success: boolean; message: string }>(`/casas_de_paz/${id}`, data),
    onSuccess: invalidateEstructura,
  });

  const toggleCdpMutation = useMutation({
    mutationFn: (id: number | string) =>
      api.post<{ success: boolean; status?: string; message: string }>(`/casas_de_paz/${id}/toggle`),
    onSuccess: invalidateEstructura,
  });

  const eliminarCdpMutation = useMutation({
    mutationFn: (id: number | string) =>
      api.delete<{ success: boolean; message: string }>(`/casas_de_paz/${id}`),
    onSuccess: invalidateEstructura,
  });

  // Mutaciones de Líder
  const crearLiderMutation = useMutation({
    mutationFn: (data: LiderInput) =>
      api.post<{ success: boolean; message: string }>('/lideres', data),
    onSuccess: invalidateEstructura,
  });

  const editarLiderMutation = useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: Partial<LiderInput> }) =>
      api.put<{ success: boolean; message: string }>(`/lideres/${id}`, data),
    onSuccess: invalidateEstructura,
  });

  return {
    crearRed: crearRedMutation.mutateAsync,
    isCreandoRed: crearRedMutation.isPending,
    editarRed: editarRedMutation.mutateAsync,
    isEditandoRed: editarRedMutation.isPending,
    toggleRed: toggleRedMutation.mutateAsync,
    isTogglingRed: toggleRedMutation.isPending,
    eliminarRed: eliminarRedMutation.mutateAsync,
    isEliminandoRed: eliminarRedMutation.isPending,

    crearCdp: crearCdpMutation.mutateAsync,
    isCreandoCdp: crearCdpMutation.isPending,
    editarCdp: editarCdpMutation.mutateAsync,
    isEditandoCdp: editarCdpMutation.isPending,
    toggleCdp: toggleCdpMutation.mutateAsync,
    isTogglingCdp: toggleCdpMutation.isPending,
    eliminarCdp: eliminarCdpMutation.mutateAsync,
    isEliminandoCdp: eliminarCdpMutation.isPending,

    crearLider: crearLiderMutation.mutateAsync,
    isCreandoLider: crearLiderMutation.isPending,
    editarLider: editarLiderMutation.mutateAsync,
    isEditandoLider: editarLiderMutation.isPending,
  };
}

