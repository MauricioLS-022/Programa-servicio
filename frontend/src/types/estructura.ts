/**
 * Tipos de datos para Estructura Ministerial (Redes, Casas de Paz, Líderes y Métricas)
 */

export interface Red {
  id: number;
  nombre: string;
  is_active: number | boolean;
  supervisor_id?: string | null;
  supervisor_nombre?: string;
  supervisor_username?: string;
}

export interface CasaDePaz {
  id: number;
  codigo: string;
  red_id: number;
  anfitrion?: string;
  direccion?: string;
  telefono?: string;
  dia_semana?: string;
  hora?: string;
  is_active: number | boolean;
  red_nombre?: string;
  total_lideres?: number;
  sin_reporte_7d?: boolean;
}

export interface Lider {
  id: number;
  nombre: string;
  apellido: string;
  telefono?: string;
  rol?: string;
  cdp_id?: number | null;
  cdp_codigo?: string;
  red_id?: number;
  red_nombre?: string;
  is_active: number | boolean;
}

export interface RedesResponse {
  redes: Red[];
}

export interface CasasResponse {
  casas: CasaDePaz[];
  total: number;
  sin_reporte_7d_ids?: number[];
}

export interface LideresResponse {
  lideres: Lider[];
  total: number;
  page: number;
  pages: number;
  per_page: number;
}

export interface DashboardMetricas {
  kpis?: {
    total_asistencia?: number;
    promedio_asistencia?: number;
    total_ofrenda_usd?: number;
    total_ofrenda_bs?: number;
    total_hermanos?: number;
    total_amigos?: number;
    total_ninos?: number;
  };
  grafico?: {
    labels?: string[];
    asistencia?: number[];
    fechas_rango?: string[];
    interpolado?: boolean;
  };
  ranking_redes?: Array<{
    red_id: number;
    nombre: string;
    asistencia: number;
  }>;
  casas_resumen?: Array<{
    id: number;
    codigo: string;
    asistencia: number;
    sin_reporte_7d: boolean;
  }>;
  [key: string]: unknown;
}

