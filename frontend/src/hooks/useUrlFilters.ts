import { useMemo, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';

export type FilterValue = string | number | boolean | null | undefined;
export type FilterRecord = Record<string, FilterValue>;

export interface UseUrlFiltersOptions {
  /**
   * Claves adicionales que deben eliminarse de la URL al resetear o interactuar
   * (por ejemplo, parámetros legados o IDs transitorios como cdp_id/casa_id)
   */
  cleanupKeys?: string[];
  /**
   * Si es true, la navegación crea una nueva entrada en el historial del navegador.
   * Por defecto es false (usa `{ replace: true }` para evitar ensuciar el historial en búsquedas y toggles).
   */
  pushHistory?: boolean;
}

export interface UseUrlFiltersReturn<T extends FilterRecord> {
  /** Valores actuales de los filtros derivados reactivamente de la URL */
  filters: T;
  /** Actualiza un único filtro por su clave */
  setFilter: <K extends keyof T>(key: K, value: T[K]) => void;
  /** Actualiza múltiples filtros atómicamente */
  setFilters: (updates: Partial<T>, keysToRemove?: string[]) => void;
  /** Restablece todos los filtros a sus valores por defecto, limpiando la URL */
  resetFilters: () => void;
  /** Indica si todos los filtros se encuentran en sus valores por defecto (URL limpia) */
  isDefault: boolean;
  /** Instancia nativa de URLSearchParams */
  searchParams: URLSearchParams;
}

/**
 * Hook para sincronizar el estado de los filtros con la URL como única fuente de la verdad (SSOT).
 * 
 * Regla de Oro:
 * - Los valores que coincidan con su valor por defecto o estén vacíos se ELIMINAN de la URL.
 * - De este modo, la vista por defecto siempre mantiene una URL canónica y limpia
 *   (ej: `/dashboard`, `/estructura`, `/reportes` sin query params redundantes).
 */
export function useUrlFilters<T extends FilterRecord>(
  defaults: T,
  options?: UseUrlFiltersOptions
): UseUrlFiltersReturn<T> {
  const [searchParams, setSearchParams] = useSearchParams();

  // 1. Derivar valores tipados leyendo directamente desde searchParams
  const filters = useMemo(() => {
    const result = { ...defaults };

    for (const key of Object.keys(defaults) as Array<keyof T>) {
      const paramValue = searchParams.get(key as string);
      const defaultValue = defaults[key];

      if (paramValue === null || paramValue === '') {
        result[key] = defaultValue;
        continue;
      }

      // Deserialización según el tipo del valor por defecto
      if (typeof defaultValue === 'number') {
        const parsed = Number(paramValue);
        result[key] = (isNaN(parsed) ? defaultValue : parsed) as T[keyof T];
      } else if (typeof defaultValue === 'boolean') {
        result[key] = (paramValue === 'true' || paramValue === '1') as T[keyof T];
      } else {
        result[key] = paramValue as T[keyof T];
      }
    }

    return result;
  }, [searchParams, defaults]);

  // 2. Determinar si todos los filtros actuales coinciden con los valores por defecto
  const isDefault = useMemo(() => {
    for (const key of Object.keys(defaults) as Array<keyof T>) {
      const current = filters[key];
      const def = defaults[key];
      if (String(current ?? '') !== String(def ?? '')) {
        return false;
      }
    }
    return true;
  }, [filters, defaults]);

  // 3. Mutación de múltiples filtros con limpieza estricta de defaults y vacíos
  const setFilters = useCallback(
    (updates: Partial<T>, keysToRemove?: string[]) => {
      const newParams = new URLSearchParams(searchParams);

      // Eliminar claves adicionales solicitadas
      if (keysToRemove && keysToRemove.length > 0) {
        for (const k of keysToRemove) {
          newParams.delete(k);
        }
      }

      // Aplicar actualizaciones
      for (const [key, value] of Object.entries(updates)) {
        const defaultValue = defaults[key as keyof T];

        const isEmpty = value === undefined || value === null || value === '';
        const isDefaultVal =
          defaultValue !== undefined &&
          String(value ?? '').trim() === String(defaultValue ?? '').trim();

        // REGLA CANÓNICA: Si es vacío o coincide con el valor por defecto, se elimina de la URL
        if (isEmpty || isDefaultVal) {
          newParams.delete(key);
        } else {
          newParams.set(key, String(value).trim());
        }
      }

      setSearchParams(newParams, { replace: !options?.pushHistory });
    },
    [searchParams, setSearchParams, defaults, options?.pushHistory]
  );

  // 4. Mutación de un filtro individual
  const setFilter = useCallback(
    <K extends keyof T>(key: K, value: T[K]) => {
      setFilters({ [key]: value } as unknown as Partial<T>);
    },
    [setFilters]
  );

  // 5. Restablecimiento completo de filtros a valores por defecto (limpieza de URL)
  const resetFilters = useCallback(() => {
    const newParams = new URLSearchParams(searchParams);

    for (const key of Object.keys(defaults)) {
      newParams.delete(key);
    }

    if (options?.cleanupKeys) {
      for (const k of options.cleanupKeys) {
        newParams.delete(k);
      }
    }

    setSearchParams(newParams, { replace: !options?.pushHistory });
  }, [searchParams, setSearchParams, defaults, options?.cleanupKeys, options?.pushHistory]);

  return {
    filters,
    setFilter,
    setFilters,
    resetFilters,
    isDefault,
    searchParams,
  };
}
