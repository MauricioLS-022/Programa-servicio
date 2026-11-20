/**
 * Cliente HTTP base para la API REST.
 * 100% libre de dependencias del DOM para máxima portabilidad (Web y React Native).
 */

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

const BASE_URL = import.meta.env?.VITE_API_URL || '/api';

const MUTATING_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

let cachedCsrfToken: string | null = null;
let csrfTokenPromise: Promise<string | null> | null = null;

export function resetCsrfToken(): void {
  cachedCsrfToken = null;
  csrfTokenPromise = null;
}

async function fetchCsrfToken(): Promise<string | null> {
  if (cachedCsrfToken) {
    return cachedCsrfToken;
  }
  if (!csrfTokenPromise) {
    csrfTokenPromise = (async () => {
      try {
        const res = await fetch(`${BASE_URL}/auth/csrf-token`, {
          method: 'GET',
          credentials: 'include',
          headers: { Accept: 'application/json' },
        });
        if (!res.ok) return null;
        const contentType = res.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) return null;
        const body = (await res.json()) as { csrf_token?: string };
        if (typeof body?.csrf_token === 'string' && body.csrf_token) {
          cachedCsrfToken = body.csrf_token;
          return cachedCsrfToken;
        }
        return null;
      } catch {
        return null;
      } finally {
        csrfTokenPromise = null;
      }
    })();
  }
  return csrfTokenPromise;
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>;
}

async function request<T>(endpoint: string, options: RequestOptions = {}, isRetry = false): Promise<T> {
  const { params, headers, ...customConfig } = options;

  let url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        searchParams.append(key, String(val));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString;
    }
  }

  const method = (customConfig.method || 'GET').toUpperCase();
  const isMutating = MUTATING_METHODS.has(method);

  const defaultHeaders: Record<string, string> = {
    'Accept': 'application/json',
  };

  if (!(customConfig.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  if (isMutating) {
    const providedHeaders = (headers as Record<string, string> | undefined) || {};
    const hasExplicitCsrf = Boolean(providedHeaders['X-CSRFToken'] || providedHeaders['X-CSRF-Token']);
    if (!hasExplicitCsrf) {
      const token = await fetchCsrfToken();
      if (token) {
        defaultHeaders['X-CSRFToken'] = token;
      }
    }
  }

  const response = await fetch(url, {
    credentials: 'include', // Imprescindible para transporte de cookies HttpOnly
    headers: {
      ...defaultHeaders,
      ...(headers as Record<string, string>),
    },
    ...customConfig,
  });

  const contentType = response.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const isCsrfError =
      response.status === 400 &&
      typeof data === 'object' &&
      data !== null &&
      (data as { code?: string }).code === 'csrf_error';

    if (isCsrfError && isMutating && !isRetry) {
      resetCsrfToken();
      return request<T>(endpoint, options, true);
    }

    const errorMessage =
      (typeof data === 'object' && data !== null && 'error' in data ? (data as { error: string }).error : null) ||
      (typeof data === 'object' && data !== null && 'message' in data ? (data as { message: string }).message : null) ||
      `Error HTTP ${response.status}: ${response.statusText}`;

    throw new ApiError(response.status, errorMessage, data);
  }

  // Sincronizar caché de token CSRF tras respuestas de autenticación
  if (typeof data === 'object' && data !== null && typeof (data as { csrf_token?: unknown }).csrf_token === 'string') {
    const returnedToken = (data as { csrf_token: string }).csrf_token;
    if (returnedToken) {
      cachedCsrfToken = returnedToken;
    }
  } else if (endpoint === '/auth/login' || endpoint === '/auth/logout') {
    resetCsrfToken();
  }

  return data as T;
}

export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { method: 'GET', ...options }),

  post: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      method: 'POST',
      body: body instanceof FormData ? body : JSON.stringify(body),
      ...options,
    }),

  put: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      method: 'PUT',
      body: body instanceof FormData ? body : JSON.stringify(body),
      ...options,
    }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { method: 'DELETE', ...options }),
};

