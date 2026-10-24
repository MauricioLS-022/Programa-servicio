import { useEffect } from 'react';
import { useAuth } from './useAuth';
import type { UserRole } from '../types/auth';

export interface UseDocumentTitleOptions {
  /** Si es true, usa el título tal cual sin anteponer la convención institucional y de rol */
  override?: boolean;
}

/**
 * Obtiene el descriptor ministerial del rol según la plantilla original Jinja2 (admin_layout.html):
 * admin -> "Panel Administrativo"
 * supervisor -> "Supervisión Regional"
 * lider_cdp (o cualquier otro) -> "Casa de Paz"
 */
export function getRoleTitlePrefix(rol?: UserRole | string): string {
  if (rol === 'admin') return 'Panel Administrativo';
  if (rol === 'supervisor') return 'Supervisión Regional';
  return 'Casa de Paz';
}

/**
 * Hook para gestionar el título dinámico del documento (document.title)
 * preservando la paridad canónica con las plantillas Jinja2 y la identidad institucional de Vino Nuevo.
 *
 * @param title Nombre de la sección o vista (ej: "Dashboard", "Reportes", "Iniciar Sesión — Vino Nuevo")
 * @param options Opciones adicionales (ej: override para títulos independientes como Login)
 */
export function useDocumentTitle(title?: string, options?: UseDocumentTitleOptions): void {
  const { user } = useAuth();

  useEffect(() => {
    if (typeof document === 'undefined') return;

    const previousTitle = document.title;

    if (options?.override) {
      if (title) {
        document.title = title;
      }
      return () => {
        document.title = previousTitle;
      };
    }

    const roleDescriptor = getRoleTitlePrefix(user?.rol);
    const cleanTitle = title?.trim().replace(/^[-—]\s*/, '');

    const newTitle = cleanTitle
      ? `Vino Nuevo - ${roleDescriptor} - ${cleanTitle}`
      : `Vino Nuevo - ${roleDescriptor}`;

    document.title = newTitle;

    return () => {
      document.title = previousTitle;
    };
  }, [title, user?.rol, options?.override]);
}
