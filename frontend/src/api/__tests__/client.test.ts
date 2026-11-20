import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api, ApiError, resetCsrfToken } from '../client';

function createMockResponse(options: {
  ok: boolean;
  status: number;
  statusText?: string;
  contentType?: string;
  body?: unknown;
}) {
  const { ok, status, statusText = '', contentType = 'application/json', body = {} } = options;
  return {
    ok,
    status,
    statusText,
    headers: {
      get: (key: string) => (key.toLowerCase() === 'content-type' ? contentType : null),
    },
    json: vi.fn().mockResolvedValue(body),
    text: vi.fn().mockResolvedValue(typeof body === 'string' ? body : JSON.stringify(body)),
  };
}

describe('HTTP API Client (client.ts)', () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    resetCsrfToken();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    resetCsrfToken();
    vi.unstubAllGlobals();
  });

  it('envía credentials: include, construye query params omitiendo null/undefined/vacíos y parsea JSON', async () => {
    fetchMock.mockResolvedValue(createMockResponse({ ok: true, status: 200, body: { total: 3 } }));

    const data = await api.get<{ total: number }>('/reportes', {
      params: {
        page: 2,
        q: 'fe',
        red_id: '',
        cdp_id: undefined,
        extra: null,
        activo: true,
      },
    });

    expect(data).toEqual({ total: 3 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, config] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/reportes?page=2&q=fe&activo=true');
    expect(config.method).toBe('GET');
    expect(config.credentials).toBe('include');
    expect(config.headers).toMatchObject({
      Accept: 'application/json',
      'Content-Type': 'application/json',
    });
  });

  it('obtiene y cachea X-CSRFToken automáticamente en mutaciones POST, PUT y DELETE', async () => {
    fetchMock
      // 1. Consulta automática de token CSRF
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 200, body: { csrf_token: 'tok-abc-123' } }))
      // 2. POST /redes
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 201, body: { success: true } }))
      // 3. PUT /redes/1 (reutiliza token cacheado sin pedir de nuevo)
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 200, body: { success: true } }))
      // 4. DELETE /redes/1 (reutiliza token cacheado)
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 200, body: { success: true } }));

    await api.post('/redes', { nombre: 'Hebrón' });
    await api.put('redes/1', { nombre: 'Hebrón Norte' });
    await api.delete('/redes/1');

    expect(fetchMock).toHaveBeenCalledTimes(4);
    expect(fetchMock.mock.calls[0][0]).toBe('/api/auth/csrf-token');

    const [postUrl, postConfig] = fetchMock.mock.calls[1];
    expect(postUrl).toBe('/api/redes');
    expect(postConfig.method).toBe('POST');
    expect(postConfig.body).toBe(JSON.stringify({ nombre: 'Hebrón' }));
    expect(postConfig.headers['X-CSRFToken']).toBe('tok-abc-123');

    const [putUrl, putConfig] = fetchMock.mock.calls[2];
    expect(putUrl).toBe('/api/redes/1');
    expect(putConfig.method).toBe('PUT');
    expect(putConfig.headers['X-CSRFToken']).toBe('tok-abc-123');

    const [delUrl, delConfig] = fetchMock.mock.calls[3];
    expect(delUrl).toBe('/api/redes/1');
    expect(delConfig.method).toBe('DELETE');
    expect(delConfig.headers['X-CSRFToken']).toBe('tok-abc-123');
  });

  it('reintenta una sola vez tras refrescar el token cuando el servidor responde 400 csrf_error', async () => {
    fetchMock
      // Token inicial expirado
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 200, body: { csrf_token: 'tok-old' } }))
      // Primer POST falla con csrf_error
      .mockResolvedValueOnce(
        createMockResponse({
          ok: false,
          status: 400,
          body: { success: false, error: 'Token CSRF expirado', code: 'csrf_error' },
        })
      )
      // Refresco de token
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 200, body: { csrf_token: 'tok-fresh' } }))
      // Reintento exitoso
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 201, body: { success: true } }));

    const res = await api.post<{ success: boolean }>('/redes', { nombre: 'Betel' });
    expect(res.success).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(4);
    expect(fetchMock.mock.calls[1][1].headers['X-CSRFToken']).toBe('tok-old');
    expect(fetchMock.mock.calls[3][1].headers['X-CSRFToken']).toBe('tok-fresh');
  });

  it('omite Content-Type: application/json cuando el body es FormData', async () => {
    fetchMock
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 200, body: { csrf_token: 'tok-fd' } }))
      .mockResolvedValueOnce(createMockResponse({ ok: true, status: 200, body: { ok: true } }));
    const formData = new FormData();
    formData.append('tema', 'Oración');

    await api.post('/reportes', formData);

    const [, config] = fetchMock.mock.calls[1];
    expect(config.body).toBe(formData);
    expect(config.headers['Content-Type']).toBeUndefined();
    expect(config.headers['Accept']).toBe('application/json');
    expect(config.headers['X-CSRFToken']).toBe('tok-fd');
  });

  it('lanza ApiError con mensaje estructurado en respuestas 400, 401, 429, 500 y 503', async () => {
    const cases = [
      { status: 400, body: { error: 'Payload inválido', details: [{ field: 'tema' }] }, expectedMsg: 'Payload inválido' },
      { status: 401, body: { error: 'No autenticado' }, expectedMsg: 'No autenticado' },
      { status: 429, body: { error: 'Demasiados intentos' }, expectedMsg: 'Demasiados intentos' },
      { status: 500, body: { message: 'Error interno del servidor' }, expectedMsg: 'Error interno del servidor' },
      { status: 503, body: { error: 'Servicio temporalmente no disponible' }, expectedMsg: 'Servicio temporalmente no disponible' },
    ];

    for (const c of cases) {
      fetchMock.mockResolvedValueOnce(
        createMockResponse({ ok: false, status: c.status, body: c.body })
      );
      await expect(api.get('/dashboard/datos')).rejects.toMatchObject({
        name: 'ApiError',
        status: c.status,
        message: c.expectedMsg,
        data: c.body,
      });
    }
  });

  it('maneja respuestas no-JSON (HTML/texto plano) tanto exitosas como de error HTTP', async () => {
    fetchMock.mockResolvedValueOnce(
      createMockResponse({
        ok: true,
        status: 200,
        contentType: 'text/plain',
        body: 'OK',
      })
    );
    const textResult = await api.get<string>('/health');
    expect(textResult).toBe('OK');

    fetchMock.mockResolvedValueOnce(
      createMockResponse({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        contentType: 'text/html',
        body: '<html><body>503 Service Unavailable</body></html>',
      })
    );

    try {
      await api.get('/dashboard/datos');
      expect.unreachable('Debió lanzar ApiError');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      const apiErr = err as ApiError;
      expect(apiErr.status).toBe(503);
      expect(apiErr.message).toBe('Error HTTP 503: Service Unavailable');
      expect(apiErr.data).toContain('503 Service Unavailable');
    }
  });
});
