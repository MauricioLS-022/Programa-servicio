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

export interface TendenciaItem {
  semana: string;
  fecha_completa?: string;
  asistencia: number;
  porcentaje?: number | null;
  num_mes?: number;
  rango_fecha?: string;
}

export interface DistribucionAsistencia {
  regulares: number;
  ninos: number;
  visitas: number;
  comprometidos: number;
}

export interface RankingRedItem {
  nombre: string;
  supervisor: string;
  cumplimiento: number;
  asistencia: number;
  asistencia_semana?: number;
  asistencia_total?: number;
  casas_reportadas?: number;
  total_casas?: number;
  color_class?: string;
}

export interface AlertaSeguimiento {
  nombre: string;
  codigo: string;
  red?: string;
  dias_sin_reporte: number;
  motivo: string;
  lider: string;
  telefono?: string;
}

export interface TopCrecimiento {
  nombre?: string;
  codigo?: string;
  tasa?: string | number;
  visitas?: number;
  lider?: string;
  crecimiento?: number;
}

export interface LiderRedItem {
  id?: number;
  nombre: string;
  rol?: string;
  telefono?: string;
  cdp_codigo?: string;
  cdp_anfitrion?: string;
}

export interface CasaDetalleZonal {
  id: number;
  codigo: string;
  anfitrion?: string;
  lider: string;
  asistencia: number;
  visitas: number;
  telefono?: string;
  nombre?: string;
  red_id?: number;
  is_active?: number | boolean;
  dias_desde_reporte?: number | null;
  tiene_reporte_7d?: number | boolean;
}

export interface ActividadRecienteItem {
  lider: string;
  cdp_codigo: string;
  cdp_nombre?: string;
  fecha_formateada?: string;
  asistencia: number;
  tema?: string;
  iniciales?: string;
  avatar_class?: string;
}

export interface DashboardMetricas {
  total_asistencia?: number;
  asistencia_total?: number;
  cumplimiento?: number;
  ofrendas_usd?: number;
  ofrendas_bs?: number;
  conversiones?: number;
  reconciliaciones?: number;
  cestas_amor?: number;
  total_visitas?: number;
  total_casas?: number;
  casas_con_reporte?: number;
  casas_pendientes?: number;
  total_sin_reporte_7d?: number;
  casas_sin_reporte_ids?: number[];
  casas_sin_reporte_codigos?: string[];
  casas_sin_reporte_7d?: string[];
  reportes_enviados?: number;
  distribucion?: DistribucionAsistencia;
  tendencia?: TendenciaItem[];
  tendencia_semanas?: TendenciaItem[];
  promedio_tendencia?: number;
  ranking_redes?: RankingRedItem[];
  alertas?: AlertaSeguimiento[];
  alertas_zonal?: AlertaSeguimiento[];
  top_crecimiento?: TopCrecimiento;
  lideres_red?: LiderRedItem[];
  casas?: CasaDetalleZonal[];
  actividad_reciente?: ActividadRecienteItem[];
  nombre_red?: string;
  supervisor?: string;
  casas_activas?: number;
  promedio_casa?: number;
  periodo?: string;
  periodo_nombre?: string;
  nombre_mes?: string;
  mes_numero?: number;
  anio?: number;
  nombre_cdp?: string;
  codigo?: string;
  codigo_cdp?: string;
  lider?: string;
  sublider?: string;
  telefono?: string;
  direccion?: string;
  anfitrion?: string;
  sin_red_asignada?: boolean;
  estado_reporte?: 'enviado' | 'pendiente' | string;
  reporte_al_dia?: boolean;
  ultimo_reporte_por?: string;
  ultimo_reporte_fecha?: string;
  dias_desde_reporte?: number | null;
  asistencia_ultimo?: number;
  promedio_historico?: number;
  ultimo_tema?: string;
  hr_inicio?: string;
  hr_fin?: string;
  cesta_amor?: boolean;
  potencial_multiplicacion?: boolean;
  historial?: Array<{
    id?: number;
    fecha?: string;
    asistencia?: number;
    nro_regulares?: number;
    nro_niños?: number;
    nro_visitas?: number;
    nro_comprometidos?: number;
    ofrendas_usd?: number;
    ofrendas_bs?: number;
    confesiones?: number;
    tema?: string;
    observaciones?: string;
    enviado_por_nombre?: string;
    [key: string]: unknown;
  }>;

  // Retrocompatibilidad con componentes antiguos si aplica
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
  casas_resumen?: Array<{
    id: number;
    codigo: string;
    asistencia: number;
    sin_reporte_7d: boolean;
  }>;
  [key: string]: unknown;
}

