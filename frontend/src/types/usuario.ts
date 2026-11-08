/**
 * Tipos de datos para el módulo de Gestión Administrativa de Usuarios
 */

export interface Usuario {
  id: string;
  username: string;
  nombre: string;
  apellido: string;
  rol?: string;
  tipo_usuario?: string;
  is_active: number | boolean;
  red_id?: number | string | null;
  red_nombre?: string | null;
  cdp_id?: number | string | null;
  cdp_codigo?: string | null;
}

export interface UsuariosResponse {
  usuarios: Usuario[];
  total: number;
  total_activos: number;
  page: number;
  pages: number;
  per_page: number;
}

export interface RedAsignacionOpcion {
  id: number;
  nombre: string;
}

export interface CdpAsignacionOpcion {
  id: number;
  codigo: string;
  direccion?: string;
  red_nombre?: string;
}

export interface UsuarioOpcionesAsignacion {
  redes: RedAsignacionOpcion[];
  casas_de_paz: CdpAsignacionOpcion[];
}

export interface UsuarioInput {
  nombre: string;
  apellido: string;
  username: string;
  password?: string;
  tipo_usuario: 'admin' | 'supervisor' | 'lider_cdp';
  red_id?: number | string | null;
  cdp_id?: number | string | null;
  is_active?: number | boolean | string;
}

