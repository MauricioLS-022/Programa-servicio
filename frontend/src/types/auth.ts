/**
 * Tipos de datos para el módulo de Autenticación y Usuarios
 */

export type UserRole = 'admin' | 'supervisor' | 'lider_cdp' | 'cdp';

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

