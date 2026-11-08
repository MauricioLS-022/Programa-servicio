import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type {
  UsuariosResponse,
  UsuarioOpcionesAsignacion,
  UsuarioInput,
} from '../types/usuario';

export interface UseUsuariosParams {
  q?: string;
  rol?: string;
  page?: number;
  per_page?: number;
}

export function useUsuarios(params: UseUsuariosParams = {}) {
  const query = useQuery<UsuariosResponse>({
    queryKey: ['usuarios', params],
    queryFn: () =>
      api.get<UsuariosResponse>('/usuarios', {
        params: {
          q: params.q || undefined,
          rol: params.rol || undefined,
          page: params.page || 1,
          per_page: params.per_page || 100, // Fetch amplio para soportar Live Search en memoria
        },
      }),
    staleTime: 1000 * 60 * 2, // 2 minutos
  });

  return {
    usuarios: query.data?.usuarios || [],
    total: query.data?.total || 0,
    totalActivos: query.data?.total_activos || 0,
    page: query.data?.page || 1,
    pages: query.data?.pages || 1,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}

export function useUsuarioOpcionesAsignacion(usuarioId?: string | null) {
  const query = useQuery<UsuarioOpcionesAsignacion>({
    queryKey: ['usuario-opciones-asignacion', usuarioId],
    queryFn: () =>
      api.get<UsuarioOpcionesAsignacion>('/usuarios/opciones_asignacion', {
        params: usuarioId ? { usuario_id: usuarioId } : undefined,
      }),
    staleTime: 1000 * 60 * 5,
  });

  return {
    redes: query.data?.redes || [],
    casasDePaz: query.data?.casas_de_paz || [],
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}

export function useUsuarioMutations() {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    queryClient.invalidateQueries({ queryKey: ['usuario-opciones-asignacion'] });
    queryClient.invalidateQueries({ queryKey: ['selectores-estructura'] });
    queryClient.invalidateQueries({ queryKey: ['lideres'] });
    queryClient.invalidateQueries({ queryKey: ['redes'] });
    queryClient.invalidateQueries({ queryKey: ['casas'] });
  };

  const crearMutation = useMutation({
    mutationFn: (data: UsuarioInput) =>
      api.post<{ success: boolean; message: string }>('/usuarios', data),
    onSuccess: invalidate,
  });

  const editarMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<UsuarioInput> }) =>
      api.put<{ success: boolean; message: string }>(`/usuarios/${id}`, data),
    onSuccess: invalidate,
  });

  const toggleMutation = useMutation({
    mutationFn: (id: string) =>
      api.post<{ success: boolean; status?: string; message: string }>(`/usuarios/${id}/toggle`),
    onSuccess: invalidate,
  });

  const eliminarMutation = useMutation({
    mutationFn: (id: string) =>
      api.delete<{ success: boolean; message: string }>(`/usuarios/${id}`),
    onSuccess: invalidate,
  });

  return {
    crearUsuario: crearMutation.mutateAsync,
    isCreando: crearMutation.isPending,
    editarUsuario: editarMutation.mutateAsync,
    isEditando: editarMutation.isPending,
    toggleUsuario: toggleMutation.mutateAsync,
    isToggling: toggleMutation.isPending,
    eliminarUsuario: eliminarMutation.mutateAsync,
    isEliminando: eliminarMutation.isPending,
  };
}

