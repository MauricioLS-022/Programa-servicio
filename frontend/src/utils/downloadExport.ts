/**
 * Utilidad para descargar exportaciones binarias autenticadas (PDF, XLSX, CSV)
 * desde `/api/export/*`, preservando el nombre de archivo de Content-Disposition
 * y traduciendo respuestas JSON de error a ApiError.
 */
import { ApiError } from '../api/client';

const BASE_URL = import.meta.env?.VITE_API_URL || '/api';

export type ExportFormat = 'pdf' | 'xlsx' | 'csv';
export type ExportResource = 'reportes' | 'usuarios' | 'lideres' | 'casas_de_paz';

export interface DownloadExportOptions {
  resource: ExportResource;
  format: ExportFormat;
  params?: Record<string, string | number | boolean | undefined | null>;
  fallbackFilename?: string;
}

export function extractFilenameFromDisposition(
  header: string | null | undefined,
  fallback: string
): string {
  if (!header) return fallback;
  const utf8Match = header.match(/filename\*=UTF-8''([^;\n]+)/i);
  if (utf8Match?.[1]) {
    try {
      return decodeURIComponent(utf8Match[1].trim());
    } catch {
      return utf8Match[1].trim();
    }
  }
  const simpleMatch = header.match(/filename="?([^";\n]+)"?/i);
  if (simpleMatch?.[1]) {
    return simpleMatch[1].trim();
  }
  return fallback;
}

export function buildExportUrl(
  resource: ExportResource,
  format: ExportFormat,
  params?: Record<string, string | number | boolean | undefined | null>
): string {
  const qs = new URLSearchParams();
  qs.set('format', format);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null && String(v).trim() !== '') {
        qs.set(k, String(v).trim());
      }
    }
  }
  return `${BASE_URL}/export/${resource}?${qs.toString()}`;
}

export async function downloadExport({
  resource,
  format,
  params,
  fallbackFilename,
}: DownloadExportOptions): Promise<string> {
  const url = buildExportUrl(resource, format, params);
  const res = await fetch(url, {
    method: 'GET',
    credentials: 'include',
  });

  if (!res.ok) {
    let message = `Error al generar la exportación (HTTP ${res.status}).`;
    let payload: unknown = null;
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      try {
        payload = await res.json();
        if (payload && typeof payload === 'object') {
          const obj = payload as { error?: string; message?: string };
          message = obj.error || obj.message || message;
        }
      } catch {
        // Ignorar fallo de parseo
      }
    }
    throw new ApiError(res.status, message, payload);
  }

  const blob = await res.blob();
  const today = new Date().toISOString().split('T')[0];
  const defaultName = fallbackFilename || `${resource}_${today}.${format}`;
  const filename = extractFilenameFromDisposition(
    res.headers.get('content-disposition'),
    defaultName
  );

  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(objectUrl);

  return filename;
}
