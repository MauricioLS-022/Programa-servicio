import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { LoginPage } from '../LoginPage';
import { ApiError } from '../../api/client';

// Mocks de navegación y toasts
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: null }),
  };
});

const mockSuccess = vi.fn();
const mockToastError = vi.fn();
vi.mock('../../context/ToastContext', () => ({
  useToast: () => ({
    success: mockSuccess,
    error: mockToastError,
  }),
}));

const mockToggleTheme = vi.fn();
vi.mock('../../context/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'light',
    toggleTheme: mockToggleTheme,
  }),
}));

let mockLoginFn = vi.fn();
let mockIsLoggingIn = false;
let mockAuthConfig: { siteKey: string; isDev: boolean } = { siteKey: '', isDev: false };

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    login: mockLoginFn,
    isLoggingIn: mockIsLoggingIn,
    isAuthenticated: false,
    user: undefined,
  }),
  useAuthConfig: () => ({
    data: mockAuthConfig,
    isLoading: false,
  }),
}));

describe('LoginPage Component (Paridad 1 a 1 Jinja2 y reCAPTCHA v3)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockIsLoggingIn = false;
    mockAuthConfig = { siteKey: '', isDev: false };
    delete (window as any).grecaptcha;
  });

  it('renderiza correctamente el formulario de login, inputs y botón de acceso', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /Vino Nuevo/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ingresa tu usuario/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/••••••••/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Ingresar al Sistema/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cambiar tema de color/i })).toBeInTheDocument();
  });

  it('permite alternar la visibilidad de la contraseña con el botón toggle', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const passInput = screen.getByPlaceholderText(/••••••••/i) as HTMLInputElement;
    const toggleBtn = screen.getByRole('button', { name: /Mostrar contraseña/i });

    expect(passInput.type).toBe('password');

    fireEvent.click(toggleBtn);
    expect(passInput.type).toBe('text');

    fireEvent.click(toggleBtn);
    expect(passInput.type).toBe('password');
  });

  it('rechaza el envío y muestra mensaje de validación si los campos están vacíos', async () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const submitBtn = screen.getByRole('button', { name: /Ingresar al Sistema/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('Por favor completa todos los campos.')).toBeInTheDocument();
    });
    expect(mockLoginFn).not.toHaveBeenCalled();
  });

  it('renderiza condicionalmente el banner de entorno de desarrollo cuando isDev es true', () => {
    mockAuthConfig = { siteKey: '', isDev: true };

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('dev-banner')).toBeInTheDocument();
    expect(screen.getByText(/Entorno de Desarrollo/i)).toBeInTheDocument();
    expect(screen.getByText(/admin/i)).toBeInTheDocument();
    expect(screen.getByText(/supervisor/i)).toBeInTheDocument();
    expect(screen.getByText(/lider/i)).toBeInTheDocument();
  });

  it('no muestra el banner de desarrollo cuando isDev es false', () => {
    mockAuthConfig = { siteKey: '', isDev: false };

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(screen.queryByTestId('dev-banner')).not.toBeInTheDocument();
  });

  it('detecta bloqueo de reCAPTCHA (adblocker/red) si hay siteKey pero grecaptcha no está disponible', async () => {
    mockAuthConfig = { siteKey: 'dummy-site-key-123', isDev: false };

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const userInput = screen.getByPlaceholderText(/Ingresa tu usuario/i);
    const passInput = screen.getByPlaceholderText(/••••••••/i);
    const submitBtn = screen.getByRole('button', { name: /Ingresar al Sistema/i });

    fireEvent.change(userInput, { target: { value: 'admin' } });
    fireEvent.change(passInput, { target: { value: 'secret' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/No se pudo cargar la verificación de seguridad \(reCAPTCHA\)/i)
      ).toBeInTheDocument();
    });
    expect(mockLoginFn).not.toHaveBeenCalled();
  });

  it('ejecuta reCAPTCHA correctamente cuando grecaptcha está presente y envía token', async () => {
    mockAuthConfig = { siteKey: 'dummy-site-key-123', isDev: false };

    // Simulamos la API grecaptcha de Google
    (window as any).grecaptcha = {
      ready: (cb: () => void) => cb(),
      execute: vi.fn().mockResolvedValue('token-google-recaptcha-valido'),
    };

    mockLoginFn.mockResolvedValueOnce({
      success: true,
      user: { id: '1', username: 'admin', rol: 'admin', nombre: 'Admin' },
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const userInput = screen.getByPlaceholderText(/Ingresa tu usuario/i);
    const passInput = screen.getByPlaceholderText(/••••••••/i);
    const submitBtn = screen.getByRole('button', { name: /Ingresar al Sistema/i });

    fireEvent.change(userInput, { target: { value: 'admin' } });
    fireEvent.change(passInput, { target: { value: 'password123' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect((window as any).grecaptcha.execute).toHaveBeenCalledWith('dummy-site-key-123', {
        action: 'login',
      });
      expect(mockLoginFn).toHaveBeenCalledWith({
        username: 'admin',
        password: 'password123',
        recaptcha_token: 'token-google-recaptcha-valido',
        'g-recaptcha-response': 'token-google-recaptcha-valido',
      });
      expect(mockSuccess).toHaveBeenCalledWith('Bienvenido, Admin');
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
    });
  });

  it('mapea el error HTTP 429 a mensaje amigable de límite de tasa', async () => {
    mockLoginFn.mockRejectedValueOnce(
      new ApiError(429, 'Too Many Requests', { error: 'Rate limit exceeded' })
    );

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const userInput = screen.getByPlaceholderText(/Ingresa tu usuario/i);
    const passInput = screen.getByPlaceholderText(/••••••••/i);
    const submitBtn = screen.getByRole('button', { name: /Ingresar al Sistema/i });

    fireEvent.change(userInput, { target: { value: 'admin' } });
    fireEvent.change(passInput, { target: { value: 'password123' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(
        screen.getByText('Demasiados intentos. Por favor espera un minuto antes de reintentar.')
      ).toBeInTheDocument();
    });
  });

  it('oculta la insignia de reCAPTCHA (.grecaptcha-badge) al desmontar LoginPage para no invadir otras vistas', () => {
    mockAuthConfig = { siteKey: 'dummy-site-key-123', isDev: false };

    const dummyBadge = document.createElement('div');
    dummyBadge.className = 'grecaptcha-badge';
    document.body.appendChild(dummyBadge);

    const { unmount } = render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(dummyBadge.style.visibility).toBe('visible');

    // Al navegar a otra ruta, LoginPage se desmonta
    unmount();

    expect(dummyBadge.style.visibility).toBe('hidden');
    expect(dummyBadge.style.opacity).toBe('0');

    dummyBadge.remove();
  });
});
