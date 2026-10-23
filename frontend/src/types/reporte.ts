/**
 * Tipos de datos para el módulo de Reportes de Casa de Paz.
 * Alineado estrictamente con el esquema relacional de MySQL y las vistas canónicas.
 */

export interface Reporte {
  id: string; // UUID
  cdp_id: number;
  fecha: string; // YYYY-MM-DD
  fecha_formateada?: string;
  hr_inicio?: string; // HH:MM
  hr_fin?: string; // HH:MM
  tema: string;
  nro_regulares: number;
  nro_ninos?: number;
  nro_niños?: number;
  nro_visitas: number;
  nro_comprometidos: number;
  asistencia: number; // regulares + niños + visitas + comprometidos
  reconciliaciones: number;
  confesiones: number;
  cesta_amor: boolean | number;
  cesta_amor_desc?: string;
  ofrendas_usd: number;
  ofrendas_bs: number;
  total_usd?: number;
  total_bs?: number;
  ofrenda_efectivo_usd?: number;
  ofrenda_efectivo_bs?: number;
  observaciones?: string;
  enviado_por_lider_id?: number;
  lider_nombre?: string;
  iniciales?: string;
  cdp_codigo?: string;
  cdp_nombre?: string;
  cdp_anfitrion?: string;
  red_id?: number;
  red_nombre?: string;
}

export interface ReporteFiltros {
  q?: string;
  red_id?: number | string;
  cdp_id?: number | string;
  fecha_desde?: string;
  fecha_hasta?: string;
  page?: number;
  per_page?: number;
}

export interface ReporteFormPayload {
  cdp_id?: number;
  lider_id?: number | string;
  fecha: string;
  hr_inicio: string;
  hr_fin: string;
  tema: string;
  nro_regulares: number;
  nro_ninos: number;
  nro_visitas: number;
  nro_comprometidos: number;
  reconciliaciones: number;
  confesiones: number;
  cesta_amor: boolean | number | string;
  ofrendas_usd: number;
  ofrendas_bs: number;
  observaciones?: string;
}

export interface ReportesResponse {
  reportes: Reporte[];
  total: number;
  page: number;
  pages: number;
  per_page: number;
}

export interface ProcesarReporteResponse {
  success: boolean;
  message?: string;
  error?: string;
  cdp_id?: number;
}
