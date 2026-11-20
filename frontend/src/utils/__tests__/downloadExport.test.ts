import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  buildExportUrl,
  extractFilenameFromDisposition,
  downloadExport,
} from '../downloadExport';
import { ApiError } from '../../api/client';

describe('downloadExport utilities', () => {
  const originalCreateObjectURL = URL.createObjectURL;
  const originalRevokeObjectURL = URL.revokeObjectURL;

  beforeEach(() => {
    URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    URL.createObjectURL = originalCreateObjectURL;
    URL.revokeObjectURL = originalRevokeObjectURL;
  });

  it('construye la URL omitiendo parámetros vacíos o nulos', () => {
    const url = buildExportUrl('reportes', 'pdf', {
      q: 'Hebrón',
      red_id: 2,
      cdp_id: '',
      fecha_desde: undefined,
      fecha_hasta: null,
    });
    expect(url).toBe('/api/export/reportes?format=pdf&q=Hebr%C3%B3n&red_id=2');
  });

  it('extrae el nombre de archivo desde Content-Disposition (simple y UTF-8)', () => {
    expect(
      extractFilenameFromDisposition(
        'attachment; filename="reportes_consolidado_2026-11-18.pdf"',
        'fallback.pdf'
      )
    ).toBe('reportes_consolidado_2026-11-18.pdf');

    expect(
      extractFilenameFromDisposition(
        "attachment; filename*=UTF-8''directorio_l%C3%ADderes.xlsx",
        'fallback.xlsx'
      )
    ).toBe('directorio_líderes.xlsx');

    expect(extractFilenameFromDisposition(null, 'fallback.csv')).toBe('fallback.csv');
  });

  it('descarga el blob autenticado con el nombre del servidor y limpia ObjectURL', async () => {
    const mockBlob = new Blob(['%PDF-1.4'], { type: 'application/pdf' });
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({
        'content-disposition': 'attachment; filename="reportes_consolidado_2026-11-18.pdf"',
      }),
      blob: vi.fn().mockResolvedValue(mockBlob),
    } as unknown as Response);

    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});

    const filename = await downloadExport({
      resource: 'reportes',
      format: 'pdf',
      params: { red_id: '1' },
    });

    expect(filename).toBe('reportes_consolidado_2026-11-18.pdf');
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/export/reportes?format=pdf&red_id=1',
      expect.objectContaining({ method: 'GET', credentials: 'include' })
    );
    expect(clickSpy).toHaveBeenCalledTimes(1);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:mock-url');
  });

  it('lanza ApiError con el mensaje JSON cuando el backend devuelve 503 o 403', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 503,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: vi.fn().mockResolvedValue({
        success: false,
        error: 'Base de datos temporalmente no disponible.',
        code: 'db_unavailable',
      }),
    } as unknown as Response);

    await expect(
      downloadExport({ resource: 'usuarios', format: 'xlsx' })
    ).rejects.toThrow(ApiError);

    await expect(
      downloadExport({ resource: 'usuarios', format: 'xlsx' })
    ).rejects.toThrow('Base de datos temporalmente no disponible.');
  });
});
