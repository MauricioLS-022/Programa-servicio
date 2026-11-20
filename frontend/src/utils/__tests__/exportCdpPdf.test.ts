import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { buildCdpFichaHtml, escapeHtml, exportCdpPdf } from '../exportCdpPdf';
import type { CdpDetalle } from '../../types/estructura';

const baseCdp: CdpDetalle = {
  id: 1,
  codigo: 'HEB-001',
  nombre: 'Casa Bethel',
  anfitrion: 'Familia Mendoza',
  direccion: 'Calle Principal #10',
  telefono: '+584121112233',
  horario: 'Miércoles · 7:00 PM',
  red_id: 1,
  red_nombre: 'Red Hebrón',
  supervisor_nombre: 'Pedro González',
  is_active: 1,
  reporte_reciente_7d: true,
  asistencia_promedio: 18,
  total_reportes: 6,
  ofrendas_usd_totales: 125.5,
  ofrendas_bs_totales: 4500.25,
  visitas_totales: 9,
  conversiones_totales: 3,
  lideres: [
    {
      id: 10,
      nombre_completo: 'Juan Pérez',
      iniciales: 'JP',
      rol: 'Lider',
      telefono: '+584140001122',
    },
  ],
  reportes: [
    {
      id: 'rep-1',
      fecha: '2026-10-21',
      fecha_formateada: '21 Oct 2026',
      tema: 'La Fe Activa',
      observaciones: 'Excelente participación',
      asistencia: 18,
      nro_regulares: 12,
      nro_ninos: 3,
      nro_visitas: 3,
      ofrendas_usd: 20,
      ofrendas_bs: 720,
      cesta_amor: 1,
    },
  ],
};

describe('exportCdpPdf & escapeHtml', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('escapa caracteres HTML especiales incluyendo etiquetas, comillas y ampersands', () => {
    expect(escapeHtml('<script>alert("xss")</script>')).toBe(
      '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
    );
    expect(escapeHtml("A & B 'test'")).toBe('A &amp; B &#39;test&#39;');
    expect(escapeHtml(null)).toBe('');
    expect(escapeHtml(undefined)).toBe('');
  });

  it('genera la ficha técnica HTML completa con KPIs, equipo e historial formateado', () => {
    const html = buildCdpFichaHtml(baseCdp, '18 de noviembre de 2026');

    expect(html).toContain('Ficha Técnica Oficial - Casa de Paz HEB-001');
    expect(html).toContain('18 de noviembre de 2026');
    expect(html).toContain('$125.50');
    expect(html).toContain('Bs. 4500.25');
    expect(html).toContain('Juan Pérez');
    expect(html).toContain('La Fe Activa');
    expect(html).toContain('Excelente participación');
    expect(html).toContain('$20.00 · Bs. 720.00');
    expect(html).toContain('>Sí<');
  });

  it('renderiza estados vacíos y valores por defecto cuando no hay líderes ni reportes', () => {
    const emptyCdp: CdpDetalle = {
      ...baseCdp,
      direccion: '',
      anfitrion: '',
      telefono: '',
      horario: '',
      lideres: [],
      reportes: [],
    };
    const html = buildCdpFichaHtml(emptyCdp, '18 Nov 2026');

    expect(html).toContain('No hay líderes asignados.');
    expect(html).toContain('Sin reportes registrados aún.');
    expect(html).toContain('No registrada');
    expect(html).toContain('Sin asignar');
    expect(html).toContain('Miércoles · 7:00 PM');
  });

  it('neutraliza payloads XSS en todos los campos dinámicos de la casa, equipo y reportes', () => {
    const xssPayload = '<img src=x onerror="alert(1)"><script>evil()</script>';
    const maliciousCdp: CdpDetalle = {
      ...baseCdp,
      codigo: `HEB-${xssPayload}`,
      anfitrion: xssPayload,
      direccion: xssPayload,
      red_nombre: xssPayload,
      supervisor_nombre: xssPayload,
      lideres: [
        {
          id: 1,
          nombre_completo: xssPayload,
          iniciales: 'XY',
          rol: 'Lider',
          telefono: '<script>tel()</script>',
        },
      ],
      reportes: [
        {
          id: 'rep-xss',
          fecha: '2026-10-21',
          tema: xssPayload,
          observaciones: '<svg onload=alert(2)>',
          asistencia: 5,
          nro_regulares: 5,
          nro_ninos: 0,
          nro_visitas: 0,
          ofrendas_usd: 0,
          ofrendas_bs: 0,
          cesta_amor: 0,
        },
      ],
    };

    const html = buildCdpFichaHtml(maliciousCdp, '<b>fecha</b>');

    expect(html).not.toContain('<script>');
    expect(html).not.toContain('<img src=x');
    expect(html).not.toContain('<svg onload');
    expect(html).toContain('&lt;script&gt;evil()&lt;/script&gt;');
    expect(html).toContain('&lt;svg onload=alert(2)&gt;');
    expect(html).toContain('&lt;b&gt;fecha&lt;/b&gt;');
  });

  it('crea el iframe oculto, escribe el documento y dispara focus + print', () => {
    const writeSpy = vi.fn();
    const openSpy = vi.fn();
    const closeSpy = vi.fn();
    const focusSpy = vi.fn();
    const printSpy = vi.fn();

    const originalCreate = document.createElement.bind(document);
    vi.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
      const el = originalCreate(tagName);
      if (tagName.toLowerCase() === 'iframe') {
        Object.defineProperty(el, 'contentWindow', {
          value: {
            document: { open: openSpy, write: writeSpy, close: closeSpy },
            focus: focusSpy,
            print: printSpy,
          },
          configurable: true,
        });
      }
      return el;
    });

    exportCdpPdf(baseCdp);

    expect(document.getElementById('print-cdp-iframe')).not.toBeNull();
    expect(openSpy).toHaveBeenCalledTimes(1);
    expect(writeSpy).toHaveBeenCalledWith(expect.stringContaining('HEB-001'));
    expect(closeSpy).toHaveBeenCalledTimes(1);

    vi.advanceTimersByTime(300);
    expect(focusSpy).toHaveBeenCalledTimes(1);
    expect(printSpy).toHaveBeenCalledTimes(1);
  });

  it('ejecuta fallback window.print() si ocurre una excepción al crear o escribir en el iframe', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const windowPrintSpy = vi.spyOn(window, 'print').mockImplementation(() => {});
    vi.spyOn(document, 'createElement').mockImplementation(() => {
      throw new Error('DOM bloqueado');
    });

    exportCdpPdf(baseCdp);

    expect(consoleErrorSpy).toHaveBeenCalled();
    expect(windowPrintSpy).toHaveBeenCalledTimes(1);
  });
});
