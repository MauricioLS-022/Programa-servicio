/**
 * Tipos de datos para el módulo de Reportes de Casa de Paz
 */

export interface Reporte {
  id: number;
  cdp_id: number;
  fecha: string;
  tema?: string;
  asistencia: number;
  hermanos?: number;
  amigos?: number;
  ninos?: number;
  ofrenda_efectivo_usd?: number;
  ofrenda_efectivo_bs?: number;
  ofrenda_digital_usd?: number;
  ofrenda_digital_bs?: number;
  total_usd?: number;
  total_bs?: number;
  tasa_cambio?: number;
  motivo_oracion?: string;
  observaciones?: string;
  cesta_amor?: boolean | number;
  enviado_por_lider_id?: number;
  cdp_codigo?: string;
  cdp_anfitrion?: string;
  red_nombre?: string;
  red_id?: number;
  lider_nombre?: string;
  lider_apellido?: string;
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
  fecha: string;
  tema?: string;
  asistencia: number;
  hermanos?: number;
  amigos?: number;
  ninos?: number;
  ofrenda_efectivo_usd?: number;
  ofrenda_efectivo_bs?: number;
  ofrenda_digital_usd?: number;
  ofrenda_digital_bs?: number;
  tasa_cambio?: number;
  motivo_oracion?: string;
  observaciones?: string;
  cesta_amor?: boolean | number | string;
  lider_id?: number;
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

