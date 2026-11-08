/**
/**
 * Types para el Dashboard de Líder de Casa de Paz.
 * Paridad con el contexto de Jinja2 (index.html).
 */

export interface LiderCdpInfo {
  id: number | string;
  codigo: string;
  anfitrion?: string;
  direccion?: string;
  telefono?: string;
  red_id?: number;
}

export interface LiderMiembro {
  id: number | string;
  nombre: string;
  apellido?: string;
  rol: 'Lider' | 'Sublider' | string;
  telefono?: string;
}

export interface LiderMetricas {
  total_reportes: number;
  asistencia_promedio: number;
  ofrendas_usd_totales: number;
  ofrendas_bs_totales: number;
  visitas_totales: number;
  conversiones_totales: number;
  reconciliaciones_totales: number;
  reporte_esta_semana: boolean;
  dias_cierre_texto?: string;
}

export interface LiderReporteItem {
  id: string | number;
  fecha: string;
  fecha_formateada?: string;
  hr_inicio?: string;
  hr_fin?: string;
  lider_nombre: string;
  enviado_por_lider_id?: string | number;
  iniciales?: string;
  tema: string;
  asistencia: number;
  nro_regulares?: number;
  nro_niños?: number;
  nro_visitas?: number;
  nro_comprometidos?: number;
  reconciliaciones?: number;
  confesiones?: number;
  ofrendas_usd?: number;
  ofrendas_bs?: number;
  cesta_amor?: string | number | boolean;
  observaciones?: string;
}

export interface LiderDashboardData {
  cdp: LiderCdpInfo | null;
  lideres: LiderMiembro[];
  metricas: LiderMetricas;
  reportes: LiderReporteItem[];
  total_reportes: number;
  page: number;
  pages: number;
  tiene_cdp: boolean;
}
