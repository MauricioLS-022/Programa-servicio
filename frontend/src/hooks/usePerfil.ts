/**
 * Hook de Perfil Ministerial con TanStack Query.
 * Permite acceder a los datos de identidad y contexto asignado (Red / CDP) del usuario en sesión.
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export interface PerfilData {
  id: number | string;
  username: string;
  nombre: string;
  apellido: string;
  tipo_usuario: string;
  red_id?: number;
  red_nombre?: string;
  red_asignada?: string;
  cdp_id?: number;
  cdp_codigo?: string;
  cdp_nombre?: string;
  cdp_anfitrion?: string;
  cdp_asignada?: string;
  asignacion_admin?: string;
}

export interface PerfilResponse {
  perfil: PerfilData;
  usuario: string;
  rol: string;
  error?: string;
}

export const PERFIL_QUERY_KEY = ['perfil'];

export function usePerfil() {
  const query = useQuery<PerfilResponse>({
    queryKey: PERFIL_QUERY_KEY,
    queryFn: () => api.get<PerfilResponse>('/perfil'),
    staleTime: 1000 * 60 * 5, // 5 minutos de caché
  });

  return {
    perfil: query.data?.perfil,
    usuario: query.data?.usuario,
    rol: query.data?.rol,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}

