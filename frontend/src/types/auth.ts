/**
 * Tipos de datos para el módulo de Autenticación y Usuarios
 */

export type UserRole = 'admin' | 'supervisor' | 'lider_cdp';

export interface User {
  id: string;
  username: string;
  rol: UserRole;
  nombre: string;
  apellido: string;
  is_active?: boolean;
}

export interface LoginCredentials {
  username?: string;
  usuario?: string;
  password?: string;
  contrasena?: string;
  recaptcha_token?: string;
  'g-recaptcha-response'?: string;
}

export interface AuthConfigResponse {
  siteKey: string;
  isDev: boolean;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  error?: string;
  message?: string;
}

export interface AuthMeResponse {
  authenticated: boolean;
  user?: User;
  error?: string;
}

